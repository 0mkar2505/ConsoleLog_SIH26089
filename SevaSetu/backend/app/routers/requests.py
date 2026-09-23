"""
Customer Service Requests API Router for Console Log platform.
Handles customer request creation, dispatch triggering, and request status retrieval.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.database import (
    get_service_requests_collection,
    get_bookings_collection,
    get_users_collection,
    get_workers_collection,
    get_customers_collection,
    get_services_collection,
)
from app.services.dispatch import assign_worker_to_request
from app.models.document_helpers import clean_doc_id

router = APIRouter(prefix="/api/requests", tags=["Requests"])


class CreateRequestInput(BaseModel):
    customer_id: Optional[str] = None
    service_id: str
    problem_description: str
    address: str
    landmark: Optional[str] = None
    directions: Optional[str] = None
    request_type: str = "immediate"  # "immediate" or "scheduled"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    preferred_date: Optional[str] = None
    preferred_start_time: Optional[datetime] = None


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_service_request(payload: CreateRequestInput):
    """
    Create a new customer service request in MongoDB Atlas,
    run simple dispatch engine to assign nearest verified worker,
    and return the created request and booking.
    """
    requests_col = get_service_requests_collection()
    customers_col = get_customers_collection()

    now = datetime.utcnow()

    # Fallback default customer_id if not supplied
    cust_id = payload.customer_id
    if not cust_id:
        first_cust = customers_col.find_one({})
        cust_id = str(first_cust["_id"]) if first_cust else "cust_default_01"

    # GeoJSON location if lat/lon provided
    location_geo = None
    if payload.latitude is not None and payload.longitude is not None:
        location_geo = {
            "type": "Point",
            "coordinates": [payload.longitude, payload.latitude]
        }

    # Resolve service name if possible
    services_col = get_services_collection()
    s_name = "Service"
    if payload.service_id:
        s_doc = services_col.find_one({
            "$or": [
                {"_id": ObjectId(payload.service_id) if ObjectId.is_valid(payload.service_id) else payload.service_id},
                {"name": payload.service_id}
            ]
        })
        if s_doc:
            s_name = s_doc.get("name", "Service")

    req_doc = {
        "customer_id": cust_id,
        "service_id": payload.service_id,
        "service_name": s_name,
        "problem_description": payload.problem_description,
        "request_type": payload.request_type,
        "address": payload.address,
        "landmark": payload.landmark,
        "directions": payload.directions,
        "location": location_geo,
        "preferred_date": payload.preferred_date,
        "preferred_start_time": payload.preferred_start_time,
        "flexibility": "exact",
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    }

    res = requests_col.insert_one(req_doc)
    req_doc["_id"] = res.inserted_id

    # Run Simple Dispatch Engine
    dispatch_result = assign_worker_to_request(req_doc)

    # Fetch updated request doc
    updated_req = requests_col.find_one({"_id": res.inserted_id})
    updated_req = clean_doc_id(updated_req)
    updated_req["id"] = str(res.inserted_id)

    return {
        "message": "Service request submitted and worker dispatched successfully.",
        "request": updated_req,
        "dispatch": dispatch_result
    }


@router.get("/{request_id}")
def get_service_request(request_id: str):
    """Retrieve service request details, current booking state, and assigned worker info."""
    requests_col = get_service_requests_collection()
    bookings_col = get_bookings_collection()
    workers_col = get_workers_collection()
    users_col = get_users_collection()
    services_col = get_services_collection()

    query_id = request_id
    if ObjectId.is_valid(request_id):
        query_id = ObjectId(request_id)

    req = requests_col.find_one({"$or": [{"_id": query_id}, {"_id": request_id}]})
    if not req:
        # Check if query_id is a booking_id
        booking_match = bookings_col.find_one({"$or": [{"_id": query_id}, {"_id": request_id}]})
        if booking_match and booking_match.get("request_id"):
            b_req_id = booking_match["request_id"]
            query_req_id = ObjectId(b_req_id) if ObjectId.is_valid(b_req_id) else b_req_id
            req = requests_col.find_one({"$or": [{"_id": query_req_id}, {"_id": b_req_id}]})

    if not req:
        raise HTTPException(status_code=404, detail="Service request not found")

    req_id_str = str(req["_id"])
    req = clean_doc_id(req)
    req["id"] = req_id_str

    if "service_name" not in req or not req["service_name"]:
        s_doc = services_col.find_one({
            "$or": [
                {"_id": ObjectId(req.get("service_id")) if ObjectId.is_valid(req.get("service_id")) else req.get("service_id")},
                {"name": req.get("service_id")}
            ]
        })
        req["service_name"] = s_doc.get("name", "Service") if s_doc else "Service"

    # Fetch linked booking
    booking = bookings_col.find_one({"request_id": req_id_str})
    worker_info = None

    if booking:
        booking_id_str = str(booking["_id"])
        booking = clean_doc_id(booking)
        booking["id"] = booking_id_str

        # Fetch worker user profile
        w_doc = workers_col.find_one({"_id": ObjectId(booking["worker_id"]) if ObjectId.is_valid(booking["worker_id"]) else booking["worker_id"]})
        if w_doc:
            u_doc = users_col.find_one({"_id": ObjectId(w_doc["user_id"]) if ObjectId.is_valid(w_doc["user_id"]) else w_doc["user_id"]})
            worker_info = {
                "worker_id": str(w_doc["_id"]),
                "name": u_doc.get("name", "Assigned Worker") if u_doc else "Assigned Worker",
                "phone": u_doc.get("phone", "+919844444401") if u_doc else "+919844444401",
                "rating_average": w_doc.get("rating_average", 4.8),
                "digital_access": w_doc.get("digital_access", ["smartphone"])
            }

    return {
        "request": req,
        "booking": booking,
        "worker": worker_info,
        "current_status": booking.get("status", req.get("status")) if booking else req.get("status")
    }


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def list_service_requests(customer_id: Optional[str] = None):
    """List service requests filtered optionally by customer_id."""
    requests_col = get_service_requests_collection()
    bookings_col = get_bookings_collection()

    query = {}
    if customer_id:
        query["customer_id"] = customer_id

    reqs = list(requests_col.find(query).sort("created_at", -1))
    cleaned = []
    for r in reqs:
        r_id_str = str(r["_id"])
        r = clean_doc_id(r)
        r["id"] = r_id_str

        booking = bookings_col.find_one({"request_id": r_id_str})
        if booking:
            r["booking_id"] = str(booking["_id"])
            r["job_status"] = booking.get("status")
        else:
            r["job_status"] = r.get("status")

        cleaned.append(r)
    return cleaned
