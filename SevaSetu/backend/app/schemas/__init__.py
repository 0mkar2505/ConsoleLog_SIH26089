"""
MongoDB Pydantic schemas package for Console Log platform.
"""
from app.schemas.common import PyObjectId, MongoBaseModel
from app.schemas.documents import (
    GeoLocationSchema,
    CooperativeContactSchema,
    CooperativeSchema,
    UserSchema,
    UnavailablePeriodSchema,
    WorkerScheduleSchema,
    WorkerSchema,
    CustomerAddressSchema,
    CustomerSchema,
    ServiceSchema,
    ServiceRequestSchema,
    DispatchAttemptSchema,
    BookingSchema,
    CommunicationLogSchema,
    RatingSchema,
    InvoiceSchema,
)

__all__ = [
    "PyObjectId",
    "MongoBaseModel",
    "GeoLocationSchema",
    "CooperativeContactSchema",
    "CooperativeSchema",
    "UserSchema",
    "UnavailablePeriodSchema",
    "WorkerScheduleSchema",
    "WorkerSchema",
    "CustomerAddressSchema",
    "CustomerSchema",
    "ServiceSchema",
    "ServiceRequestSchema",
    "DispatchAttemptSchema",
    "BookingSchema",
    "CommunicationLogSchema",
    "RatingSchema",
    "InvoiceSchema",
]
