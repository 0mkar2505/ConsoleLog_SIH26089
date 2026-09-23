"""
MongoDB database models & document helpers package for Console Log.
"""
from app.models.document_helpers import clean_doc_id, str_to_object_id

__all__ = ["clean_doc_id", "str_to_object_id"]
