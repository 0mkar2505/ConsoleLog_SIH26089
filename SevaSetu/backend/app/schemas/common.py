"""
Common schema utilities for MongoDB ObjectId handling in Pydantic v2.
"""
from typing import Any
from bson import ObjectId
from pydantic import BaseModel, ConfigDict
from pydantic_core import core_schema


class PyObjectId(str):
    """Custom Pydantic field type for handling BSON ObjectId serialization and validation."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(cls.validate),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value: Any) -> str:
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, str):
            if ObjectId.is_valid(value):
                return value
            raise ValueError(f"Invalid ObjectId: '{value}'")
        raise ValueError(f"Cannot convert {type(value)} to ObjectId string")


class MongoBaseModel(BaseModel):
    """Base model with population by field name enabled for MongoDB document conversion."""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
