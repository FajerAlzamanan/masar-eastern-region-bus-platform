# Masar | مسار

Masar is a bilingual urban bus reservation and operations platform for the Eastern Region of Saudi Arabia. It connects riders, drivers, station staff, and the operations center through one FastAPI service and React web application.

## Platform Capabilities

- Public home page with Eastern Region Bus branding, official network map, service information, and partner acknowledgements.
- Role-based sign-in for riders, drivers, station staff, and operations personnel.
- Map-validated booking: every booking is checked against the official Eastern Region route termini.
- Fixed fare of `3.45 SAR` per passenger, with Mada, Apple Pay, card, and pay-at-boarding flows.
- Shared booking workflow: rider requests appear for drivers, who can accept, decline, and mark passengers as boarded.
- Operations Center with live booking KPIs, dataset exploration, data-quality checks, scenario simulation, recommendation, and database relationship diagram.

## Roles

| Role | Access |
| --- | --- |
| Rider | Select an official route, review origin and destination, choose payment, and track requests. |
| Driver | Review shared passenger requests and update their status. |
| Station staff | Review network and passenger-service requests. A Masar official email and phone number are required. |
| Operations | Access the full Operations Center, including the DSS dataset and simulations. A Masar official email and phone number are required. |

## Eastern Region Network

Masar uses the official network key for these services:

`A2`, `A3`, `B2`, `C31`, `C32`, `D4`, `E5`, `F6`, `G7`, `H8`, and `K9`.

The booking API verifies that the selected origin and destination match the termini of the selected line. Circular line `B2` is handled as a loop service.

## Operations Center

The Operations Center combines the original DSS services with Masar's live booking workflow:

- KPI dashboard: on-time rate, average delay, worst stop, causes of delay, and current booking activity.
- Data Quality Gate: validation checks for tables, relationships, non-negative values, capacity, and stop order.
- Data Model: relationship diagram for `routes`, `stops`, `trips`, and `stop_events`.
- Dataset Explorer: select a table and inspect its live generated rows and columns.
- Dataset Generator: regenerate the synthetic DSS dataset from the configured generation rules.
- Scenario Lab: choose an intervention, adjust its strength, run a server-side simulation, and inspect its impact on delay, confidence, action score, and affected rows.
- Recommendation: review the explainable recommended action, evidence, confidence, limitations, and next step.

> The DSS dataset is synthetic training data for the original B12 delay-analysis model. It is explicitly separated from the official Eastern Region booking map.

## Architecture

```text
React frontend
    |
    +-- Booking and role workspaces
    +-- Operations Center
    |
FastAPI backend
    |
    +-- Eastern Region route validation
    +-- SQLite booking store
    +-- Dataset generation and validation
    +-- KPI analysis and scenario simulation
    |
Generated DSS data and configuration
```

## Project Structure

```text
backend/        FastAPI application, booking store, DSS logic, and simulations
config/         Dataset, KPI, validation, and scenario configuration
data/           Generated and sample datasets
frontend/       React and Vite web application
notebooks/      Data-analysis learning notebooks
tests/          Backend validation and pipeline tests
docs/           Project documentation and report material
```

## Run Locally

### Backend

```bash
cd /Users/fajermohammed/Downloads/Masar
venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd /Users/fajermohammed/Downloads/Masar/frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173).

## Key API Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /api/network` | Official Eastern Region route contract and fare. |
| `POST /api/auth/login` | Role-based local sign-in. |
| `POST /api/bookings` | Create a route-validated boarding request. |
| `GET /api/bookings` | Read rider or shared operations bookings. |
| `PATCH /api/bookings/{id}` | Driver decision and boarding update. |
| `GET /api/kpis` | DSS KPI analysis. |
| `GET /api/data-quality` | Dataset validation results. |
| `GET /api/data-model` | Table schemas and relationships. |
| `GET /api/tables/{table_name}` | Live table preview. |
| `POST /api/generate` | Regenerate the synthetic DSS dataset. |
| `GET /api/scenarios` | Configured scenario comparison. |
| `POST /api/scenarios/simulate` | Run a custom scenario strength simulation. |
| `GET /api/recommendation` | Explainable operational recommendation. |

## Verification

```bash
cd /Users/fajermohammed/Downloads/Masar/frontend
npm run build
```

For backend checks:

```bash
cd /Users/fajermohammed/Downloads/Masar
venv/bin/python -m pytest
```
