# Project Constitution: Console Log

## 1. Project Metadata
- **Problem Statement**: Cooperative Service Allocation and Dispatch Platform for Household & Community Services
- **Platform Name**: Console Log Platform
- **Team**: Console Log
- **Nature of Project**: Cooperative Service Allocation & Capacity Dispatch Infrastructure
- **Primary Goal**: Build a cooperative service allocation and dispatch platform connecting customers with local cooperative workers while supporting multi-tiered levels of digital access (Digital-First Mobile & Low-Digital-Access SMS/Voice).

---

## 2. Product Concept & Core Architecture (FINAL — Source of Truth)

Console Log is **NOT** a generic gig-worker marketplace where customers manually select a worker from a list.

It is a **cooperative service allocation and dispatch platform** designed to intelligently allocate community workforce capacity to customer demand based on:
- Service/skill match
- Worker availability & schedule
- Worker workload
- Proximity & estimated travel time
- Verification status
- Cooperative/service operational area
- Digital communication capabilities

The platform connects four participant interfaces to a central, unified Python FastAPI backend.

```text
+-------------------------------------------------------------------------------+
|                            CONSOLE LOG PLATFORM                               |
+-------------------------------------------------------------------------------+
|  1. Customer Interface        |  2. Digital-First Worker Interface            |
|     - Flutter Mobile App      |     - Flutter Mobile App (Role-based)         |
|     - Immediate & Scheduled   |     - Skills, Area, Schedule & Availability     |
|     - Address, Landmark, Directions- Navigation & Job Status Workflow         |
+-------------------------------+-----------------------------------------------+
|  3. Low-Digital-Access Worker |  4. Admin / Cooperative Dashboard             |
|     - Standard SMS / Voice    |     - React + Vite Web Dashboard              |
|     - Plaintext Job Specs     |     - Cooperative & Worker Management         |
|     - Reply 1=ACCEPT, 2=REJECT|     - Workforce Capacity & Demand Analytics   |
+-------------------------------+-----------------------------------------------+
                                |
                                v
+-------------------------------------------------------------------------------+
|  CENTRAL BACKEND (FastAPI + PyMongo + Pydantic v2)                            |
|  - Dispatch Engine            - Scheduling Engine                             |
|  - Availability Engine        - Matching Engine                               |
|  - Notification Service       - Communication/SMS Service (Mock/Provider)     |
|  - Analytics Engine           - Central Database: MongoDB (PyMongo)           |
+-------------------------------------------------------------------------------+
```

---

## 3. Four Participant Interfaces

### Interface 1: Customer
- **Technology**: Flutter Mobile Application (role-based experience within the unified mobile application).
- **Core Capabilities**:
  - Register & login (Customer self-registration).
  - Maintain profile and save multi-location addresses (latitude/longitude coordinates + human-readable address + landmark + additional directions).
  - Submit service requests under two modes:
    1. **Immediate**: On-demand problem reporting (e.g. "My car broke down"). System determines required service and dispatches a suitable nearby worker.
    2. **Scheduled**: Future booking request (e.g. "I need a plumber tomorrow at 5 PM"). Scheduling system considers worker calendar, travel time, and community capacity. Supports flexible window preferences (exact time, ±30 mins, ±1 hour, preferred window).
  - View automated worker assignment and job status updates (`pending` -> `accepted` -> `en_route` -> `in_progress` -> `completed`).
  - Receive real-time notifications (WebSockets & FCM).
  - View service history and rate completed services.

### Interface 2: Digital-First Worker
- **Technology**: Flutter Mobile Application (role-based experience).
- **Core Capabilities**:
  - Registered through cooperative/admin process.
  - Manage availability (`online`/`offline`), service skills, and operational service area.
  - Receive real-time job offers with customer location and detailed address breakdown.
  - Accept or reject job offers.
  - Interactive map and navigation interface via `flutter_map` + OpenStreetMap.
  - Update job progress status (`en_route` -> `in_progress` -> `completed`).
  - View upcoming scheduled jobs, completed job history, earnings summary, and ratings.
- **Communication Protocol**: Flutter App UI, WebSockets for realtime events, FCM push notifications.

### Interface 3: Low-Digital-Access Worker
- **Technology**: Cellular Phone (SMS and optional Voice/IVR).
- **Target Audience**: Cooperative workers without smartphones, mobile internet, or app capabilities.
- **Participation Flow**:
  - Registered with cooperative using standard phone number.
  - Receives complete human-readable job dispatch message via SMS containing:
    - Job ID
    - Service required
    - Customer name & phone number
    - Full human-readable address, landmark, & additional directions
    - Requested time & immediate/scheduled status
    - Incident/problem description
  - Accepts or rejects via simple SMS reply (e.g., `1 = ACCEPT`, `2 = REJECT`).
  - System must **NOT** assume low-digital workers can open URLs or transmit continuous GPS.
  - After acceptance, worker can call customer directly if additional guidance is required.

### Interface 4: Admin / Cooperative Management
- **Technology**: React + Vite Web Dashboard.
- **Scope**: Dedicated exclusively to cooperative administration, capacity oversight, and analytics.
- **Core Capabilities**:
  - Cooperative organization management and service area configuration.
  - Worker registration, background credential review, skill management, and verification.
  - Operational booking and job dispatch monitoring across immediate & scheduled requests.
  - Customer records and service history review.
  - Community workforce capacity monitoring and real-time demand analytics.
  - Cooperative-level performance reports and fair-wage index tracking.

---

## 4. Core Backend & Engine Architecture

The backend API (Python 3.10+ / FastAPI / PyMongo / Pydantic v2) serves as the central source of truth. All clients (Flutter app, SMS gateway, React Dashboard) communicate exclusively with the backend API. Direct database access from frontend/mobile clients is strictly prohibited.

### Core Backend Engines:

1. **Dispatch Engine**:
   - Manages immediate service requests.
   - Evaluates customer problem -> identifies service -> fetches customer location & structured address -> finds candidate workers -> filters by skills, verification, availability, distance, workload, and communication channel -> dispatches job offer -> manages acceptance lifecycle and fallback escalation.

2. **Scheduling Engine**:
   - Manages future service bookings.
   - Evaluates worker calendars, existing commitments, service duration, travel buffer times, and customer preferred flexibility windows (exact, ±30m, ±1h, window).
   - Handles capacity reallocation, waitlists, and cancellation-based reassignments.

3. **Availability Engine**:
   - Tracks actual worker availability and shift schedules beyond simple boolean flags.
   - Evaluates community-level capacity ("Can this community satisfy this request?").

4. **Matching Engine**:
   - Multi-factor algorithmic worker selection taking into account skills, location, workload, schedule, distance, travel time, and verification.

5. **Notification Service**:
   - Broadcasts real-time events over WebSockets and dispatches background alerts via FCM.

6. **Communication / SMS Service**:
   - Pluggable SMS gateway abstraction handling outbound job dispatches and inbound SMS reply webhooks (`1 = ACCEPT`, `2 = REJECT`).
   - Includes a mock SMS gateway for local development and testing without physical SMS costs.

7. **Analytics Engine**:
   - Evaluates demand forecasting, location-based service trends, community workforce capacity, and predicted labor shortages.
   - Delivers advisory recommendations to cooperative administrators in the web dashboard.

---

## 5. Location & Mapping Model

- **Customer Requests**: Must support both:
  1. Latitude / Longitude coordinates (for geospatial calculations & digital worker navigation).
  2. Human-readable address + Landmark + Additional directions (essential for low-digital workers).
- **Worker Location**:
  - Digital-First Workers: Live location updates via Flutter app.
  - Low-Digital Workers: Operational service area / neighborhood assignment (continuous GPS is NOT assumed).
- **Maps**: `flutter_map` with OpenStreetMap (OSM) tile rendering. Paid Google Maps APIs are prohibited unless explicitly approved.

---

## 6. Database Architecture

- **Technology**: MongoDB using PyMongo driver (`pymongo`).
- **Configuration**: Managed via `MONGODB_URI` and `MONGODB_DATABASE`.
- **Geospatial Indexing**: `2dsphere` indexes on worker locations for spatial queries.
- **Strict Prohibition**: MongoDB is the sole database engine. Do **NOT** reintroduce SQLite, SQLAlchemy, PostgreSQL, or ORM layers.

---

## 7. Strict Technical Prohibitions

Do **NOT** introduce any of the following without prior explicit approval:
- **Database Switching**: No SQLite, SQLAlchemy, PostgreSQL, MySQL, or Firebase Firestore.
- **Manual Worker List Selection**: Do not build interfaces where customers pick workers from a catalog list.
- **Hard Dependency on SMS Providers**: Local dev must work using mock SMS services.
- **Paid Maps**: No paid Google Maps or Mapbox SDKs.
- **Real Payment SDKs**: No live payment gateway integrations (Razorpay, Stripe, etc.); payments remain mocked.
- **Direct Database Access**: Neither Flutter nor React may access MongoDB directly.

---

## 8. Repository Structure

```text
SevaSetu/
├── AGENTS.md                  # Project constitution (this file)
├── TASKS.md                   # System roadmap and task tracker
├── README.md                  # Setup & architecture overview
├── .env.example               # Environment variables template
│
├── mobile/                    # Component 1 & 2: Flutter App (Customer + Digital Worker)
│   ├── pubspec.yaml
│   └── lib/
│       ├── main.dart
│       ├── config/            # App routes & theme
│       ├── models/            # Customer & Worker models
│       ├── services/          # REST, WebSocket, FCM clients
│       └── screens/           # Customer & Worker role-based screens
│
├── backend/                   # Central Python FastAPI Backend
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # FastAPI entry point & WebSockets
│   │   ├── config.py          # Pydantic environment configuration
│   │   ├── database.py        # PyMongo client & index initialization
│   │   ├── seed.py            # Reproducible MongoDB seed script
│   │   ├── models/            # MongoDB document helpers
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── routers/           # REST endpoints
│   │   └── services/          # Engines: Dispatch, Scheduling, Matching, SMS, Analytics
│   └── tests/
│
├── dashboard/                 # Component 4: React + Vite Admin Dashboard
│   ├── package.json
│   ├── vite.config.js
│   └── src/                   # Cooperative management UI & Analytics
│
├── ml/                        # Intelligence & Advisory Analytics Module
│   └── forecasting/           # Demand forecasting & capacity heuristics
│
└── data/                      # Seed data JSONs & synthetic datasets
```

---

## 9. AI Pair-Programming Rules

Before modifying code:
1. Check `AGENTS.md` and `TASKS.md`.
2. Inspect existing codebase and maintain consistency with Console Log architectural principles.
3. Keep changes incremental, modular, and clear.
4. Report changes made with exact file paths.
