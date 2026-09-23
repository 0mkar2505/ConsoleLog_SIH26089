"""
MongoDB database connection manager, collection accessors, and index initializers for Console Log platform.
Uses PyMongo driver to connect to MongoDB.
"""
import logging
from typing import Optional
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

# Configure DNS resolver to avoid Windows SRV lookup timeouts with MongoDB Atlas
try:
    import dns.resolver
    _custom_resolver = dns.resolver.Resolver(configure=False)
    _custom_resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
    dns.resolver.default_resolver = _custom_resolver
except Exception as _e:
    pass

from app.config import settings

logger = logging.getLogger(__name__)

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """Get or create singleton PyMongo MongoClient instance."""
    global _client
    if _client is None:
        try:
            _client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Verify server is reachable
            _client.admin.command('ping')
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB at {settings.MONGODB_URI}: {e}")
            raise ConnectionFailure(
                f"MongoDB connection failed at {settings.MONGODB_URI}. "
                "Ensure MongoDB server is running or MONGODB_URI environment variable is correctly configured."
            ) from e
    return _client


def get_db() -> Database:
    """Get MongoDB database instance."""
    client = get_client()
    return client[settings.MONGODB_DATABASE]


# Collection Accessors
def get_cooperatives_collection():
    return get_db()["cooperatives"]


def get_users_collection():
    return get_db()["users"]


def get_workers_collection():
    return get_db()["workers"]


def get_customers_collection():
    return get_db()["customers"]


def get_services_collection():
    return get_db()["services"]


def get_worker_services_collection():
    return get_db()["worker_services"]


def get_service_requests_collection():
    return get_db()["service_requests"]


def get_dispatch_attempts_collection():
    return get_db()["dispatch_attempts"]


def get_bookings_collection():
    return get_db()["bookings"]


def get_communication_logs_collection():
    return get_db()["communication_logs"]


def get_ratings_collection():
    return get_db()["ratings"]


def get_invoices_collection():
    return get_db()["invoices"]


def init_db_indexes():
    """Create MongoDB indexes across all Console Log collections."""
    db = get_db()

    # 1. Cooperatives collection
    db.cooperatives.create_index([("name", ASCENDING)], unique=True)
    db.cooperatives.create_index([("is_active", ASCENDING)])

    # 2. Users collection
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("phone", ASCENDING)])
    db.users.create_index([("role", ASCENDING)])

    # 3. Workers collection
    db.workers.create_index([("user_id", ASCENDING)], unique=True)
    db.workers.create_index([("cooperative_id", ASCENDING)])
    db.workers.create_index([("services", ASCENDING)])
    db.workers.create_index([("is_verified", ASCENDING)])
    db.workers.create_index([("is_available", ASCENDING)])
    db.workers.create_index([("digital_access", ASCENDING)])
    db.workers.create_index([("location", "2dsphere")])

    # 4. Customers collection
    db.customers.create_index([("user_id", ASCENDING)], unique=True)
    db.customers.create_index([("saved_addresses.location", "2dsphere")])

    # 5. Services collection
    db.services.create_index([("name", ASCENDING)], unique=True)
    db.services.create_index([("category", ASCENDING)])

    # 6. WorkerServices legacy link collection
    db.worker_services.create_index(
        [("worker_id", ASCENDING), ("service_id", ASCENDING)],
        unique=True
    )

    # 7. Service Requests collection (Immediate & Scheduled)
    db.service_requests.create_index([("customer_id", ASCENDING)])
    db.service_requests.create_index([("service_id", ASCENDING)])
    db.service_requests.create_index([("status", ASCENDING)])
    db.service_requests.create_index([("request_type", ASCENDING)])
    db.service_requests.create_index([("created_at", ASCENDING)])
    db.service_requests.create_index([("location", "2dsphere")])

    # 8. Dispatch Attempts collection
    db.dispatch_attempts.create_index([("request_id", ASCENDING)])
    db.dispatch_attempts.create_index([("worker_id", ASCENDING)])
    db.dispatch_attempts.create_index([("status", ASCENDING)])
    db.dispatch_attempts.create_index([("created_at", ASCENDING)])

    # 9. Bookings / Jobs collection
    db.bookings.create_index([("customer_id", ASCENDING)])
    db.bookings.create_index([("worker_id", ASCENDING)])
    db.bookings.create_index([("cooperative_id", ASCENDING)])
    db.bookings.create_index([("service_id", ASCENDING)])
    db.bookings.create_index([("status", ASCENDING)])
    db.bookings.create_index([("scheduled_start", ASCENDING)])
    db.bookings.create_index([("request_id", ASCENDING)])

    # 10. Communication Logs collection (SMS / Voice / App history)
    db.communication_logs.create_index([("worker_id", ASCENDING)])
    db.communication_logs.create_index([("request_id", ASCENDING)])
    db.communication_logs.create_index([("job_id", ASCENDING)])
    db.communication_logs.create_index([("communication_method", ASCENDING)])
    db.communication_logs.create_index([("timestamp", ASCENDING)])

    # 11. Ratings collection
    db.ratings.create_index([("booking_id", ASCENDING)], unique=True)
    db.ratings.create_index([("worker_id", ASCENDING)])

    # 12. Invoices collection
    db.invoices.create_index([("booking_id", ASCENDING)], unique=True)
    db.invoices.create_index([("invoice_number", ASCENDING)], unique=True)


def close_db_client():
    """Close MongoClient connection on shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
