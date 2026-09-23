"""
Dispatch operations, SMS gateway simulation, and scheduling management router.
Enables simulating low-digital worker incoming SMS replies (1=ACCEPT, 2=REJECT)
and inspecting communication audit logs.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.database import (
    get_communication_logs_collection,
    get_bookings_collection,
    get_service_requests_collection,
    get_dispatch_attempts_collection,
    get_workers_collection,
    get_users_collection,
)
from app.services.sms_gateway import handle_inbound_worker_sms
from app.models.document_helpers import clean_doc_id

router = APIRouter(prefix="/api/dispatch-ops", tags=["Dispatch Operations"])


class InboundSmsPayload(BaseModel):
    sender_phone: str
    message: str  # e.g., "1" or "2" or "ACCEPT" or "REJECT"


class ManualReassignPayload(BaseModel):
    request_id: str
    worker_id: str


@router.post("/sms/inbound")
def simulate_inbound_sms(payload: InboundSmsPayload):
    """
    Simulates receiving an SMS reply from a low-digital worker.
    Processes keypad reply ('1' to accept, '2' to reject).
    """
    result = handle_inbound_worker_sms(payload.sender_phone, payload.message)
    return result


@router.get("/sms/logs")
def get_communication_logs(limit: int = 50):
    """
    Retrieve SMS and voice dispatch communication logs for low-digital workers.
    """
    comm_col = get_communication_logs_collection()
    users_col = get_users_collection()
    workers_col = get_workers_collection()

    logs = list(comm_col.find({}).sort("timestamp", -1).limit(limit))

    # Preload user map
    workers_map = {str(w["_id"]): w for w in workers_col.find({})}
    users_map = {str(u["_id"]): u for u in users_col.find({})}

    result = []
    for l in logs:
        l_id = str(l["_id"])
        cleaned = clean_doc_id(l)
        cleaned["id"] = l_id

        # Worker name resolution
        w_name = "Worker"
        w_id = l.get("worker_id")
        if w_id and str(w_id) in workers_map:
            w_doc = workers_map[str(w_id)]
            u_doc = users_map.get(str(w_doc.get("user_id")))
            if u_doc:
                w_name = u_doc.get("name", "Worker")

        cleaned["worker_name"] = w_name
        time_val = l.get("timestamp") or l.get("created_at")
        cleaned["formatted_time"] = time_val.isoformat() if isinstance(time_val, datetime) else str(time_val)

        result.append(cleaned)

    return result


@router.post("/reassign")
def reassign_job(payload: ManualReassignPayload):
    """
    Manually reassign a request/job to a specific worker.
    """
    bookings_col = get_bookings_collection()
    requests_col = get_service_requests_collection()
    workers_col = get_workers_collection()
    dispatch_col = get_dispatch_attempts_collection()

    req_id = payload.request_id
    worker_id = payload.worker_id

    worker_doc = workers_col.find_one({"$or": [{"_id": ObjectId(worker_id) if ObjectId.is_valid(worker_id) else worker_id}]})
    if not worker_doc:
        raise HTTPException(status_code=404, detail="Worker not found")

    now = datetime.utcnow()

    # Update booking
    bookings_col.update_one(
        {"request_id": str(req_id)},
        {"$set": {"worker_id": str(worker_doc["_id"]), "status": "assigned", "updated_at": now}}
    )

    # Record dispatch attempt
    dispatch_col.insert_one({
        "request_id": str(req_id),
        "worker_id": str(worker_doc["_id"]),
        "status": "offered",
        "communication_method": "sms" if "sms" in worker_doc.get("digital_access", []) else "app",
        "offer_timestamp": now,
        "created_at": now,
    })

    return {"message": "Job successfully reassigned.", "worker_id": str(worker_doc["_id"])}
