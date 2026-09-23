"""
Services router for Console Log API.
Provides service catalog for customer service selection.
"""
from fastapi import APIRouter
from typing import List, Dict, Any
from app.database import get_services_collection
from app.models.document_helpers import clean_doc_id

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def list_services():
    """Get active services list for customer selection."""
    services_col = get_services_collection()
    docs = list(services_col.find({"is_active": True}))
    cleaned = []
    for d in docs:
        d = clean_doc_id(d)
        d["id"] = str(d["_id"])
        cleaned.append(d)
    return cleaned
