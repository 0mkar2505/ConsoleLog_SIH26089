"""
MongoDB database document helpers & converters for Console Log.
"""
from typing import Dict, Any, Optional
from bson import ObjectId


def clean_doc_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert BSON ObjectId _id field to string representation if present."""
    if doc and "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc


def str_to_object_id(id_str: str) -> ObjectId:
    """Safely convert string to BSON ObjectId."""
    if isinstance(id_str, ObjectId):
        return id_str
    if isinstance(id_str, str) and ObjectId.is_valid(id_str):
        return ObjectId(id_str)
    raise ValueError(f"Invalid ObjectId string: {id_str}")
