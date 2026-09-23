"""
Worker API Router for Console Log platform.
Handles worker job retrieval, job acceptance, and status updates (en_route, in_progress, completed).
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.database import (
    get_bookings_collection,
    get_dispatch_attempts_collection,
    get_service_requests_collection,
    get_services_collection,
    get_users_collection,
    get_workers_collection,
    get_customers_collection,
)
from app.models.document_helpers import clean_doc_id

router = APIRouter(prefix="/api/worker", tags=["Worker"])


class StatusUpdateInput(BaseModel):
    status: str  # "en_route", "arrived", "in_progress", "completed", "cancelled"
    notes: Optional[str] = None


@router.get("/jobs")
def get_worker_jobs(worker_id: Optional[str] = None):
    """
    Retrieve assigned/active jobs for a worker.
    If worker_id is omitted, defaults to first active worker in database.
    """
    bookings_col = get_bookings_collection()
    workers_col = get_workers_collection()
    requests_col = get_service_requests_collection()
    services_col = get_services_collection()
    users_col = get_users_collection()
    customers_col = get_customers_collection()

    target_worker_id = worker_id
    if not target_worker_id:
        first_worker = workers_col.find_one({})
        if first_worker:
            target_worker_id = str(first_worker["_id"])

    if not target_worker_id:
        return []

    # Query bookings matching worker_id
    query_w_id = target_worker_id
    if ObjectId.is_valid(target_worker_id):
        query_w_id = ObjectId(target_worker_id)

    bookings = list(bookings_col.find({
        "$or": [{"worker_id": target_worker_id}, {"worker_id": str(query_w_id)}]
    }).sort("created_at", -1))

    jobs = []
    for b in bookings:
        b_id_str = str(b["_id"])
        b = clean_doc_id(b)
        b["id"] = b_id_str

        # Fetch service name
        s_name = "Service"
        if b.get("service_id"):
            s_doc = services_col.find_one({
                "$or": [
                    {"_id": ObjectId(b["service_id"]) if ObjectId.is_valid(b["service_id"]) else b["service_id"]},
                    {"name": b["service_id"]}
                ]
            })
            if s_doc:
                s_name = s_doc.get("name", "Service")

        # Fetch customer details
        c_name = "Customer"
        c_phone = "+919811111111"
        if b.get("customer_id"):
            c_u = users_col.find_one({
                "$or": [
                    {"_id": ObjectId(b["customer_id"]) if ObjectId.is_valid(b["customer_id"]) else b["customer_id"]},
                    {"email": b["customer_id"]}
                ]
            })
            if c_u:
                c_name = c_u.get("name", "Customer")
                c_phone = c_u.get("phone", "+919811111111")

        # Fetch problem description from request
        prob_desc = "Customer requested service"
        req_type = "immediate"
        if b.get("request_id"):
            req_doc = requests_col.find_one({
                "$or": [
                    {"_id": ObjectId(b["request_id"]) if ObjectId.is_valid(b["request_id"]) else b["request_id"]}
                ]
            })
            if req_doc:
                prob_desc = req_doc.get("problem_description", prob_desc)
                req_type = req_doc.get("request_type", "immediate")

        job_entry = {
            "booking_id": b_id_str,
            "request_id": b.get("request_id"),
            "service_name": s_name,
            "customer_name": c_name,
            "customer_phone": c_phone,
            "problem_description": prob_desc,
            "request_type": req_type,
            "address": b.get("address", ""),
            "landmark": b.get("landmark"),
            "directions": b.get("directions"),
            "status": b.get("status", "assigned"),
            "estimated_price": b.get("estimated_price", 350.0),
            "created_at": b.get("created_at")
        }
        jobs.append(job_entry)

    return jobs


@router.get("/jobs/{booking_id}")
def get_job_details(booking_id: str):
    """Retrieve details for a specific job/booking."""
    bookings_col = get_bookings_collection()
    requests_col = get_service_requests_collection()
    services_col = get_services_collection()
    users_col = get_users_collection()

    query_id = ObjectId(booking_id) if ObjectId.is_valid(booking_id) else booking_id
    booking = bookings_col.find_one({"$or": [{"_id": query_id}, {"_id": booking_id}]})
    if not booking:
        raise HTTPException(status_code=404, detail="Job/Booking not found")

    b_id_str = str(booking["_id"])

    # Fetch service name
    s_name = "Service"
    if booking.get("service_id"):
        s_doc = services_col.find_one({
            "$or": [
                {"_id": ObjectId(booking["service_id"]) if ObjectId.is_valid(booking["service_id"]) else booking["service_id"]},
                {"name": booking["service_id"]}
            ]
        })
        if s_doc:
            s_name = s_doc.get("name", "Service")

    # Fetch customer details
    c_name = "Customer"
    c_phone = "+919811111111"
    if booking.get("customer_id"):
        c_u = users_col.find_one({
            "$or": [
                {"_id": ObjectId(booking["customer_id"]) if ObjectId.is_valid(booking["customer_id"]) else booking["customer_id"]},
                {"email": booking["customer_id"]}
            ]
        })
        if c_u:
            c_name = c_u.get("name", "Customer")
            c_phone = c_u.get("phone", "+919811111111")

    # Fetch problem description from request
    prob_desc = "Customer requested service"
    req_type = "immediate"
    if booking.get("request_id"):
        req_doc = requests_col.find_one({
            "$or": [
                {"_id": ObjectId(booking["request_id"]) if ObjectId.is_valid(booking["request_id"]) else booking["request_id"]}
            ]
        })
        if req_doc:
            prob_desc = req_doc.get("problem_description", prob_desc)
            req_type = req_doc.get("request_type", "immediate")

    return {
        "booking_id": b_id_str,
        "request_id": booking.get("request_id"),
        "worker_id": booking.get("worker_id"),
        "service_name": s_name,
        "customer_name": c_name,
        "customer_phone": c_phone,
        "problem_description": prob_desc,
        "request_type": req_type,
        "address": booking.get("address", ""),
        "landmark": booking.get("landmark"),
        "directions": booking.get("directions"),
        "status": booking.get("status", "assigned"),
        "estimated_price": booking.get("estimated_price", 350.0),
        "created_at": booking.get("created_at")
    }


@router.post("/jobs/{booking_id}/accept")
def accept_job(booking_id: str):
    """Worker accepts an assigned job."""
    bookings_col = get_bookings_collection()
    dispatch_col = get_dispatch_attempts_collection()
    requests_col = get_service_requests_collection()

    query_id = ObjectId(booking_id) if ObjectId.is_valid(booking_id) else booking_id
    booking = bookings_col.find_one({"$or": [{"_id": query_id}, {"_id": booking_id}]})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    now = datetime.utcnow()

    # Update booking status to accepted
    bookings_col.update_one(
        {"_id": booking["_id"]},
        {"$set": {"status": "accepted", "updated_at": now}}
    )

    req_id = booking.get("request_id")
    if req_id:
        requests_col.update_one(
            {"$or": [{"_id": ObjectId(req_id) if ObjectId.is_valid(req_id) else req_id}]},
            {"$set": {"status": "allocated", "updated_at": now}}
        )
        dispatch_col.update_one(
            {"request_id": str(req_id), "worker_id": str(booking.get("worker_id"))},
            {"$set": {"status": "accepted", "response_timestamp": now, "updated_at": now}}
        )

    return {
        "message": "Job accepted successfully.",
        "booking_id": str(booking["_id"]),
        "status": "accepted"
    }


@router.post("/jobs/{booking_id}/status")
def update_job_status(booking_id: str, payload: StatusUpdateInput):
    """Update job workflow status (en_route, arrived, in_progress, completed, cancelled)."""
    bookings_col = get_bookings_collection()
    requests_col = get_service_requests_collection()
    workers_col = get_workers_collection()

    query_id = ObjectId(booking_id) if ObjectId.is_valid(booking_id) else booking_id
    booking = bookings_col.find_one({"$or": [{"_id": query_id}, {"_id": booking_id}]})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    valid_statuses = ["assigned", "accepted", "en_route", "arrived", "in_progress", "completed", "cancelled"]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{payload.status}'. Valid: {valid_statuses}")

    now = datetime.utcnow()
    update_data = {
        "status": payload.status,
        "updated_at": now
    }

    if payload.status == "completed":
        update_data["completed_at"] = now

    bookings_col.update_one(
        {"_id": booking["_id"]},
        {"$set": update_data}
    )

    # Sync request status
    req_id = booking.get("request_id")
    if req_id:
        req_status = "fulfilled" if payload.status == "completed" else payload.status
        requests_col.update_one(
            {"$or": [{"_id": ObjectId(req_id) if ObjectId.is_valid(req_id) else req_id}]},
            {"$set": {"status": req_status, "updated_at": now}}
        )

    # Update worker metrics when job is completed
    if payload.status == "completed" and booking.get("worker_id"):
        w_id = booking["worker_id"]
        w_obj = ObjectId(w_id) if ObjectId.is_valid(w_id) else w_id
        workers_col.update_one(
            {"$or": [{"_id": w_obj}]},
            {"$inc": {"completed_jobs": 1}, "$set": {"current_workload": 0}}
        )

    return {
        "message": f"Job status updated to '{payload.status}'.",
        "booking_id": str(booking["_id"]),
        "status": payload.status
    }
