"""
Integration tests for Console Log FastAPI REST endpoints & End-to-End workflow:
Customer Request -> Dispatch Engine -> Worker Accept -> Status Updates -> Customer Status View.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.seed import seed_database
from app.database import get_db, init_db_indexes
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings
import mongomock

client = TestClient(app)

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
    """Ensure database is seeded for API integration tests."""
    try:
        real_db = get_db()
        real_db.command("ping")
        for col in ALL_COLLECTIONS:
            real_db[col].drop()
        init_db_indexes()
        seed_database()
        yield
    except (ConnectionFailure, ServerSelectionTimeoutError, Exception):
        mock_client = mongomock.MongoClient()
        mock_db = mock_client[settings.MONGODB_DATABASE]

        monkeypatch.setattr("app.database.get_client", lambda: mock_client)
        monkeypatch.setattr("app.database.get_db", lambda: mock_db)

        init_db_indexes()
        seed_database()
        yield


def test_services_and_auth_endpoints():
    """Test GET /api/services and GET /api/auth/demo-accounts."""
    r_services = client.get("/api/services")
    assert r_services.status_code == 200
    services = r_services.json()
    assert len(services) >= 6
    assert any(s["name"] == "Electrical" for s in services)

    r_auth = client.get("/api/auth/demo-accounts")
    assert r_auth.status_code == 200
    accounts = r_auth.json()
    assert "customers" in accounts
    assert "workers" in accounts
    assert len(accounts["customers"]) > 0
    assert len(accounts["workers"]) > 0


def test_end_to_end_customer_worker_flow():
    """
    Test complete End-to-End flow:
    1. Customer submits request -> POST /api/requests
    2. Dispatch assigns worker & creates booking
    3. Worker retrieves job -> GET /api/worker/jobs
    4. Worker accepts job -> POST /api/worker/jobs/{id}/accept
    5. Worker updates status -> POST /api/worker/jobs/{id}/status (en_route -> completed)
    6. Customer views completed status -> GET /api/requests/{id}
    """
    # 1. Fetch Electrical service ID
    services = client.get("/api/services").json()
    electrical_service = next(s for s in services if s["name"] == "Electrical")

    # 2. Customer posts request
    req_payload = {
        "service_id": electrical_service["id"],
        "problem_description": "Main circuit breaker tripped in living room",
        "address": "12 Station Road, Sion East, Mumbai",
        "landmark": "Opposite Sion Railway Station",
        "directions": "Gate 2, 3rd Floor",
        "request_type": "immediate",
        "latitude": 19.0400,
        "longitude": 72.8625
    }
    r_create = client.post("/api/requests", json=req_payload)
    assert r_create.status_code == 201
    res_data = r_create.json()

    assert "request" in res_data
    assert "dispatch" in res_data
    assert res_data["dispatch"] is not None

    req_id = res_data["request"]["id"]
    assigned_worker_id = res_data["dispatch"]["worker_id"]
    booking_id = res_data["dispatch"]["booking_id"]

    assert assigned_worker_id is not None
    assert booking_id is not None

    # 3. Worker retrieves jobs
    r_jobs = client.get(f"/api/worker/jobs?worker_id={assigned_worker_id}")
    assert r_jobs.status_code == 200
    jobs = r_jobs.json()
    assert len(jobs) >= 1
    my_job = next(j for j in jobs if j["booking_id"] == booking_id)
    assert my_job["status"] == "assigned"

    # 4. Worker accepts job
    r_accept = client.post(f"/api/worker/jobs/{booking_id}/accept")
    assert r_accept.status_code == 200
    assert r_accept.json()["status"] == "accepted"

    # 5. Worker marks en_route -> completed
    r_enroute = client.post(f"/api/worker/jobs/{booking_id}/status", json={"status": "en_route"})
    assert r_enroute.status_code == 200
    assert r_enroute.json()["status"] == "en_route"

    r_completed = client.post(f"/api/worker/jobs/{booking_id}/status", json={"status": "completed"})
    assert r_completed.status_code == 200
    assert r_completed.json()["status"] == "completed"

    # 6. Customer retrieves request & verifies completed status
    r_status = client.get(f"/api/requests/{req_id}")
    assert r_status.status_code == 200
    final_data = r_status.json()
    assert final_data["booking"]["status"] == "completed"
    assert final_data["current_status"] in ["completed", "fulfilled"]
