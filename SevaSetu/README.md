# SevaSetu (PS 26089)
> **Cooperative Gig Services Platform for Household & Community Services**  
> **Team**: Null Value  
> **Hackathon MVP**: 12-Hour Vertical Milestone Prototype

---

## 1. Project Purpose
**SevaSetu** is a cooperative-driven digital platform designed to empower informal gig workers and provide households with verified, fair-priced local services. Unlike predatory commercial aggregator platforms, SevaSetu operates on a cooperative model where:
- Workers retain fair compensation with transparent cooperative fund margins.
- Customers access verified local service providers matched by geographic proximity.
- Cooperative administrators monitor community demand, verify credentials, and receive data-driven workforce recommendations.

---

## 2. Platform Architecture

The system is composed of **four coordinated components**:

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

1. **Mobile Application (`mobile/`)**: Flutter-based multi-role mobile application serving both Customers and Workers.
2. **Backend API (`backend/`)**: FastAPI REST and WebSocket application enforcing business rules, authentication, and geospatial proximity calculations.
3. **Admin Web Dashboard (`dashboard/`)**: React + Vite application dedicated exclusively to cooperative oversight, worker verification, and analytics.
4. **AI & Analytics (`ml/`)**: Modular Python forecasting and workforce capacity recommendation toolkit.

---

## 3. Repository Structure

```text
SevaSetu/
├── AGENTS.md                  # Project constitution & development rules
├── TASKS.md                   # Vertical milestone roadmap and status tracker
├── README.md                  # System overview and setup guide (this file)
├── .gitignore                 # Version control exclusions
├── .env.example               # Environment variables template
│
├── mobile/                    # Component 1: Flutter mobile app (Customer + Worker)
│   ├── pubspec.yaml
│   ├── lib/
│   │   └── main.dart
│   └── test/
│
├── backend/                   # Component 2: FastAPI central backend
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # FastAPI entry point & health check
│   │   ├── database.py        # SQLAlchemy SQLite engine
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API routes
│   │   ├── services/          # Haversine matching & core logic
│   │   ├── utils/             # Helpers & security
│   │   └── seed.py            # Reproducible database seed script
│   └── tests/
│
├── dashboard/                 # Component 3: React Admin Dashboard (Vite)
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── index.css
│
├── ml/                        # Component 4: AI & Analytics module
│   ├── data/                  # Synthetic training datasets
│   ├── models/                # Trained model artifacts
│   ├── training/              # Training scripts
│   ├── forecasting/           # Demand & workforce heuristics
│   └── requirements.txt
│
├── data/                      # Shared seed JSONs and sample files
└── docs/                      # Technical specifications and architecture documentation
```

---

## 4. Required Software & Runtime Versions

To build and run the complete platform, ensure your development machine has the following tools installed:

| Tool | Recommended Version | Verification Command |
| :--- | :--- | :--- |
| **Python** | `3.12.x` | `py -3.12 --version` or `python --version` |
| **Node.js** | `22.x` (or current LTS) | `node -v` |
| **npm** | `10.x+` or `11.x+` | `npm -v` |
| **Flutter** | `3.24.x+` (stable channel) | `flutter --version` |
| **Dart** | Bundled with Flutter (`3.5.x+`) | `dart --version` |
| **Git** | `2.x+` | `git --version` |

---

## 5. Clone & Setup Guide (Fresh Windows Machine)

### Step 0: Clone the Repository
```powershell
git clone https://github.com/0mkar2505/ConsoleLog_SIH26089.git
cd ConsoleLog_SIH26089\SevaSetu
```

### Step 1: Environment Configuration
Copy the template configuration file:
```powershell
copy .env.example .env
```
*(Do not commit your `.env` file to Git.)*

---

## 6. Component Setup & Execution

### A. Backend (FastAPI) Setup & Run

1. Navigate to the `backend/` directory:
   ```powershell
   cd backend
   ```
2. Create and activate a dedicated Python 3.12 virtual environment:
   ```powershell
   py -3.12 -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
5. Verify health endpoint in your browser or terminal:
   - **Healthcheck**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
   - **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### B. Dashboard (React + Vite) Setup & Run

1. Navigate to the `dashboard/` directory:
   ```powershell
   cd ..\dashboard
   ```
2. Install npm dependencies:
   ```powershell
   npm install
   ```
3. Run the Vite development server:
   ```powershell
   npm run dev
   ```
4. Access the dashboard at:
   - [http://localhost:5173](http://localhost:5173)
5. To test a production build:
   ```powershell
   npm run build
   ```

---

### C. Mobile App (Flutter) Setup & Run

1. Navigate to the `mobile/` directory:
   ```powershell
   cd ..\mobile
   ```
2. Fetch Flutter packages:
   ```powershell
   flutter pub get
   ```
3. Run code analysis and widget smoke tests:
   ```powershell
   flutter analyze
   flutter test
   ```
4. Launch the application:
   - On Windows desktop (for rapid UI development):
     ```powershell
     flutter run -d windows
     ```
   - On an Android Emulator / physical device:
     ```powershell
     flutter run -d android
     ```
   - In Chrome (web preview):
     ```powershell
     flutter run -d chrome
     ```

---

### D. AI & Analytics Module (`ml/`) Setup

1. Navigate to the `ml/` directory:
   ```powershell
   cd ..\ml
   ```
2. Create and activate a virtual environment (or use backend's environment):
   ```powershell
   py -3.12 -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

---

## 7. Development Guidelines & Constraints
- **Database**: SQLite (`sevasetu.db`) with automated schema generation and reproducible `seed.py`. Never commit database files to Git.
- **Security**: Mocked payments; JWT authentication; no hardcoded credentials.
- **Prohibitions**: Strictly no real payment gateways, no external paid map APIs, and no microservices.
