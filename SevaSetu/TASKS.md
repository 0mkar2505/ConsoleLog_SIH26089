# Milestone & Task Tracker: Console Log (PS 26089)

## Foundation & Central Backend:
- [x] Repository scaffold & architecture realignment (Console Log)
- [x] MongoDB database layer (PyMongo + 2dsphere indexing)
- [ ] Authentication & Role-Based Access Control (Customer, Worker, Admin)
- [ ] Core Data Schemas (Users, Workers, Services, Bookings, Ratings, Invoices)

## Core Backend Engines:
- [ ] Dispatch Engine (Immediate service requests & proximity/workload dispatch)
- [ ] Scheduling Engine (Calendar bookings & time flexibility window management)
- [ ] Availability Engine (Worker schedule capacity & community-level availability)
- [ ] Matching Engine (Multi-factor algorithmic allocation considering skills, distance, workload)
- [ ] Communication & SMS Service (Low-digital-access SMS gateway abstraction & mock gateway)
- [ ] Notification Service (WebSockets hub for live state sync & FCM background alerts)
- [ ] Analytics Engine (Demand forecasting & workforce shortage advisory)

## Interface 1: Customer (Flutter Mobile App):
- [ ] Customer authentication & profile management
- [ ] Address manager (Lat/Lon + Human Readable Address + Landmark + Directions)
- [ ] Immediate problem report flow ("My car broke down")
- [ ] Scheduled booking flow ("Plumber tomorrow 5 PM") with flexibility windows (exact, ±30m, ±1h)
- [ ] Live assignment & status tracking (`pending` -> `accepted` -> `en_route` -> `in_progress` -> `completed`)
- [ ] Map rendering (`flutter_map` + OpenStreetMap)
- [ ] Service history, mock invoice viewing, & ratings submission

## Interface 2: Digital-First Worker (Flutter Mobile App):
- [ ] Worker role authentication & cooperative onboarding
- [ ] Skills, service area, & availability toggle (`online`/`offline`)
- [ ] Job offer reception with customer address, location & problem description
- [ ] Job offer acceptance / rejection interface
- [ ] Navigation map view & job status workflow updates
- [ ] Upcoming scheduled jobs calendar & completed job history

## Interface 3: Low-Digital-Access Worker (SMS / Voice):
- [ ] Worker phone number registration with cooperative profile
- [ ] Plaintext SMS job dispatch generator (Job ID, customer name, phone, full address, landmark, directions, requested time, problem description)
- [ ] Inbound SMS webhook parser for text replies (`1 = ACCEPT`, `2 = REJECT`)
- [ ] Interactive mock SMS simulator interface for local dev & testing
- [ ] Direct customer call trigger fallback handling

## Interface 4: Admin / Cooperative Dashboard (React + Vite):
- [ ] Admin login & cooperative management
- [ ] Worker registration review, credential inspection, & skill verification
- [ ] Live booking monitoring & operational dispatch overview
- [ ] Customer records and service history review
- [ ] Community workforce capacity monitoring & demand forecasting charts

## Intelligence & Analytics (`ml/`):
- [ ] Synthetic community demand & workforce dataset
- [ ] Demand forecasting by location and service category
- [ ] Workforce capacity & shortage prediction algorithms
- [ ] Cooperative staffing advisory recommendations

## Verification & Demo Rehearsal:
- [ ] End-to-end multi-role integration testing (Customer app -> Dispatch engine -> Digital worker app & Low-digital SMS -> Admin dashboard)
- [ ] Error handling & graceful fallback validation (mock SMS & FCM)
- [ ] Rehearsal & demonstration preparation
