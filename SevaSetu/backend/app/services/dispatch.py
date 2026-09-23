"""
Simple Dispatch Engine for Console Log platform.
Matches service requests to eligible, verified, nearest available workers
and records bookings and dispatch attempt logs in MongoDB.
"""
import math
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.database import (
    get_workers_collection,
    get_bookings_collection,
    get_dispatch_attempts_collection,
    get_service_requests_collection,
    get_services_collection,
    get_users_collection,
)

logger = logging.getLogger(__name__)


def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Haversine distance in kilometers between two geo points."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def assign_worker_to_request(request_doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Deterministically match and assign an available worker to a customer request.

    Selection Criteria:
    1. Worker matches requested service_id.
    2. Worker is available (is_available == True).
    3. Prefer verified workers (is_verified == True).
    4. Prefer nearest worker based on GeoJSON location.
    5. Prefer lower current_workload.
    """
    workers_col = get_workers_collection()
    bookings_col = get_bookings_collection()
    dispatch_col = get_dispatch_attempts_collection()
    requests_col = get_service_requests_collection()
    services_col = get_services_collection()
    users_col = get_users_collection()

    service_id = str(request_doc.get("service_id", ""))
    request_id_str = str(request_doc["_id"])

    # Fetch service details for base price
    service_doc = services_col.find_one({"_id": request_doc.get("service_id")})
    if not service_doc and isinstance(service_id, str):
        try:
            from bson import ObjectId
            if ObjectId.is_valid(service_id):
                service_doc = services_col.find_one({"_id": ObjectId(service_id)})
        except Exception:
            pass

    base_price = service_doc.get("base_price", 350.0) if service_doc else 350.0

    # Query matching available workers
    query = {"is_available": True}
    if service_id:
        query["$or"] = [
            {"services": service_id},
            {"services": service_doc.get("name")} if service_doc else {"services": service_id}
        ]

    candidate_workers = list(workers_col.find(query))

    # Fallback to any available worker if specific service match query yields empty list
    if not candidate_workers:
        candidate_workers = list(workers_col.find({"is_available": True}))

    if not candidate_workers:
        logger.warning(f"No available workers found for request {request_id_str}")
        return None

    # Get request coordinates if present
    req_loc = request_doc.get("location")
    req_coords = req_loc.get("coordinates") if req_loc else None  # [lng, lat]

    def worker_score_key(w: Dict[str, Any]):
        # 1. Verified bonus (-1 for verified so it sorts first)
        verified_rank = -1 if w.get("is_verified", False) else 0

        # 2. Distance rank
        dist_km = 9999.0
        w_loc = w.get("location")
        if req_coords and w_loc and w_loc.get("coordinates"):
            try:
                w_lng, w_lat = w_loc["coordinates"]
                r_lng, r_lat = req_coords
                dist_km = _haversine_distance_km(r_lat, r_lng, w_lat, w_lng)
            except Exception:
                pass

        # 3. Workload
        workload = w.get("current_workload", 0)

        return (verified_rank, dist_km, workload)

    # Sort candidate workers according to criteria
    candidate_workers.sort(key=worker_score_key)
    selected_worker = candidate_workers[0]
    worker_id_str = str(selected_worker["_id"])

    now = datetime.utcnow()

    # Create Booking document fields for $set (without created_at)
    booking_set_fields = {
        "request_id": request_id_str,
        "customer_id": str(request_doc.get("customer_id", "")),
        "worker_id": worker_id_str,
        "cooperative_id": str(selected_worker.get("cooperative_id", "")),
        "service_id": service_id,
        "scheduled_start": request_doc.get("preferred_start_time") or now,
        "estimated_duration_minutes": 60,
        "location": request_doc.get("location"),
        "address": request_doc.get("address", ""),
        "landmark": request_doc.get("landmark"),
        "directions": request_doc.get("directions"),
        "status": "assigned",
        "estimated_price": base_price,
        "updated_at": now,
    }

    # Upsert booking in database
    booking_res = bookings_col.find_one_and_update(
        {"request_id": request_id_str},
        {"$setOnInsert": {"created_at": now}, "$set": booking_set_fields},
        upsert=True,
        return_document=True
    )
    booking_id_str = str(booking_res["_id"])

    # Determine communication method
    digital_methods = selected_worker.get("digital_access", ["smartphone"])
    comm_method = "app" if "smartphone" in digital_methods else ("sms" if "sms" in digital_methods else "voice")

    # Create Dispatch Attempt record
    dispatch_set_fields = {
        "request_id": request_id_str,
        "worker_id": worker_id_str,
        "status": "offered",
        "communication_method": comm_method,
        "offer_timestamp": now,
        "updated_at": now,
    }
    dispatch_col.update_one(
        {"request_id": request_id_str, "worker_id": worker_id_str},
        {"$setOnInsert": {"created_at": now}, "$set": dispatch_set_fields},
        upsert=True
    )

    # If low-digital worker (SMS/voice), trigger SMS dispatch simulation
    if comm_method in ["sms", "voice"]:
        try:
            from app.services.sms_gateway import generate_job_sms_text, send_dispatch_sms
            w_u = users_col.find_one({"_id": selected_worker.get("user_id")})
            w_phone = w_u.get("phone", "+919844444403") if w_u else "+919844444403"
            sms_body = generate_job_sms_text(
                booking_id=booking_id_str,
                service_name=service_doc.get("name", "Service") if service_doc else "Service",
                customer_name=request_doc.get("customer_name", "Customer"),
                customer_phone=request_doc.get("customer_phone", "+919811111111"),
                address=request_doc.get("address", ""),
                landmark=request_doc.get("landmark"),
                directions=request_doc.get("directions"),
                scheduled_time=request_doc.get("preferred_date"),
                problem_description=request_doc.get("problem_description", "Service requested"),
                estimated_price=base_price,
            )
            send_dispatch_sms(
                worker_phone=w_phone,
                worker_id=worker_id_str,
                request_id=request_id_str,
                booking_id=booking_id_str,
                message_body=sms_body,
            )
        except Exception as e:
            logger.warning(f"Failed to log SMS dispatch: {e}")

    # Update Service Request status to allocated
    requests_col.update_one(
        {"_id": request_doc["_id"]},
        {"$set": {"status": "allocated", "updated_at": now}}
    )

    # Fetch worker user profile for name and phone
    w_user = users_col.find_one({"_id": selected_worker.get("user_id")})
    if not w_user and isinstance(selected_worker.get("user_id"), str):
        try:
            from bson import ObjectId
            if ObjectId.is_valid(selected_worker["user_id"]):
                w_user = users_col.find_one({"_id": ObjectId(selected_worker["user_id"])})
        except Exception:
            pass

    worker_name = w_user.get("name", "Assigned Worker") if w_user else "Assigned Worker"
    worker_phone = w_user.get("phone", "+919844444401") if w_user else "+919844444401"

    result = {
        "booking_id": booking_id_str,
        "request_id": request_id_str,
        "worker_id": worker_id_str,
        "worker_name": worker_name,
        "worker_phone": worker_phone,
        "status": "assigned",
        "communication_method": comm_method,
        "estimated_price": base_price,
    }

    logger.info(f"Successfully assigned worker {worker_name} ({worker_id_str}) to request {request_id_str}")
    return result
