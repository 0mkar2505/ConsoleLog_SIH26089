# Project Constitution: SevaSetu (PS 26089)

## 1. Project Metadata
- **Problem Statement**: PS 26089 — Cooperative Gig Services Platform for Household & Community Services
- **Platform Name**: SevaSetu
- **Team**: Null Value
- **Nature of Project**: 12-Hour Hackathon MVP (Functional demonstration, NOT enterprise production)
- **Primary Goal**: Build a functional 12-hour MVP demonstrating a cooperative gig-services platform connecting customers with verified local workers, supporting booking, worker acceptance, service status, ratings, mock invoices/payments, and cooperative/admin analytics.

---

## 2. Core Application Architecture (FINAL — Source of Truth)

The platform consists of **FOUR major components**:

```text
+-------------------------------------------------------------------------------+
|                           SEVASETU PLATFORM                                   |
+-------------------------------------------------------------------------------+
|  1. Mobile App (Flutter)       |  3. Admin Dashboard (React + Vite)           |
|     - Dual-role (Customer/Worker)  - Cooperative Admin & Ops Only             |
|     - flutter_map + OSM        |     - Workforce Insights & Demand Charts     |
|     - REST + WebSockets + FCM  |     - REST API to FastAPI                    |
+--------------------------------+----------------------------------------------+
                                 |
                                 v
+-------------------------------------------------------------------------------+
|  2. Central Backend (FastAPI + SQLAlchemy + Pydantic)                         |
|     - JWT Auth, Roles, Verification, Bookings, Haversine Geospatial Matching  |
|     - Realtime WebSockets Hub, FCM Integration, Mock Invoicing & Payments    |
+-------------------------------------------------------------------------------+
         |                                              |
         v                                              v
+----------------------------------+   +----------------------------------------+
|  4. Database (SQLite)            |   |  AI / Analytics Module (Pandas/sklearn)|
|     - sevasetu.db (local dev)    |   |     - Demand forecasting               |
|     - Reproducible seed scripts  |   |     - Workforce shortage alerts        |
|     - Zero direct client access  |   |     - Fully modular (non-blocking)     |
+----------------------------------+   +----------------------------------------+
```

### Component 1: Mobile Application (Primary User-Facing App)
- **Technology**: Flutter / Dart
- **Role Model**: ONE single Flutter application serving **both Customer and Worker**. The authenticated user's role determines which interface renders.
- **Customer Functionality**:
  - Registration & login
  - Service discovery & category browsing
  - Location selection & nearby worker discovery on map
  - Worker profile inspection & transparent cooperative rate viewing
  - Booking creation & real-time status tracking
  - In-app live status updates via WebSockets & background push notifications (FCM)
  - Booking history, ratings/reviews, and mock itemized invoices
- **Worker Functionality**:
  - Login & worker profile management (skills, pricing, service radius)
  - Availability toggle (`online`/`offline`)
  - Incoming booking notifications & acceptance/rejection
  - Real-time job status transitions (`en_route` -> `in_progress` -> `completed`)
  - Service location mapping
  - Completed jobs history, earnings summary, and customer ratings
- **Communication Protocol**:
  - REST APIs for standard CRUD operations
  - WebSockets (via FastAPI) for real-time live events
  - Firebase Cloud Messaging (FCM) for push notifications (FCM is NOT a hard blocker for local dev)
- **Maps**: `flutter_map` with OpenStreetMap tiles (strict prohibition on paid Google Maps APIs without explicit approval)

### Component 2: Central Backend API
- **Technology**: Python 3.10+ / FastAPI / SQLAlchemy ORM / Pydantic v2
- **Role**: Central application & business logic engine. Neither Flutter nor the Admin Dashboard may access the database directly.
- **Responsibilities**:
  - Authentication (JWT), password hashing, role-based authorization
  - User and worker profile lifecycle, worker verification
  - Service category management & pricing structures
  - Location handling & deterministic Haversine distance-based worker matching
  - Booking lifecycle management & state machine enforcement
  - Ratings & reviews calculation
  - Mock invoice generation (itemized cooperative splits: worker share vs. cooperative fund)
  - Real-time event broadcasting over WebSockets
  - Push notification dispatch via FCM
  - Analytical aggregations and ML module hooks

### Component 3: Admin Web Dashboard
- **Technology**: React / Vite / JavaScript / React Router
- **Scope**: Dedicated **ONLY** for administrative and cooperative management.
- **Strict Constraint**: Do NOT build customer or worker web applications; customer and worker experiences belong exclusively in the Flutter mobile application.
- **Capabilities**:
  - Cooperative manager login
  - Worker verification, credential review, and roster management
  - Service catalog management
  - Live booking monitoring & operational overview
  - Cooperative statistics, fair-wage index, and fund balances
  - Demand analytics and workforce insights (powered by the analytics module)
  - Geographic/operational density maps where useful

### Component 4: Database Layer
- **Technology**: SQLite (`sevasetu.db`) with SQLAlchemy ORM
- **Scope**: Development and demo database.
- **Seed & Reproducibility**: Automated table creation on startup with reproducible seed script (`seed.py`).
- **Git Hygiene**: Generated `.db`, `.sqlite`, or `.sqlite3` files must NEVER be committed to Git.
- **Strict Constraint**: Do NOT introduce PostgreSQL, MongoDB, Firebase Database/Firestore, or Supabase.

---

## 3. Subsystem Specifications

### Authentication & Authorization
- Lightweight JWT authentication with role claims: `customer`, `worker`, `admin`.
- Secure password hashing (e.g. `passlib`/`bcrypt`).
- Unified authentication system serving both the Flutter app and Admin Dashboard.
- Never hardcode passwords, tokens, or secrets.

### Location & Worker Matching
- Workers store `latitude`, `longitude`, service capabilities, availability status, and verification status.
- Python Haversine formula calculates geographic distance.
- Worker discovery filters by:
  1. Requested service category
  2. Verified status (`is_verified == True`)
  3. Availability (`is_available == True`)
  4. Distance within worker's operational radius
- Pure deterministic, distance-based matching initially. Do NOT introduce AI into the core matching path.

### Mapping & Geolocation UI
- Frontend/Mobile mapping MUST use `flutter_map` + OpenStreetMap (OSM) tile servers.
- Free, open-source mapping only. No paid map APIs (Google Maps, Mapbox) without explicit approval.

### Realtime Communication (WebSockets)
- FastAPI WebSockets manage live in-app sessions.
- In-app events include:
  - `booking_requested`
  - `booking_accepted` / `booking_rejected`
  - `status_changed` (`en_route`, `in_progress`, `completed`)
  - `payment_confirmed`

### Push Notifications (FCM)
- Firebase Cloud Messaging (FCM) for background/system alerts.
- **Critical Local Dev Rule**: FCM must be structured gracefully with mock/noop fallbacks so that local development and testing never stall if FCM credentials or physical devices are absent.

### AI & Analytics Module
- **Technology**: Python, Pandas, `scikit-learn` where appropriate.
- **Decoupling**: The core application MUST function completely without the AI/analytics module.
- **Scope**: Evaluates historical and synthetic booking data to generate:
  - Service demand forecasts across time intervals
  - Demand distribution by neighborhood/location
  - Worker capacity and projected workforce shortages
  - Cooperative workforce recommendations (e.g., recruitment needs, shift optimization)
- **Role**: AI outputs are recommendations for cooperative managers in the Admin Dashboard, NOT automated black-box decisions.
- **Strict Prohibitions**: No OpenAI API, TensorFlow, PyTorch, or external paid LLM/AI APIs without explicit approval.

### Payments & Invoicing
- 100% **MOCKED** for the hackathon MVP.
- Simulated payment flows with itemized receipts detailing:
  - Service base cost
  - Worker payout (e.g., 90%)
  - Cooperative fund allocation (e.g., 10%)
- Strictly NO integration with real payment gateways (Razorpay, Stripe, PayPal, etc.).

---

## 4. Strict Prohibitions ("DO NOT INTRODUCE")
Do **NOT** introduce any of the following without prior explicit user approval:
- **Databases**: No PostgreSQL, MongoDB, CouchDB, MySQL, Firebase Firestore/RTDB, or Supabase.
- **Cloud/BaaS Auth**: No OAuth, Google Sign-In, Auth0, or Clerk.
- **Infrastructure / Orchestration**: No Kubernetes, Docker (unless explicitly requested), Celery, or background worker brokers.
- **Caching & Message Queues**: No Redis, RabbitMQ, Kafka, or Memcached.
- **API Formats**: No GraphQL, gRPC, or SOAP (REST + WebSockets only).
- **Payment Gateways**: No real payment SDKs (Razorpay, Stripe, PayPal).
- **External Dependencies**: No government APIs (Aadhaar, DigiLocker, etc.) or paid mapping services.
- **Heavy ML/LLM Libraries**: No TensorFlow, PyTorch, or paid external LLM APIs.
- **Separate Web Apps**: No separate Customer/Worker web apps (Flutter is the sole customer/worker interface).

---

## 5. Repository Structure

All work is organized strictly within the project folder:

```text
SevaSetu/
├── AGENTS.md                  # Project constitution (this file)
├── TASKS.md                   # Milestone tracker & progress log
├── README.md                  # Setup & execution instructions
├── .gitignore                 # Git ignore rules
├── .env.example               # Template environment configuration
│
├── mobile/                    # Component 1: Flutter Mobile Application
│   ├── pubspec.yaml
│   ├── lib/
│   │   ├── main.dart
│   │   ├── config/            # App constants, routes, theme
│   │   ├── models/            # Dart data models
│   │   ├── services/          # REST client, WebSocket client, FCM service
│   │   ├── providers/         # State management (auth, booking, worker)
│   │   ├── screens/
│   │   │   ├── auth/          # Login, Register, Role selection
│   │   │   ├── customer/      # Discovery, Map, Booking, Invoices, Ratings
│   │   │   └── worker/        # Requests, Job Tracker, Profile, Earnings
│   │   └── widgets/           # MapView, StatusChip, WorkerCard
│
├── backend/                   # Component 2: Central FastAPI Backend
│   ├── requirements.txt
│   ├── main.py                # FastAPI entry point & WebSocket endpoints
│   ├── config.py              # Environment settings (Pydantic Settings)
│   ├── database.py            # SQLite engine & sessionmaker
│   ├── models/                # SQLAlchemy database models
│   │   ├── user.py
│   │   ├── worker.py
│   │   ├── service.py
│   │   ├── booking.py
│   │   └── review.py
│   ├── schemas/               # Pydantic validation schemas
│   ├── routers/               # API route handlers (auth, workers, bookings, etc.)
│   ├── services/              # Business logic (geo/Haversine, notifications)
│   └── seed.py                # Reproducible database seed data script
│
├── dashboard/                 # Component 3: React Admin Web Dashboard
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── api/               # REST client for backend endpoints
│       ├── pages/             # Verification, Analytics, Bookings, Services
│       └── components/        # MetricsCard, ChartWidget, Header, Sidebar
│
├── ml/                        # Component 4: AI & Analytics Module
│   ├── requirements.txt
│   ├── forecast.py            # Demand forecasting & workforce analysis
│   └── recommendations.py     # Cooperative decision recommendations
│
├── data/                      # Synthetic data, seed JSONs, test datasets
└── docs/                      # Architecture notes, API specifications, demo scripts
```

---

## 6. Cross-Platform Development & Git Hygiene Rules

The repository MUST remain cleanly cloneable and runnable on any developer machine:
- **No machine-specific paths**: Always use relative paths or environment-configured paths.
- **No committed secrets**: Never commit `.env`, private keys, passwords, or service account files.
- **Environment config**: Always maintain `.env.example` with clear documentation.
- **Excluded artifacts**:
  - Python: `__pycache__/`, `*.pyc`, `venv/`, `.venv/`
  - Node: `node_modules/`, `dist/`, `.vite/`
  - Flutter: `.dart_tool/`, `build/`, `*.lock` (per team standard), `.flutter-plugins`
  - Database: `*.db`, `*.sqlite`, `*.sqlite3`
  - Credentials: `google-services.json`, `GoogleService-Info.plist`, `*.pem`, `*.key`

---

## 7. Vertical Milestone Development Strategy

The application must be developed in the following strict vertical sequence:

1. **Milestone 1**: Repository & directory scaffolding (`.env.example`, `.gitignore`, baseline structure)
2. **Milestone 2**: Database models & reproducible seed script (`sevasetu.db`, `seed.py`)
3. **Milestone 3**: Authentication system (JWT, password hashing, roles)
4. **Milestone 4**: Core backend REST APIs (Services, Worker profiles, Verification)
5. **Milestone 5**: Flutter application shell & navigation (Role-aware routing)
6. **Milestone 6**: Flutter/Backend integration (Authentication & profile fetch)
7. **Milestone 7**: Service discovery & listing UI
8. **Milestone 8**: Worker matching engine (Haversine distance calculation & filtering)
9. **Milestone 9**: Booking workflow (Creation, dispatch, acceptance/rejection lifecycle)
10. **Milestone 10**: Mapping integration (`flutter_map` + OSM marker rendering)
11. **Milestone 11**: Realtime WebSockets (Live in-app booking state synchronizer)
12. **Milestone 12**: Push notifications (FCM integration with fallback simulator)
13. **Milestone 13**: Admin Web Dashboard (React + Vite cooperative oversight & verification)
14. **Milestone 14**: Ratings, reviews & mock itemized invoice generation
15. **Milestone 15**: AI / Analytics module (Demand forecasting & workforce capacity insights)
16. **Milestone 16**: End-to-end integration testing across all four components
17. **Milestone 17**: Demo polish, seed data verification, and rehearsal preparation

---

## 8. AI Pair-Programming Rules

Before modifying code:
1. Read `AGENTS.md` and check active milestones in `TASKS.md`.
2. Inspect relevant existing files.
3. Understand existing architecture and data flow.
4. Make the smallest reasonable, incremental change.
5. Avoid unnecessary rewrites of functioning code.
6. Run relevant syntax, build, and test checks.
7. Report what changed with full file paths.

Operational rules:
- Do not introduce new technologies without explicit user approval.
- Keep API contracts stable once frontend/mobile integration begins. If a contract changes, update all clients and documentation in the same step.
- When completing a milestone or task:
  - Update `TASKS.md`
  - Update `README.md` if setup instructions changed
  - List all modified files
  - Document verification tests performed
  - Flag any known issues or dependencies

---

## 9. Primary End-to-End Demo Priority

The primary benchmark for success is a smooth, continuous, end-to-end demonstration covering all three user roles:

1. **Customer Flow (Flutter App)**:
   Login ➔ Select service category ➔ Provide location ➔ View nearby verified workers on map ➔ Select worker ➔ Create booking ➔ Receive live acceptance via WebSocket/notification ➔ Track job progress ➔ View completion & mock invoice ➔ Submit rating & review.

2. **Worker Flow (Flutter App)**:
   Login ➔ Receive incoming booking alert ➔ View customer & service location on map ➔ Accept booking ➔ Transition status (`en_route` ➔ `in_progress` ➔ `completed`) ➔ View updated earnings & rating.

3. **Admin Flow (React Web Dashboard)**:
   Login ➔ View cooperative operations overview ➔ Review & verify new workers ➔ Monitor live bookings ➔ Inspect demand analytics and workforce capacity recommendations.
