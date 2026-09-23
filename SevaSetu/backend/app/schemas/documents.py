"""
Pydantic schemas for MongoDB documents in Console Log platform.
Enforces validation and document serialization for all core architecture entities.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import MongoBaseModel, PyObjectId


# GeoJSON Location Schema for MongoDB 2dsphere indexing
class GeoLocationSchema(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


# Cooperative Schemas
class CooperativeContactSchema(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class CooperativeSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    description: Optional[str] = None
    contact_info: Optional[CooperativeContactSchema] = None
    service_areas: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# User Schemas
class UserSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    email: str
    phone: Optional[str] = None
    password_hash: str
    role: str  # 'customer', 'worker', 'admin'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Worker Availability & Schedule Schemas
class UnavailablePeriodSchema(BaseModel):
    start: datetime
    end: datetime
    reason: Optional[str] = None


class WorkerScheduleSchema(BaseModel):
    working_days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    working_hours: Dict[str, str] = {"start": "08:00", "end": "20:00"}
    unavailable_periods: List[UnavailablePeriodSchema] = []


# Worker Schemas
class WorkerSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str  # References users._id as string
    cooperative_id: Optional[str] = None  # References cooperatives._id as string
    services: List[str] = []  # Service names or service IDs provided
    digital_access: List[str] = ["smartphone"]  # e.g., ["smartphone"], ["sms"], ["voice"], ["smartphone", "sms"]
    is_verified: bool = False
    is_available: bool = True
    availability_schedule: Optional[WorkerScheduleSchema] = None
    location: Optional[GeoLocationSchema] = None
    location_updated_at: Optional[datetime] = None
    service_area: Optional[str] = None
    max_service_radius_km: float = 10.0
    current_workload: int = 0
    max_concurrent_jobs: int = 1
    completed_jobs: int = 0
    rating_average: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Customer Address & Profile Schemas
class CustomerAddressSchema(BaseModel):
    id: Optional[str] = None
    label: str  # e.g., "Home", "Office", "Parents"
    address: str  # Full human-readable street address
    landmark: Optional[str] = None
    additional_directions: Optional[str] = None
    location: Optional[GeoLocationSchema] = None


class CustomerSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str  # References users._id
    saved_addresses: List[CustomerAddressSchema] = []
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Service Schemas
class ServiceSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    description: Optional[str] = None
    base_price: float
    category: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Service Request Schemas (Immediate vs Scheduled)
class ServiceRequestSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    customer_id: str  # References customers._id or users._id
    service_id: str  # References services._id
    problem_description: str
    request_type: str = "immediate"  # "immediate" or "scheduled"
    location: Optional[GeoLocationSchema] = None
    address: str
    landmark: Optional[str] = None
    directions: Optional[str] = None
    preferred_date: Optional[str] = None  # e.g., "2026-09-24"
    preferred_start_time: Optional[datetime] = None
    preferred_end_time: Optional[datetime] = None
    flexibility: str = "exact"  # "exact", "plus_minus_30m", "plus_minus_1h", "custom_window"
    status: str = "pending"  # "pending", "dispatching", "allocated", "fulfilled", "cancelled", "expired"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Dispatch Attempt Schemas
class DispatchAttemptSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    request_id: str  # References service_requests._id
    worker_id: str  # References workers._id
    offer_timestamp: datetime = Field(default_factory=datetime.utcnow)
    response_timestamp: Optional[datetime] = None
    status: str = "offered"  # "offered", "accepted", "rejected", "no_response", "expired", "cancelled"
    communication_method: str = "app"  # "app", "sms", "voice"
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Booking / Job Schemas
class BookingSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    request_id: Optional[str] = None  # References service_requests._id
    customer_id: str  # References users._id or customers._id
    worker_id: str  # References workers._id
    cooperative_id: Optional[str] = None  # References cooperatives._id
    service_id: str  # References services._id
    scheduled_start: Optional[datetime] = None
    estimated_duration_minutes: int = 60
    location: Optional[GeoLocationSchema] = None
    address: str
    landmark: Optional[str] = None
    directions: Optional[str] = None
    status: str = "pending"  # "pending", "dispatching", "assigned", "accepted", "rejected", "en_route", "arrived", "in_progress", "completed", "cancelled"
    estimated_price: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# Communication Log Schemas
class CommunicationLogSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    request_id: Optional[str] = None
    job_id: Optional[str] = None
    worker_id: str  # References workers._id
    customer_id: Optional[str] = None
    communication_method: str = "sms"  # "app", "sms", "voice"
    direction: str = "outbound"  # "outbound", "inbound"
    message_body: Optional[str] = None
    status: str = "sent"  # "sent", "delivered", "failed", "received", "completed"
    provider_message_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Rating Schemas
class RatingSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    booking_id: str  # References bookings._id / jobs._id
    customer_id: str
    worker_id: str
    rating: int  # 1 to 5
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Invoice Schemas
class InvoiceSchema(MongoBaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    booking_id: str  # References bookings._id / jobs._id
    invoice_number: str
    amount: float
    payment_status: str = "pending"  # "pending", "paid", "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
