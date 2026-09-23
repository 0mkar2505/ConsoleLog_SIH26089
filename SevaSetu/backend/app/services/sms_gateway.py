"""
Low-digital access worker communication service (SMS & Voice simulator).
Allows workers without smartphones to receive plain-text SMS dispatch offers,
view job details via text, and respond with simple keypad inputs (1=ACCEPT, 2=REJECT).
Logs all events into MongoDB 'communication_logs' collection.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from bson import ObjectId

from app.database import (
    get_communication_logs_collection,
    get_dispatch_attempts_collection,
    get_bookings_collection,
    get_service_requests_collection,
    get_workers_collection,
    get_users_collection,
)
from app.models.document_helpers import clean_doc_id

logger = logging.getLogger(__name__)


def generate_job_sms_text(
    booking_id: str,
    service_name: str,
    customer_name: str,
    customer_phone: str,
    address: str,
    landmark: Optional[str],
    directions: Optional[str],
    scheduled_time: Optional[str],
    problem_description: str,
    estimated_price: float,
) -> str:
    """Format plaintext SMS message for low-digital workers."""
    short_id = booking_id[-6:].upper() if len(booking_id) >= 6 else booking_id.upper()
    time_str = scheduled_time or "IMMEDIATE"
    landmark_str = f" Near: {landmark}." if landmark else ""
    directions_str = f" Notes: {directions}." if directions else ""

    return (
        f"[SEVASETU COOP JOB #{short_id}]\n"
        f"Trade: {service_name}\n"
        f"Customer: {customer_name} ({customer_phone})\n"
        f"When: {time_str}\n"
        f"Address: {address}.{landmark_str}{directions_str}\n"
        f"Problem: {problem_description}\n"
        f"Payout Est: Rs.{int(estimated_price)}\n"
        f"---\n"
        f"Reply 1 to ACCEPT, 2 to REJECT"
    )


def send_dispatch_sms(
    worker_phone: str,
    worker_id: str,
    request_id: str,
    booking_id: str,
    message_body: str,
) -> Dict[str, Any]:
    """
    Simulates sending an SMS dispatch alert to a low-digital worker and logs to MongoDB.
    """
    comm_col = get_communication_logs_collection()
    now = datetime.utcnow()

    log_doc = {
        "worker_id": str(worker_id),
        "request_id": str(request_id),
        "job_id": str(booking_id),
        "recipient_phone": worker_phone,
        "direction": "outbound",
        "communication_method": "sms",
        "message": message_body,
        "status": "delivered",
        "timestamp": now,
        "created_at": now,
    }

    res = comm_col.insert_one(log_doc)
    log_doc["_id"] = str(res.inserted_id)

    logger.info(f"Simulated outbound SMS to worker {worker_phone} for booking {booking_id}")
    return log_doc


def handle_inbound_worker_sms(sender_phone: str, message_text: str) -> Dict[str, Any]:
    """
    Parse inbound SMS response from worker:
    - '1' or containing 'ACCEPT' -> Accept job
    - '2' or containing 'REJECT' -> Reject job
    """
    clean_text = message_text.strip().upper()
    now = datetime.utcnow()

    users_col = get_users_collection()
    workers_col = get_workers_collection()
    comm_col = get_communication_logs_collection()
    bookings_col = get_bookings_collection()
    dispatch_col = get_dispatch_attempts_collection()
    requests_col = get_service_requests_collection()

    # Find worker by phone
    user_doc = users_col.find_one({"phone": sender_phone})
    if not user_doc:
        # Try finding worker directly or normalized phone
        norm_phone = sender_phone.replace("+91", "").replace(" ", "")
        user_doc = users_col.find_one({"phone": {"$regex": norm_phone}})

    worker_id = None
    if user_doc:
        worker_doc = workers_col.find_one({"user_id": str(user_doc["_id"])})
        if worker_doc:
            worker_id = str(worker_doc["_id"])

    # Find the latest pending dispatch attempt for this worker
    query = {"status": "offered"}
    if worker_id:
        query["worker_id"] = worker_id

    latest_attempt = dispatch_col.find_one(query, sort=[("offer_timestamp", -1)])
    if not latest_attempt:
        # Fallback to any offered dispatch if test simulator
        latest_attempt = dispatch_col.find_one({"status": "offered"}, sort=[("offer_timestamp", -1)])

    if not latest_attempt:
        return {
            "success": False,
            "message": "No active job offer pending for this worker phone.",
            "response_text": "SevaSetu: You have no active job offers at this moment.",
        }

    req_id = latest_attempt.get("request_id")
    target_worker_id = latest_attempt.get("worker_id")

    # Inbound logging
    inbound_log = {
        "worker_id": target_worker_id,
        "request_id": req_id,
        "recipient_phone": sender_phone,
        "direction": "inbound",
        "communication_method": "sms",
        "message": message_text,
        "status": "received",
        "timestamp": now,
        "created_at": now,
    }
    comm_col.insert_one(inbound_log)

    is_accept = "1" in clean_text or "ACCEPT" in clean_text
    is_reject = "2" in clean_text or "REJECT" in clean_text or not is_accept

    if is_accept:
        # Mark dispatch attempt accepted
        dispatch_col.update_one(
            {"_id": latest_attempt["_id"]},
            {"$set": {"status": "accepted", "response_timestamp": now, "updated_at": now}}
        )

        # Update booking
        bookings_col.update_one(
            {"request_id": str(req_id)},
            {"$set": {"status": "accepted", "updated_at": now}}
        )

        # Update request
        requests_col.update_one(
            {"$or": [{"_id": ObjectId(req_id) if ObjectId.is_valid(req_id) else req_id}]},
            {"$set": {"status": "allocated", "updated_at": now}}
        )

        # Update worker workload
        if target_worker_id:
            w_obj = ObjectId(target_worker_id) if ObjectId.is_valid(target_worker_id) else target_worker_id
            workers_col.update_one({"_id": w_obj}, {"$set": {"current_workload": 1}})

        confirmation = f"SevaSetu: Job #{str(req_id)[-6:].upper()} ACCEPTED! Please head to customer address. Reply ARRIRED or 3 when on site."
    else:
        # Mark dispatch attempt rejected
        dispatch_col.update_one(
            {"_id": latest_attempt["_id"]},
            {"$set": {"status": "rejected", "rejection_reason": "Worker replied 2 (SMS)", "response_timestamp": now, "updated_at": now}}
        )
        confirmation = f"SevaSetu: Job #{str(req_id)[-6:].upper()} rejected. We will dispatch the next community worker."

    # Log confirmation reply
    outbound_confirm = {
        "worker_id": target_worker_id,
        "request_id": req_id,
        "recipient_phone": sender_phone,
        "direction": "outbound",
        "communication_method": "sms",
        "message": confirmation,
        "status": "delivered",
        "timestamp": now,
        "created_at": now,
    }
    comm_col.insert_one(outbound_confirm)

    return {
        "success": True,
        "action": "accepted" if is_accept else "rejected",
        "request_id": str(req_id),
        "worker_id": target_worker_id,
        "confirmation_sent": confirmation,
    }
