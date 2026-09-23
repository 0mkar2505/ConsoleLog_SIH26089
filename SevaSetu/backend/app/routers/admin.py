"""
Admin / Cooperative Dashboard API Router for Console Log / SevaSetu platform.
Provides aggregated analytics, workforce capacity, request lifecycle details,
worker cooperative profiles, customer profiles, and service catalog.
Reads directly from existing MongoDB Atlas collections.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId

from app.database import (
    get_service_requests_collection,
    get_bookings_collection,
    get_workers_collection,
    get_customers_collection,
    get_services_collection,
    get_cooperatives_collection,
    get_users_collection,
    get_dispatch_attempts_collection,
)
from app.models.document_helpers import clean_doc_id

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def _obj_id(val):
    if val and ObjectId.is_valid(val):
        return ObjectId(val)
    return val


@router.get("/overview")
def get_admin_overview():
    """
    Returns real statistics and workforce capacity breakdown across cooperatives:
    - Active Requests
    - Active Jobs
    - Available Workers
    - Total Workers
    - Completed Jobs
    - Pending Requests
    - Workforce capacity by service (Available vs Busy)
    """
    requests_col = get_service_requests_collection()
    bookings_col = get_bookings_collection()
    workers_col = get_workers_collection()
    services_col = get_services_collection()
    coops_col = get_cooperatives_collection()

    total_workers = workers_col.count_documents({})
    available_workers = workers_col.count_documents({"is_available": True})
    
    # Active jobs: assigned, accepted, en_route, arrived, in_progress
    active_job_statuses = ["assigned", "accepted", "en_route", "arrived", "in_progress"]
    active_jobs = bookings_col.count_documents({"status": {"$in": active_job_statuses}})
    completed_jobs = bookings_col.count_documents({"status": "completed"})

    # Pending requests
    pending_requests = requests_col.count_documents({"status": {"$in": ["pending", "open", "broadcasting"]}})
    active_requests = requests_col.count_documents({"status": {"$in": ["pending", "open", "broadcasting", "assigned", "allocated"]}})

    # Calculate workforce capacity per service
    services = list(services_col.find({"is_active": True}))
    all_workers = list(workers_col.find({}))
    
    # Build capacity map
    capacity_by_service = []
    for s in services:
        s_id_str = str(s["_id"])
        s_name = s.get("name", "Unknown")
        
        # Workers who offer this service (services array stores service ObjectIds or strings)
        matching_workers = [
            w for w in all_workers 
            if s_id_str in [str(x) for x in w.get("services", [])] or s_name in w.get("services", [])
        ]
        
        total_for_trade = len(matching_workers)
        available_for_trade = sum(1 for w in matching_workers if w.get("is_available", False) and w.get("current_workload", 0) == 0)
        busy_for_trade = total_for_trade - available_for_trade

        capacity_by_service.append({
            "service_id": s_id_str,
            "service_name": s_name,
            "category": s.get("category", "General"),
            "base_price": s.get("base_price", 0),
            "total_workers": total_for_trade,
            "available": available_for_trade,
            "busy": busy_for_trade,
        })

    # Total cooperatives count
    coop_count = coops_col.count_documents({"is_active": True})

    return {
        "stats": {
            "active_requests": active_requests,
            "active_jobs": active_jobs,
            "available_workers": available_workers,
            "total_workers": total_workers,
            "completed_jobs": completed_jobs,
            "pending_requests": pending_requests,
            "active_cooperatives": coop_count,
        },
        "capacity_by_service": capacity_by_service,
    }


@router.get("/requests")
def get_admin_requests(limit: int = 50):
    """
    Returns list of requests joined with service, customer, booking, and worker info.
    """
    requests_col = get_service_requests_collection()
    bookings_col = get_bookings_collection()
    workers_col = get_workers_collection()
    users_col = get_users_collection()
    services_col = get_services_collection()

    req_docs = list(requests_col.find({}).sort("created_at", -1).limit(limit))

    # Pre-fetch lookup caches for efficiency
    services_map = {str(s["_id"]): s.get("name") for s in services_col.find({})}
    for s in services_col.find({}):
        services_map[s.get("name")] = s.get("name")

    users_map = {str(u["_id"]): u for u in users_col.find({})}
    workers_map = {str(w["_id"]): w for w in workers_col.find({})}

    results = []
    for req in req_docs:
        req_id_str = str(req["_id"])
        
        # Link booking if exists
        booking = bookings_col.find_one({"request_id": req_id_str})
        if not booking:
            # Maybe request_id in booking was an ObjectId
            if ObjectId.is_valid(req_id_str):
                booking = bookings_col.find_one({"request_id": ObjectId(req_id_str)})

        # Customer info
        cust_name = "Customer"
        cust_phone = ""
        cust_id = req.get("customer_id")
        if cust_id:
            cust_user = users_map.get(str(cust_id))
            if not cust_user:
                cust_user = users_col.find_one({"$or": [{"_id": _obj_id(cust_id)}, {"email": cust_id}]})
            if cust_user:
                cust_name = cust_user.get("name", "Customer")
                cust_phone = cust_user.get("phone", "")

        # Worker info
        worker_name = "Unassigned"
        worker_phone = ""
        worker_id_str = ""
        worker_digital_access = []

        if booking and booking.get("worker_id"):
            worker_id_str = str(booking.get("worker_id"))
            w_doc = workers_map.get(worker_id_str)
            if not w_doc:
                w_doc = workers_col.find_one({"_id": _obj_id(worker_id_str)})
            if w_doc:
                w_u = users_map.get(str(w_doc.get("user_id")))
                if not w_u:
                    w_u = users_col.find_one({"_id": _obj_id(w_doc.get("user_id"))})
                if w_u:
                    worker_name = w_u.get("name", "Assigned Worker")
                    worker_phone = w_u.get("phone", "")
                worker_digital_access = w_doc.get("digital_access", ["smartphone"])

        # Determine effective status
        effective_status = booking.get("status") if booking else req.get("status", "pending")

        # Resolve service name
        s_id = req.get("service_id")
        service_name = req.get("service_name") or services_map.get(str(s_id), s_id or "General Service")

        created_at_val = req.get("created_at")
        if isinstance(created_at_val, datetime):
            created_at_str = created_at_val.isoformat()
        else:
            created_at_str = str(created_at_val) if created_at_val else ""

        results.append({
            "request_id": req_id_str,
            "booking_id": str(booking["_id"]) if booking else None,
            "service": service_name,
            "service_id": str(s_id) if s_id else "",
            "customer_name": cust_name,
            "customer_phone": cust_phone,
            "customer_id": str(cust_id) if cust_id else "",
            "worker_name": worker_name,
            "worker_id": worker_id_str,
            "worker_phone": worker_phone,
            "worker_digital_access": worker_digital_access,
            "status": effective_status,
            "request_type": req.get("request_type", "immediate"),
            "problem_description": req.get("problem_description", ""),
            "address": req.get("address", ""),
            "landmark": req.get("landmark", ""),
            "directions": req.get("directions", ""),
            "created_at": created_at_str,
            "preferred_date": req.get("preferred_date"),
            "estimated_price": booking.get("estimated_price") if booking else None,
        })

    return results


@router.get("/requests/{request_id}")
def get_admin_request_detail(request_id: str):
    """
    Returns single request full detail including dispatch history and booking status.
    """
    requests_col = get_service_requests_collection()
    bookings_col = get_bookings_collection()
    workers_col = get_workers_collection()
    users_col = get_users_collection()
    services_col = get_services_collection()
    dispatch_col = get_dispatch_attempts_collection()

    req = requests_col.find_one({"$or": [{"_id": _obj_id(request_id)}, {"_id": request_id}]})
    if not req:
        # Check if booking
        b = bookings_col.find_one({"$or": [{"_id": _obj_id(request_id)}, {"_id": request_id}]})
        if b and b.get("request_id"):
            req = requests_col.find_one({"$or": [{"_id": _obj_id(b["request_id"])}, {"_id": b["request_id"]}]})

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req_id_str = str(req["_id"])
    cleaned_req = clean_doc_id(req)
    cleaned_req["id"] = req_id_str

    # Booking
    booking = bookings_col.find_one({"$or": [{"request_id": req_id_str}, {"request_id": _obj_id(req_id_str)}]})
    cleaned_booking = None
    worker_info = None

    if booking:
        cleaned_booking = clean_doc_id(booking)
        cleaned_booking["id"] = str(booking["_id"])

        w_id = booking.get("worker_id")
        if w_id:
            w_doc = workers_col.find_one({"_id": _obj_id(w_id)})
            if w_doc:
                u_doc = users_col.find_one({"_id": _obj_id(w_doc.get("user_id"))})
                worker_info = {
                    "id": str(w_doc["_id"]),
                    "name": u_doc.get("name", "Worker") if u_doc else "Worker",
                    "phone": u_doc.get("phone", "") if u_doc else "",
                    "rating": w_doc.get("rating_average", 4.8),
                    "digital_access": w_doc.get("digital_access", ["smartphone"]),
                    "completed_jobs": w_doc.get("completed_jobs", 0),
                }

    # Dispatch attempts
    dispatches = list(dispatch_col.find({"$or": [{"request_id": req_id_str}, {"request_id": _obj_id(req_id_str)}]}))
    cleaned_dispatches = []
    for d in dispatches:
        d_cleaned = clean_doc_id(d)
        d_cleaned["id"] = str(d["_id"])
        cleaned_dispatches.append(d_cleaned)

    # Service info
    s_doc = services_col.find_one({"$or": [{"_id": _obj_id(req.get("service_id"))}, {"name": req.get("service_id")}]})
    service_info = {
        "name": s_doc.get("name", "Service") if s_doc else req.get("service_name", "Service"),
        "category": s_doc.get("category", "General") if s_doc else "General",
        "base_price": s_doc.get("base_price", 350.0) if s_doc else 350.0,
    }

    return {
        "request": cleaned_req,
        "booking": cleaned_booking,
        "worker": worker_info,
        "service": service_info,
        "dispatch_attempts": cleaned_dispatches,
        "current_status": cleaned_booking.get("status") if cleaned_booking else cleaned_req.get("status", "pending"),
    }


@router.get("/workers")
def get_admin_workers():
    """
    Returns list of workers with cooperative, services, digital access channels,
    availability, current workload, rating, and completed jobs.
    """
    workers_col = get_workers_collection()
    users_col = get_users_collection()
    coops_col = get_cooperatives_collection()
    services_col = get_services_collection()
    bookings_col = get_bookings_collection()

    workers = list(workers_col.find({}))
    users_map = {str(u["_id"]): u for u in users_col.find({})}
    coops_map = {str(c["_id"]): c.get("name", "Independent Cooperative") for c in coops_col.find({})}
    services_map = {str(s["_id"]): s.get("name", "Service") for s in services_col.find({})}

    active_statuses = ["assigned", "accepted", "en_route", "arrived", "in_progress"]

    result = []
    for w in workers:
        w_id_str = str(w["_id"])
        u_id = str(w.get("user_id"))
        user = users_map.get(u_id)

        # Resolve cooperative name
        coop_id = str(w.get("cooperative_id"))
        coop_name = coops_map.get(coop_id, "Dadar Workers Cooperative")

        # Resolve service names
        worker_services = []
        for s_ref in w.get("services", []):
            s_name = services_map.get(str(s_ref), str(s_ref))
            worker_services.append(s_name)

        # Check for active job
        active_booking = bookings_col.find_one({
            "worker_id": {"$in": [w_id_str, _obj_id(w_id_str)]},
            "status": {"$in": active_statuses}
        })
        current_job_info = None
        if active_booking:
            current_job_info = {
                "booking_id": str(active_booking["_id"]),
                "status": active_booking.get("status"),
                "address": active_booking.get("address", ""),
            }

        result.append({
            "id": w_id_str,
            "name": user.get("name", "Worker") if user else "Worker",
            "phone": user.get("phone", "") if user else "",
            "email": user.get("email", "") if user else "",
            "cooperative_name": coop_name,
            "skills": worker_services,
            "is_verified": w.get("is_verified", False),
            "is_available": w.get("is_available", False),
            "digital_access": w.get("digital_access", ["smartphone"]),
            "rating": w.get("rating_average", 4.5),
            "completed_jobs": w.get("completed_jobs", 0),
            "current_workload": w.get("current_workload", 0),
            "service_area": w.get("service_area", "Mumbai Metro"),
            "current_job": current_job_info,
        })

    return result


@router.get("/customers")
def get_admin_customers():
    """
    Returns list of customers, their total requests, recent request, and address details.
    """
    customers_col = get_customers_collection()
    users_col = get_users_collection()
    requests_col = get_service_requests_collection()

    customers = list(customers_col.find({}))
    users_map = {str(u["_id"]): u for u in users_col.find({})}

    result = []
    for c in customers:
        c_id_str = str(c["_id"])
        u_id = str(c.get("user_id"))
        user = users_map.get(u_id)

        # Count customer requests
        req_count = requests_col.count_documents({
            "$or": [
                {"customer_id": c_id_str},
                {"customer_id": u_id}
            ]
        })

        recent_req = requests_col.find_one(
            {"$or": [{"customer_id": c_id_str}, {"customer_id": u_id}]},
            sort=[("created_at", -1)]
        )

        recent_info = None
        if recent_req:
            created_at_val = recent_req.get("created_at")
            recent_info = {
                "request_id": str(recent_req["_id"]),
                "service": recent_req.get("service_name", "Service"),
                "status": recent_req.get("status", "pending"),
                "created_at": created_at_val.isoformat() if isinstance(created_at_val, datetime) else str(created_at_val),
            }

        saved_addresses = c.get("saved_addresses", [])
        primary_address = saved_addresses[0]["address"] if saved_addresses else "No address on file"

        result.append({
            "id": c_id_str,
            "name": user.get("name", "Customer") if user else "Customer",
            "phone": user.get("phone", "") if user else "",
            "email": user.get("email", "") if user else "",
            "requests_count": req_count,
            "recent_request": recent_info,
            "saved_addresses": saved_addresses,
            "primary_address": primary_address,
        })

    return result


@router.get("/services")
def get_admin_services():
    """
    Returns service catalogue with active worker counts and trade details.
    """
    services_col = get_services_collection()
    workers_col = get_workers_collection()

    services = list(services_col.find({}).sort("name", 1))
    all_workers = list(workers_col.find({}))

    result = []
    for s in services:
        s_id_str = str(s["_id"])
        s_name = s.get("name", "Unknown")

        # Worker count for this service
        worker_count = sum(
            1 for w in all_workers
            if s_id_str in [str(x) for x in w.get("services", [])] or s_name in w.get("services", [])
        )
        available_count = sum(
            1 for w in all_workers
            if (s_id_str in [str(x) for x in w.get("services", [])] or s_name in w.get("services", []))
            and w.get("is_available", False) and w.get("current_workload", 0) == 0
        )

        result.append({
            "id": s_id_str,
            "name": s_name,
            "description": s.get("description", ""),
            "base_price": s.get("base_price", 0.0),
            "category": s.get("category", "General"),
            "is_active": s.get("is_active", True),
            "total_workers": worker_count,
            "available_workers": available_count,
        })

    return result
