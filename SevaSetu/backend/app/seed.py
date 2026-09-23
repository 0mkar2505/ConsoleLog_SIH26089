"""
MongoDB database seeding script for Console Log platform.
Populates reproducible sample cooperatives, users, workers, customers, services,
service requests (immediate & scheduled), dispatch attempts, bookings/jobs,
communication logs, ratings, and invoices into MongoDB.

Usage:
    python -m app.seed
    or python app/seed.py
"""
import sys
import os
import logging
from datetime import datetime, timedelta

# Ensure backend directory is in sys.path when run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    """Seed initial deterministic data into MongoDB collections idempotently."""
    logger.info("Initializing MongoDB indexes...")
    init_db_indexes()

    coops_col = get_cooperatives_collection()
    users_col = get_users_collection()
    workers_col = get_workers_collection()
    customers_col = get_customers_collection()
    services_col = get_services_collection()
    ws_col = get_worker_services_collection()
    requests_col = get_service_requests_collection()
    dispatch_col = get_dispatch_attempts_collection()
    bookings_col = get_bookings_collection()
    comm_col = get_communication_logs_collection()
    ratings_col = get_ratings_collection()
    invoices_col = get_invoices_collection()

    logger.info("Seeding MongoDB collections idempotently...")
    now = datetime.utcnow()

    # 1. Seed Cooperatives
    coop_data = [
        {
            "name": "Dadar Workers Cooperative",
            "description": "Central Mumbai local worker community cooperative",
            "contact_info": {
                "phone": "+912224100001",
                "email": "contact@dadarcoop.org",
                "address": "45 Plaza Cinema Building, Dadar West, Mumbai"
            },
            "service_areas": ["Dadar", "Sion", "Kurla", "Prabhadevi", "Ghatkopar"],
            "is_active": True,
        },
        {
            "name": "Bandra Service Society",
            "description": "Western Suburbs cooperative service network",
            "contact_info": {
                "phone": "+912226400002",
                "email": "info@bandraservices.org",
                "address": "12 Hill Road, Bandra West, Mumbai"
            },
            "service_areas": ["Bandra", "Khar", "Santacruz", "Andheri", "Thane", "Navi Mumbai"],
            "is_active": True,
        }
    ]
    coop_ids = {}
    for c_item in coop_data:
        res = coops_col.find_one_and_update(
            {"name": c_item["name"]},
            {
                "$setOnInsert": {"created_at": now},
                "$set": {
                    "description": c_item["description"],
                    "contact_info": c_item["contact_info"],
                    "service_areas": c_item["service_areas"],
                    "is_active": c_item["is_active"],
                    "updated_at": now,
                }
            },
            upsert=True,
            return_document=True
        )
        coop_ids[c_item["name"]] = str(res["_id"])

    # 2. Seed Admin User
    admin_doc = {
        "name": "System Admin",
        "email": "admin@consolelog.in",
        "password_hash": "$2b$12$dummyhashforadminpasswordconsolelog2026",
        "role": "admin",
        "phone": "+919800000000",
        "updated_at": now
    }
    users_col.update_one(
        {"email": admin_doc["email"]},
        {"$setOnInsert": {"created_at": now}, "$set": admin_doc},
        upsert=True
    )

    # 3. Seed Customer Users & Customer Documents (with saved multi-addresses)
    customers_raw_data = [
        {
            "name": "Rahul Sharma",
            "email": "rahul.sharma@gmail.com",
            "phone": "+919811111111",
            "addresses": [
                {
                    "id": "addr_1",
                    "label": "Home",
                    "address": "12 Station Road, Sion East, Mumbai",
                    "landmark": "Opposite Sion Railway Station",
                    "additional_directions": "Gate 2, 3rd Floor, Flat 301",
                    "location": {"type": "Point", "coordinates": [72.8625, 19.0400]}
                },
                {
                    "id": "addr_2",
                    "label": "Office",
                    "address": "BKC Annex, Bandra East, Mumbai",
                    "landmark": "Near ICICI Bank Tower",
                    "additional_directions": "Tower B, 5th Floor",
                    "location": {"type": "Point", "coordinates": [72.8680, 19.0650]}
                }
            ]
        },
        {
            "name": "Priya Patel",
            "email": "priya.patel@gmail.com",
            "phone": "+919822222222",
            "addresses": [
                {
                    "id": "addr_3",
                    "label": "Home",
                    "address": "Flat 402, Sea View Apartments, Bandra West, Mumbai",
                    "landmark": "Near Carter Road Promenade",
                    "additional_directions": "Ring doorbell at main entrance",
                    "location": {"type": "Point", "coordinates": [72.8250, 19.0600]}
                }
            ]
        },
        {
            "name": "Amit Verma",
            "email": "amit.verma@gmail.com",
            "phone": "+919833333333",
            "addresses": [
                {
                    "id": "addr_4",
                    "label": "Home",
                    "address": "7 Hill Road, Dadar West, Mumbai",
                    "landmark": "Next to Plaza Cinema",
                    "additional_directions": "2nd Floor, Room 14",
                    "location": {"type": "Point", "coordinates": [72.8450, 19.0200]}
                }
            ]
        },
        {
            "name": "Sneha Kulkarni",
            "email": "sneha.kulkarni@gmail.com",
            "phone": "+919844444400",
            "addresses": [
                {
                    "id": "addr_5",
                    "label": "Home",
                    "address": "25 LBS Marg, Kurla West, Mumbai",
                    "landmark": "Opposite Phoenix Marketcity",
                    "additional_directions": "Building C, Flat 102",
                    "location": {"type": "Point", "coordinates": [72.8880, 19.0800]}
                }
            ]
        }
    ]

    customer_user_ids = {}
    customer_doc_ids = {}
    for c_info in customers_raw_data:
        c_user_doc = {
            "name": c_info["name"],
            "email": c_info["email"],
            "password_hash": "$2b$12$dummyhashforcustomerpasswordconsolelog",
            "role": "customer",
            "phone": c_info["phone"],
            "updated_at": now
        }
        u_res = users_col.find_one_and_update(
            {"email": c_info["email"]},
            {"$setOnInsert": {"created_at": now}, "$set": c_user_doc},
            upsert=True,
            return_document=True
        )
        u_id_str = str(u_res["_id"])
        customer_user_ids[c_info["email"]] = u_id_str

        cust_profile_doc = {
            "user_id": u_id_str,
            "saved_addresses": c_info["addresses"],
            "notes": "Verified customer account",
            "updated_at": now
        }
        cust_res = customers_col.find_one_and_update(
            {"user_id": u_id_str},
            {"$setOnInsert": {"created_at": now}, "$set": cust_profile_doc},
            upsert=True,
            return_document=True
        )
        customer_doc_ids[c_info["email"]] = str(cust_res["_id"])

    # 4. Seed Services
    services_data = [
        ("Plumbing", "Pipe fitting, leak repairs, tap fixing, and sanitaryware installation", 350.0, "Maintenance"),
        ("Electrical", "Wiring, switchboard repair, fan/light fitting, and appliance installation", 400.0, "Maintenance"),
        ("Cleaning", "Full house deep cleaning, kitchen and bathroom sanitation services", 500.0, "Sanitation"),
        ("Carpentry", "Furniture repair, door/window fitting, lock installation, and woodwork", 450.0, "Furniture"),
        ("Painting", "Interior/exterior wall painting, damp proofing, and touchup work", 600.0, "Renovation"),
        ("Appliance Repair", "Washing machine, AC, refrigerator, microwave, and water purifier servicing", 350.0, "Maintenance"),
    ]
    service_ids = {}
    for name, desc, price, cat in services_data:
        s_doc = {
            "name": name,
            "description": desc,
            "base_price": price,
            "category": cat,
            "is_active": True,
            "updated_at": now
        }
        res = services_col.find_one_and_update(
            {"name": name},
            {"$setOnInsert": {"created_at": now}, "$set": s_doc},
            upsert=True,
            return_document=True
        )
        service_ids[name] = str(res["_id"])

    # 5. Seed Workers (Digital-First & Low-Digital-Access across Cooperatives)
    workers_data = [
        {
            "name": "Ramesh Kumar", "email": "ramesh.kumar@gmail.com", "phone": "+919844444401",
            "coop": "Dadar Workers Cooperative", "digital_access": ["smartphone"],
            "area": "Dadar", "lat": 19.0178, "lng": 72.8478, "verified": True, "available": True,
            "rating": 4.8, "jobs": 24, "services": ["Plumbing", "Electrical"], "workload": 0
        },
        {
            "name": "Suresh Pawar", "email": "suresh.pawar@gmail.com", "phone": "+919844444402",
            "coop": "Bandra Service Society", "digital_access": ["smartphone"],
            "area": "Bandra", "lat": 19.0596, "lng": 72.8295, "verified": True, "available": True,
            "rating": 4.6, "jobs": 18, "services": ["Electrical"], "workload": 1
        },
        {
            "name": "Sunita Shinde", "email": "sunita.shinde@gmail.com", "phone": "+919844444403",
            "coop": "Dadar Workers Cooperative", "digital_access": ["sms", "voice"],
            "area": "Andheri", "lat": 19.1197, "lng": 72.8464, "verified": True, "available": True,
            "rating": 4.9, "jobs": 35, "services": ["Cleaning"], "workload": 0
        },
        {
            "name": "Anil Jadhav", "email": "anil.jadhav@gmail.com", "phone": "+919844444404",
            "coop": "Bandra Service Society", "digital_access": ["sms"],
            "area": "Thane", "lat": 19.2183, "lng": 72.9781, "verified": True, "available": True,
            "rating": 4.5, "jobs": 12, "services": ["Carpentry"], "workload": 0
        },
        {
            "name": "Ganesh Kadam", "email": "ganesh.kadam@gmail.com", "phone": "+919844444405",
            "coop": "Dadar Workers Cooperative", "digital_access": ["smartphone"],
            "area": "Kurla", "lat": 19.0726, "lng": 72.8845, "verified": False, "available": True,
            "rating": 4.2, "jobs": 5, "services": ["Painting"], "workload": 0
        },
        {
            "name": "Vijay Salunkhe", "email": "vijay.salunkhe@gmail.com", "phone": "+919844444406",
            "coop": "Bandra Service Society", "digital_access": ["smartphone"],
            "area": "Colaba", "lat": 18.9067, "lng": 72.8147, "verified": True, "available": True,
            "rating": 4.7, "jobs": 29, "services": ["Appliance Repair"], "workload": 0
        },
        {
            "name": "Santosh More", "email": "santosh.more@gmail.com", "phone": "+919844444407",
            "coop": "Dadar Workers Cooperative", "digital_access": ["sms", "voice"],
            "area": "Powai", "lat": 19.1176, "lng": 72.9060, "verified": True, "available": True,
            "rating": 4.4, "jobs": 15, "services": ["Plumbing"], "workload": 0
        },
        {
            "name": "Laxmi Gaikwad", "email": "laxmi.gaikwad@gmail.com", "phone": "+919844444408",
            "coop": "Bandra Service Society", "digital_access": ["smartphone"],
            "area": "Borivali", "lat": 19.2307, "lng": 72.8567, "verified": False, "available": False,
            "rating": 4.1, "jobs": 8, "services": ["Cleaning", "Painting"], "workload": 0
        },
        {
            "name": "Deepak Chavan", "email": "deepak.chavan@gmail.com", "phone": "+919844444409",
            "coop": "Bandra Service Society", "digital_access": ["smartphone"],
            "area": "Navi Mumbai", "lat": 19.0330, "lng": 73.0297, "verified": True, "available": True,
            "rating": 4.9, "jobs": 42, "services": ["Appliance Repair", "Electrical"], "workload": 0
        },
        {
            "name": "Rajesh Thorat", "email": "rajesh.thorat@gmail.com", "phone": "+919844444410",
            "coop": "Dadar Workers Cooperative", "digital_access": ["sms"],
            "area": "Ghatkopar", "lat": 19.0860, "lng": 72.9080, "verified": True, "available": True,
            "rating": 4.3, "jobs": 10, "services": ["Carpentry", "Painting"], "workload": 0
        },
    ]

    worker_user_ids = {}
    worker_doc_ids = {}

    default_schedule = {
        "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "working_hours": {"start": "08:00", "end": "20:00"},
        "unavailable_periods": []
    }

    for w_info in workers_data:
        w_user_doc = {
            "name": w_info["name"],
            "email": w_info["email"],
            "password_hash": "$2b$12$dummyhashforworkerpasswordconsolelog",
            "role": "worker",
            "phone": w_info["phone"],
            "updated_at": now
        }
        user_res = users_col.find_one_and_update(
            {"email": w_info["email"]},
            {"$setOnInsert": {"created_at": now}, "$set": w_user_doc},
            upsert=True,
            return_document=True
        )
        u_id_str = str(user_res["_id"])
        worker_user_ids[w_info["email"]] = u_id_str

        s_ids = [service_ids[s_name] for s_name in w_info["services"]]
        coop_id_str = coop_ids[w_info["coop"]]

        w_doc = {
            "user_id": u_id_str,
            "cooperative_id": coop_id_str,
            "service_area": w_info["area"],
            "digital_access": w_info["digital_access"],
            "location": {
                "type": "Point",
                "coordinates": [w_info["lng"], w_info["lat"]]  # GeoJSON [longitude, latitude]
            },
            "location_updated_at": now,
            "is_verified": w_info["verified"],
            "is_available": w_info["available"],
            "availability_schedule": default_schedule,
            "max_service_radius_km": 12.0,
            "current_workload": w_info["workload"],
            "max_concurrent_jobs": 1,
            "rating_average": w_info["rating"],
            "completed_jobs": w_info["jobs"],
            "services": s_ids,
            "updated_at": now
        }
        w_res = workers_col.find_one_and_update(
            {"user_id": u_id_str},
            {"$setOnInsert": {"created_at": now}, "$set": w_doc},
            upsert=True,
            return_document=True
        )
        w_id_str = str(w_res["_id"])
        worker_doc_ids[w_info["email"]] = w_id_str

        # Seed legacy WorkerServices collection entries
        for s_id_str in s_ids:
            ws_col.update_one(
                {"worker_id": w_id_str, "service_id": s_id_str},
                {"$setOnInsert": {"created_at": now}},
                upsert=True
            )

    # 6. Seed Service Requests (Immediate & Scheduled)
    # Request 1: Immediate breakdown problem
    req1_doc = {
        "customer_id": customer_doc_ids["rahul.sharma@gmail.com"],
        "service_id": service_ids["Electrical"],
        "problem_description": "Car won't start - electrical battery failure in garage",
        "request_type": "immediate",
        "location": {"type": "Point", "coordinates": [72.8625, 19.0400]},
        "address": "12 Station Road, Sion East, Mumbai",
        "landmark": "Opposite Sion Railway Station",
        "directions": "Gate 2, 3rd Floor, Flat 301",
        "flexibility": "exact",
        "status": "fulfilled",
        "updated_at": now - timedelta(days=2)
    }
    req1_res = requests_col.find_one_and_update(
        {
            "customer_id": req1_doc["customer_id"],
            "service_id": req1_doc["service_id"],
            "problem_description": req1_doc["problem_description"]
        },
        {"$setOnInsert": {"created_at": now - timedelta(days=2)}, "$set": req1_doc},
        upsert=True,
        return_document=True
    )
    req1_id = str(req1_res["_id"])

    # Request 2: Scheduled Plumbing request
    scheduled_time = now + timedelta(days=1, hours=4)
    req2_doc = {
        "customer_id": customer_doc_ids["priya.patel@gmail.com"],
        "service_id": service_ids["Plumbing"],
        "problem_description": "Bathroom sink pipe leak repair required tomorrow afternoon",
        "request_type": "scheduled",
        "location": {"type": "Point", "coordinates": [72.8250, 19.0600]},
        "address": "Flat 402, Sea View Apartments, Bandra West, Mumbai",
        "landmark": "Near Carter Road Promenade",
        "directions": "Ring doorbell at main entrance",
        "preferred_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
        "preferred_start_time": scheduled_time,
        "preferred_end_time": scheduled_time + timedelta(hours=2),
        "flexibility": "plus_minus_30m",
        "status": "pending",
        "updated_at": now
    }
    req2_res = requests_col.find_one_and_update(
        {
            "customer_id": req2_doc["customer_id"],
            "service_id": req2_doc["service_id"],
            "problem_description": req2_doc["problem_description"]
        },
        {"$setOnInsert": {"created_at": now}, "$set": req2_doc},
        upsert=True,
        return_document=True
    )
    req2_id = str(req2_res["_id"])

    # 7. Seed Dispatch Attempts History
    # Attempt 1: Offer to Suresh Pawar (Rejected)
    disp1_doc = {
        "request_id": req1_id,
        "worker_id": worker_doc_ids["suresh.pawar@gmail.com"],
        "status": "rejected",
        "communication_method": "app",
        "rejection_reason": "Busy on active job",
        "response_timestamp": now - timedelta(days=2, minutes=10),
        "updated_at": now - timedelta(days=2)
    }
    dispatch_col.update_one(
        {"request_id": req1_id, "worker_id": disp1_doc["worker_id"]},
        {"$setOnInsert": {"created_at": now - timedelta(days=2, minutes=15), "offer_timestamp": now - timedelta(days=2, minutes=15)}, "$set": disp1_doc},
        upsert=True
    )

    # Attempt 2: Offer to Ramesh Kumar (Accepted)
    disp2_doc = {
        "request_id": req1_id,
        "worker_id": worker_doc_ids["ramesh.kumar@gmail.com"],
        "status": "accepted",
        "communication_method": "app",
        "response_timestamp": now - timedelta(days=2, minutes=5),
        "updated_at": now - timedelta(days=2)
    }
    dispatch_col.update_one(
        {"request_id": req1_id, "worker_id": disp2_doc["worker_id"]},
        {"$setOnInsert": {"created_at": now - timedelta(days=2, minutes=8), "offer_timestamp": now - timedelta(days=2, minutes=8)}, "$set": disp2_doc},
        upsert=True
    )

    # Attempt 3: Low-digital SMS offer to Sunita Shinde (Pending / Offered)
    disp3_doc = {
        "request_id": req2_id,
        "worker_id": worker_doc_ids["sunita.shinde@gmail.com"],
        "status": "offered",
        "communication_method": "sms",
        "updated_at": now
    }
    dispatch_col.update_one(
        {"request_id": req2_id, "worker_id": disp3_doc["worker_id"]},
        {"$setOnInsert": {"created_at": now, "offer_timestamp": now}, "$set": disp3_doc},
        upsert=True
    )

    # 8. Seed Bookings / Jobs
    b1_doc = {
        "request_id": req1_id,
        "customer_id": customer_user_ids["rahul.sharma@gmail.com"],
        "worker_id": worker_doc_ids["ramesh.kumar@gmail.com"],
        "cooperative_id": coop_ids["Dadar Workers Cooperative"],
        "service_id": service_ids["Electrical"],
        "scheduled_start": now - timedelta(days=2),
        "estimated_duration_minutes": 60,
        "location": {"type": "Point", "coordinates": [72.8625, 19.0400]},
        "address": "12 Station Road, Sion East, Mumbai",
        "landmark": "Opposite Sion Railway Station",
        "directions": "Gate 2, 3rd Floor, Flat 301",
        "status": "completed",
        "estimated_price": 400.0,
        "completed_at": now - timedelta(days=2, hours=-1),
        "updated_at": now - timedelta(days=2)
    }
    b1_res = bookings_col.find_one_and_update(
        {
            "request_id": req1_id,
            "customer_id": b1_doc["customer_id"],
            "worker_id": b1_doc["worker_id"]
        },
        {"$setOnInsert": {"created_at": now - timedelta(days=2)}, "$set": b1_doc},
        upsert=True,
        return_document=True
    )
    b1_id_str = str(b1_res["_id"])

    # 9. Seed Communication Logs (SMS & App)
    comm1_doc = {
        "request_id": req2_id,
        "job_id": None,
        "worker_id": worker_doc_ids["sunita.shinde@gmail.com"],
        "customer_id": customer_user_ids["priya.patel@gmail.com"],
        "communication_method": "sms",
        "direction": "outbound",
        "message_body": (
            "NEW JOB #REQ-4821\n"
            "Service: Plumbing\n"
            "Customer: Priya Patel (+919822222222)\n"
            "Address: Flat 402, Sea View Apartments, Bandra West, Mumbai\n"
            "Landmark: Near Carter Road Promenade\n"
            "Problem: Bathroom sink pipe leak repair\n"
            "Time: Tomorrow 5 PM\n"
            "Reply 1=ACCEPT, 2=REJECT"
        ),
        "status": "delivered",
        "provider_message_id": "MSG-TWILIO-99881122",
        "timestamp": now
    }
    comm_col.update_one(
        {"worker_id": comm1_doc["worker_id"], "provider_message_id": comm1_doc["provider_message_id"]},
        {"$set": comm1_doc},
        upsert=True
    )

    # 10. Seed Rating for Booking 1
    r1_doc = {
        "booking_id": b1_id_str,
        "customer_id": customer_user_ids["rahul.sharma@gmail.com"],
        "worker_id": worker_doc_ids["ramesh.kumar@gmail.com"],
        "rating": 5,
        "comment": "Excellent electrical repair work! Arrived on time and solved the battery problem cleanly.",
        "created_at": now - timedelta(days=2)
    }
    ratings_col.update_one(
        {"booking_id": b1_id_str},
        {"$set": r1_doc},
        upsert=True
    )

    # 11. Seed Invoice for Booking 1
    inv1_doc = {
        "booking_id": b1_id_str,
        "invoice_number": "INV-CONSOLELOG-0001",
        "amount": 400.0,
        "payment_status": "paid",
        "created_at": now - timedelta(days=2)
    }
    invoices_col.update_one(
        {"booking_id": b1_id_str},
        {"$set": inv1_doc},
        upsert=True
    )

    logger.info("Successfully seeded Console Log MongoDB database with:")
    logger.info(f" - {len(coop_data)} Cooperatives")
    logger.info(f" - 1 Admin User ({admin_doc['email']})")
    logger.info(f" - {len(customers_raw_data)} Customer Records with saved multi-addresses")
    logger.info(f" - {len(workers_data)} Worker Records (Digital-First & Low-Digital SMS/Voice)")
    logger.info(f" - {len(services_data)} Service Documents")
    logger.info(" - 2 Service Requests (Immediate & Scheduled with flexibility windows)")
    logger.info(" - 3 Dispatch Attempt Records (Offered/Rejected/Accepted history)")
    logger.info(" - 1 Completed Booking/Job")
    logger.info(" - 1 Low-Digital SMS Communication Log")
    logger.info(" - 1 Rating and 1 Paid Invoice")


if __name__ == "__main__":
    seed_database()
