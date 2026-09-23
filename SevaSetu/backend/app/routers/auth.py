"""
Demo Auth Router for Console Log platform.
Provides simple role switching accounts for Customer and Worker demo applications.
"""
from fastapi import APIRouter
from typing import Dict, Any
from app.database import get_users_collection, get_workers_collection, get_customers_collection
from app.models.document_helpers import clean_doc_id

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.get("/demo-accounts")
def get_demo_accounts() -> Dict[str, Any]:
    """Return pre-seeded customer and worker demo profiles for instant app login."""
    users_col = get_users_collection()
    workers_col = get_workers_collection()
    customers_col = get_customers_collection()

    customers = []
    c_users = list(users_col.find({"role": "customer"}))
    for u in c_users:
        u_id = str(u["_id"])
        c_doc = customers_col.find_one({"user_id": u_id})
        customers.append({
            "user_id": u_id,
            "customer_id": str(c_doc["_id"]) if c_doc else u_id,
            "name": u.get("name"),
            "email": u.get("email"),
            "phone": u.get("phone")
        })

    workers = []
    w_users = list(users_col.find({"role": "worker"}))
    for u in w_users:
        u_id = str(u["_id"])
        w_doc = workers_col.find_one({"user_id": u_id})
        if w_doc:
            workers.append({
                "user_id": u_id,
                "worker_id": str(w_doc["_id"]),
                "name": u.get("name"),
                "email": u.get("email"),
                "phone": u.get("phone"),
                "digital_access": w_doc.get("digital_access", ["smartphone"]),
                "service_area": w_doc.get("service_area", "Dadar")
            })

    return {
        "customers": customers,
        "workers": workers
    }
