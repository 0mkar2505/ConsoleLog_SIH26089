"""
Unit and integration tests for Console Log MongoDB data model.
Tests cooperatives, multi-skill workers, digital access types, customer multi-addresses,
immediate & scheduled service requests, dispatch attempts, worker schedules,
SMS/app communication logs, geospatial indexes, and seed idempotency.
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings
from app.database import (
    get_db,
    init_db_indexes,
    get_cooperatives_collection,
    get_users_collection,
    get_workers_collection,
    get_customers_collection,
    get_services_collection,
    get_worker_services_collection,
    get_service_requests_collection,
    get_dispatch_attempts_collection,
    get_bookings_collection,
    get_communication_logs_collection,
    get_ratings_collection,
    get_invoices_collection,
)
from app.schemas import (
    CooperativeSchema,
    UserSchema,
    WorkerSchema,
    CustomerSchema,
    ServiceSchema,
    ServiceRequestSchema,
    DispatchAttemptSchema,
    BookingSchema,
    CommunicationLogSchema,
    RatingSchema,
    InvoiceSchema,
)
from app.seed import seed_database
import mongomock


ALL_COLLECTIONS = [
    "cooperatives",
    "users",
    "workers",
    "customers",
    "services",
    "worker_services",
    "service_requests",
    "dispatch_attempts",
    "bookings",
    "communication_logs",
    "ratings",
    "invoices",
]


@pytest.fixture(autouse=True)
def mock_mongo_if_offline(monkeypatch):
    """
    Fixture that attempts connection to live MongoDB.
    If live MongoDB is unavailable, gracefully patches PyMongo MongoClient with mongomock
    to ensure database unit tests pass cleanly without SQLite fallbacks.
    """
    try:
        real_db = get_db()
        real_db.command("ping")
        # Live MongoDB is available
        for col in ALL_COLLECTIONS:
            real_db[col].drop()
        init_db_indexes()
        yield
        for col in ALL_COLLECTIONS:
            real_db[col].drop()
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception):
        # Live MongoDB offline; patch with in-memory mongomock Database
        mock_client = mongomock.MongoClient()
        mock_db = mock_client[settings.MONGODB_DATABASE]

        monkeypatch.setattr("app.database.get_client", lambda: mock_client)
        monkeypatch.setattr("app.database.get_db", lambda: mock_db)

        # Initialize indexes on mock db
        init_db_indexes()
        yield
        for col in ALL_COLLECTIONS:
            mock_db[col].drop()


def test_mongodb_connection_and_indexes():
    """Test MongoDB connection and index creation across all collections."""
    db = get_db()
    assert db is not None

    coop_indexes = [idx["name"] for idx in db.cooperatives.list_indexes()]
    assert "name_1" in coop_indexes

    users_indexes = [idx["name"] for idx in db.users.list_indexes()]
    assert "email_1" in users_indexes
    assert "phone_1" in users_indexes

    workers_indexes = [idx["name"] for idx in db.workers.list_indexes()]
    assert "user_id_1" in workers_indexes
    assert "location_2dsphere" in workers_indexes
    assert "digital_access_1" in workers_indexes

    customers_indexes = [idx["name"] for idx in db.customers.list_indexes()]
    assert "user_id_1" in customers_indexes

    services_indexes = [idx["name"] for idx in db.services.list_indexes()]
    assert "name_1" in services_indexes

    requests_indexes = [idx["name"] for idx in db.service_requests.list_indexes()]
    assert "location_2dsphere" in requests_indexes
    assert "status_1" in requests_indexes
    assert "request_type_1" in requests_indexes


def test_cooperative_creation():
    """Test Cooperative creation and unique name constraint."""
    coops_col = get_cooperatives_collection()

    coop_doc = {
        "name": "Dadar Workers Cooperative",
        "description": "Central Mumbai coop",
        "contact_info": {"phone": "+912224100001", "email": "dadar@coop.org"},
        "service_areas": ["Dadar", "Sion"],
        "is_active": True
    }
    res = coops_col.insert_one(coop_doc)
    assert res.inserted_id is not None

    found = coops_col.find_one({"_id": res.inserted_id})
    schema = CooperativeSchema(**found)
    assert schema.name == "Dadar Workers Cooperative"
    assert "Dadar" in schema.service_areas

    with pytest.raises(DuplicateKeyError):
        coops_col.insert_one(coop_doc)


def test_user_creation_and_unique_email():
    """Test User document creation and unique email index constraint."""
    users_col = get_users_collection()

    user_doc = {
        "name": "Test User",
        "email": "testuser@consolelog.in",
        "phone": "+919999999999",
        "password_hash": "hash123",
        "role": "customer"
    }
    res = users_col.insert_one(user_doc)
    assert res.inserted_id is not None

    found = users_col.find_one({"_id": res.inserted_id})
    schema = UserSchema(**found)
    assert schema.id == str(res.inserted_id)

    with pytest.raises(DuplicateKeyError):
        users_col.insert_one(user_doc)


def test_worker_creation_with_digital_access_and_schedule():
    """Test Worker creation with multi-skills, digital access types, schedule, and location."""
    users_col = get_users_collection()
    coops_col = get_cooperatives_collection()
    workers_col = get_workers_collection()

    u_res = users_col.insert_one({"name": "Low Digital Worker", "email": "ldw@consolelog.in", "password_hash": "pass", "role": "worker"})
    c_res = coops_col.insert_one({"name": "Sion Coop", "service_areas": ["Sion"]})

    u_id = str(u_res.inserted_id)
    c_id = str(c_res.inserted_id)

    w_doc = {
        "user_id": u_id,
        "cooperative_id": c_id,
        "services": ["Plumbing", "Electrical"],
        "digital_access": ["sms", "voice"],
        "is_verified": True,
        "is_available": True,
        "availability_schedule": {
            "working_days": ["Mon", "Wed", "Fri"],
            "working_hours": {"start": "09:00", "end": "18:00"},
            "unavailable_periods": []
        },
        "location": {"type": "Point", "coordinates": [72.8478, 19.0178]},
        "service_area": "Sion",
        "current_workload": 0,
        "max_concurrent_jobs": 1
    }
    w_res = workers_col.insert_one(w_doc)
    assert w_res.inserted_id is not None

    found_w = workers_col.find_one({"_id": w_res.inserted_id})
    w_schema = WorkerSchema(**found_w)
    assert w_schema.user_id == u_id
    assert w_schema.cooperative_id == c_id
    assert "sms" in w_schema.digital_access
    assert "voice" in w_schema.digital_access
    assert len(w_schema.services) == 2


def test_customer_multi_address_creation():
    """Test Customer profile creation with multiple saved addresses containing landmarks & directions."""
    users_col = get_users_collection()
    cust_col = get_customers_collection()

    u_res = users_col.insert_one({"name": "Customer MultiAddr", "email": "cma@consolelog.in", "password_hash": "pass", "role": "customer"})
    u_id = str(u_res.inserted_id)

    c_doc = {
        "user_id": u_id,
        "saved_addresses": [
            {
                "id": "addr_home",
                "label": "Home",
                "address": "12 Station Road, Sion East, Mumbai",
                "landmark": "Opposite Station",
                "additional_directions": "Flat 301, 3rd Floor",
                "location": {"type": "Point", "coordinates": [72.8625, 19.0400]}
            },
            {
                "id": "addr_work",
                "label": "Work",
                "address": "BKC Annex, Bandra East, Mumbai",
                "landmark": "Near ICICI Tower",
                "additional_directions": "5th Floor",
                "location": {"type": "Point", "coordinates": [72.8680, 19.0650]}
            }
        ]
    }
    res = cust_col.insert_one(c_doc)
    assert res.inserted_id is not None

    found = cust_col.find_one({"_id": res.inserted_id})
    schema = CustomerSchema(**found)
    assert len(schema.saved_addresses) == 2
    assert schema.saved_addresses[0].landmark == "Opposite Station"


def test_service_request_immediate_and_scheduled():
    """Test Service Request creation for immediate and scheduled modes with flexibility windows."""
    req_col = get_service_requests_collection()

    req_imm = {
        "customer_id": "cust_123",
        "service_id": "serv_electrical",
        "problem_description": "Car broke down right now",
        "request_type": "immediate",
        "address": "Sion Circle, Mumbai",
        "landmark": "Near Sion Fort",
        "status": "pending"
    }
    imm_res = req_col.insert_one(req_imm)

    now = datetime.utcnow()
    req_sch = {
        "customer_id": "cust_123",
        "service_id": "serv_plumbing",
        "problem_description": "Tap leaking tomorrow at 5 PM",
        "request_type": "scheduled",
        "address": "Hill Road, Bandra",
        "preferred_date": "2026-09-24",
        "preferred_start_time": now + timedelta(days=1, hours=5),
        "flexibility": "plus_minus_30m",
        "status": "pending"
    }
    sch_res = req_col.insert_one(req_sch)

    imm_schema = ServiceRequestSchema(**req_col.find_one({"_id": imm_res.inserted_id}))
    sch_schema = ServiceRequestSchema(**req_col.find_one({"_id": sch_res.inserted_id}))

    assert imm_schema.request_type == "immediate"
    assert sch_schema.request_type == "scheduled"
    assert sch_schema.flexibility == "plus_minus_30m"


def test_dispatch_attempt_recording():
    """Test Dispatch Attempt creation and history tracking."""
    disp_col = get_dispatch_attempts_collection()

    att1 = {
        "request_id": "req_1001",
        "worker_id": "work_1",
        "status": "rejected",
        "communication_method": "app",
        "rejection_reason": "Occupied on another job"
    }
    att2 = {
        "request_id": "req_1001",
        "worker_id": "work_2",
        "status": "accepted",
        "communication_method": "sms"
    }

    disp_col.insert_one(att1)
    disp_col.insert_one(att2)

    attempts = list(disp_col.find({"request_id": "req_1001"}))
    assert len(attempts) == 2
    schema1 = DispatchAttemptSchema(**attempts[0])
    schema2 = DispatchAttemptSchema(**attempts[1])

    assert schema1.status == "rejected"
    assert schema2.communication_method == "sms"


def test_communication_log_recording():
    """Test Communication Log creation for low-digital SMS message audit."""
    comm_col = get_communication_logs_collection()

    log_doc = {
        "request_id": "req_1001",
        "worker_id": "work_low_digital",
        "communication_method": "sms",
        "direction": "outbound",
        "message_body": "NEW JOB #1001 Service: Plumbing. Address: Sion. Reply 1=ACCEPT 2=REJECT",
        "status": "sent",
        "provider_message_id": "SMS-MOCK-1010"
    }
    res = comm_col.insert_one(log_doc)
    assert res.inserted_id is not None

    found = comm_col.find_one({"_id": res.inserted_id})
    schema = CommunicationLogSchema(**found)
    assert schema.communication_method == "sms"
    assert schema.direction == "outbound"


def test_booking_rating_and_invoice_workflow():
    """Test Booking creation and referencing Rating and Invoice documents."""
    users_col = get_users_collection()
    workers_col = get_workers_collection()
    services_col = get_services_collection()
    bookings_col = get_bookings_collection()
    ratings_col = get_ratings_collection()
    invoices_col = get_invoices_collection()

    c_id = str(users_col.insert_one({"name": "Customer", "email": "c@consolelog.in", "password_hash": "p", "role": "customer"}).inserted_id)
    w_u_id = str(users_col.insert_one({"name": "Worker", "email": "w@consolelog.in", "password_hash": "p", "role": "worker"}).inserted_id)
    w_id = str(workers_col.insert_one({"user_id": w_u_id, "service_area": "Bandra"}).inserted_id)
    s_id = str(services_col.insert_one({"name": "Appliance Repair", "base_price": 400.0, "category": "Maintenance"}).inserted_id)

    b_doc = {
        "customer_id": c_id,
        "worker_id": w_id,
        "service_id": s_id,
        "address": "Bandra West",
        "status": "completed",
        "estimated_price": 400.0
    }
    b_id_raw = bookings_col.insert_one(b_doc).inserted_id
    b_id = str(b_id_raw)

    r_doc = {
        "booking_id": b_id,
        "customer_id": c_id,
        "worker_id": w_id,
        "rating": 5,
        "comment": "Superb work"
    }
    r_id_raw = ratings_col.insert_one(r_doc).inserted_id

    inv_doc = {
        "booking_id": b_id,
        "invoice_number": "INV-CONSOLELOG-TEST",
        "amount": 400.0,
        "payment_status": "paid"
    }
    inv_id_raw = invoices_col.insert_one(inv_doc).inserted_id

    b_schema = BookingSchema(**bookings_col.find_one({"_id": b_id_raw}))
    r_schema = RatingSchema(**ratings_col.find_one({"_id": r_id_raw}))
    inv_schema = InvoiceSchema(**invoices_col.find_one({"_id": inv_id_raw}))

    assert b_schema.status == "completed"
    assert r_schema.booking_id == b_id
    assert inv_schema.booking_id == b_id


def test_seed_idempotency():
    """Test that running the seed function twice does not duplicate records."""
    seed_database()

    coops_col = get_cooperatives_collection()
    users_col = get_users_collection()
    workers_col = get_workers_collection()
    cust_col = get_customers_collection()
    services_col = get_services_collection()
    requests_col = get_service_requests_collection()
    dispatch_col = get_dispatch_attempts_collection()

    count_coops_1 = coops_col.count_documents({})
    count_users_1 = users_col.count_documents({})
    count_workers_1 = workers_col.count_documents({})
    count_cust_1 = cust_col.count_documents({})
    count_services_1 = services_col.count_documents({})
    count_requests_1 = requests_col.count_documents({})
    count_dispatch_1 = dispatch_col.count_documents({})

    assert count_coops_1 == 2
    assert count_workers_1 == 10
    assert count_cust_1 == 4
    assert count_services_1 == 6
    assert count_requests_1 == 2
    assert count_dispatch_1 == 3

    # Run seed second time
    seed_database()

    assert coops_col.count_documents({}) == count_coops_1
    assert users_col.count_documents({}) == count_users_1
    assert workers_col.count_documents({}) == count_workers_1
    assert cust_col.count_documents({}) == count_cust_1
    assert services_col.count_documents({}) == count_services_1
    assert requests_col.count_documents({}) == count_requests_1
    assert dispatch_col.count_documents({}) == count_dispatch_1
