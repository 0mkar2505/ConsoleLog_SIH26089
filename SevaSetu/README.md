# Console Log (PS 26089)
> **Cooperative Service Allocation & Dispatch Platform for Household & Community Services**  
> **Team**: Console Log  

---

## 1. Product Concept & Vision

**Console Log** is a **cooperative service allocation and dispatch platform** connecting customers with local cooperative workers while supporting multi-tiered digital access.

Unlike aggregator gig marketplaces where customers select workers from a generic list, Console Log solves the core technical challenge of **allocating community workforce capacity to customer demand**.

The platform intelligently considers:
- Service & skill match
- Worker availability & schedule
- Worker workload
- Geographic distance & estimated travel time
- Verification status
- Cooperative operational area
- Worker digital communication method (Digital-First vs Low-Digital-Access)

The platform supports both:
1. **Immediate / On-Demand Service Requests**: Fast dispatch based on proximity, skills, and current availability (e.g., "My car broke down").
2. **Scheduled Service Requests**: Calendar-aware booking considering worker capacity, travel buffers, and preferred customer time windows (e.g., "I need a plumber tomorrow at 5 PM").

---

## 2. Four Participant Interfaces

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

1. **Customer Interface (`mobile/`)**:
   - Single Flutter mobile application with role-based UI.
   - Self-registration, address management (Lat/Lon + Human Readable Address + Landmark + Additional Directions).
   - Immediate dispatch requests & Scheduled booking requests with flexibility windows.
   - Live assignment tracking, notifications, history, and service ratings.

2. **Digital-First Worker Interface (`mobile/`)**:
   - Integrated into the Flutter mobile application.
   - Manages skills, service radius, and online/offline availability.
   - Receives job dispatches, views customer location/address, navigates via `flutter_map` + OSM, and updates job status (`en_route` -> `in_progress` -> `completed`).

3. **Low-Digital-Access Worker Interface (`SMS / Voice`)**:
   - Designed for workers without smartphones, mobile data, or app access.
   - Operates via standard SMS text messaging on standard cellular phones.
   - Receives complete plaintext job dispatch details (Job ID, service, customer name/phone, address, landmark, directions, time, status, description).
   - Responds via simple SMS reply (`1 = ACCEPT`, `2 = REJECT`). Does **NOT** assume web URLs or continuous GPS.

4. **Admin / Cooperative Dashboard (`dashboard/`)**:
   - React + Vite web application reserved for cooperative administrators.
   - Manages worker verification, skills, service catalog, booking monitoring, community capacity, and demand analytics.

---

## 3. Core Backend Architecture

The backend (Python / FastAPI / PyMongo / Pydantic v2) acts as the central source of truth and houses seven core logical engines:
- **Dispatch Engine**: Handles immediate, real-time service requests.
- **Scheduling Engine**: Handles future calendar bookings & time-window flexibilities.
- **Availability Engine**: Evaluates true worker schedule capacity ("Can this community satisfy this request?").
- **Matching Engine**: Multi-factor worker matching algorithm.
- **Notification Service**: WebSockets for live in-app state synchronizing and FCM for background alerts.
- **Communication / SMS Service**: SMS gateway integration with local mock fallback.
- **Analytics Engine**: Demand forecasting and labor shortage advisory insights for cooperatives.

MongoDB (via PyMongo) is the sole database persistence layer. Neither Flutter nor React directly queries MongoDB.

---

## 4. Repository Structure

```text
SevaSetu/
├── AGENTS.md                  # Project constitution & architecture specifications
├── TASKS.md                   # Vertical roadmap and milestone status log
├── README.md                  # System overview and setup guide (this file)
├── .env.example               # Environment variables template
│
├── mobile/                    # Component 1 & 2: Flutter Mobile App (Customer + Worker)
│   ├── pubspec.yaml
│   ├── lib/
│   │   ├── main.dart
│   │   ├── config/            # App constants, routes, theme
│   │   ├── models/            # Customer & Worker models
│   │   ├── services/          # REST API, WebSocket, and FCM services
│   │   └── screens/           # Customer & Digital Worker screens
│   └── test/
│
├── backend/                   # Central FastAPI Backend API
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # FastAPI entry point & WebSocket hub
│   │   ├── database.py        # PyMongo client & index initialization
│   │   ├── seed.py            # Idempotent MongoDB seed data script
│   │   ├── models/            # Document schema definitions
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── routers/           # API routes
│   │   └── services/          # Core logical engines (Dispatch, Scheduling, SMS, etc.)
│   └── tests/
│
├── dashboard/                 # Component 4: React Admin Web Dashboard (Vite)
│   ├── package.json
│   ├── vite.config.js
│   └── src/                   # Cooperative management & analytics UI
│
├── ml/                        # Intelligence & Advisory Analytics Module
│   └── forecasting/           # Demand forecasting & capacity heuristics
│
└── data/                      # Shared seed JSONs and datasets
```

---

## 5. Required Software & Setup

| Tool | Recommended Version | Verification Command |
| :--- | :--- | :--- |
| **Python** | `3.12.x` | `python --version` |
| **Node.js** | `22.x` (or LTS) | `node -v` |
| **npm** | `10.x+` / `11.x+` | `npm -v` |
| **Flutter** | `3.24.x+` | `flutter --version` |
| **MongoDB** | `6.x` / `7.x` | Service running on port `27017` |

### Environment Configuration
```powershell
copy .env.example .env
```

### Running Backend (FastAPI)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Seeding Database
```powershell
python -m app.seed
```

### Running Admin Dashboard (React + Vite)
```powershell
cd dashboard
npm install
npm run dev
```

### Running Mobile App (Flutter)
```powershell
cd mobile
flutter pub get
flutter run -d windows  # or -d chrome / -d android
```

---

## 6. Key Constraints
- **Database**: MongoDB with PyMongo only. No SQLite, SQLAlchemy, or PostgreSQL.
- **Mapping**: `flutter_map` + OpenStreetMap (No paid Google Maps).
- **Communication**: FCM/WebSockets for digital workers; SMS gateway (with mock mode) for low-digital workers.
- **Payments**: Fully mocked for hackathon MVP.
