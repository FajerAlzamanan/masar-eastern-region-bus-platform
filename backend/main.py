"""FastAPI application exposing the DSS backend to the React frontend.

Students should read this file to understand the API contract: each endpoint has
a URL, returns JSON, and is consumed by one or more frontend pages.
"""

import csv
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.bookings import create_booking, list_bookings, update_booking
from backend.eastern_network import EASTERN_ROUTES, ROUTES_BY_CODE, route_allows
from backend.paths import CONFIG_DIR, GENERATED_DIR, ROOT
from backend.pipeline import run_full_pipeline
from backend.scenarios import simulate_scenario
from backend.utils import read_json

app = FastAPI(title="Masar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    phone_number: str = Field(min_length=10, max_length=15)
    role: str
    official_email: str | None = None


class BookingRequest(BaseModel):
    rider_id: str = Field(min_length=10, max_length=10)
    rider_name: str = Field(min_length=2, max_length=80)
    route_code: str
    origin_name: str = Field(min_length=2, max_length=100)
    destination_name: str = Field(min_length=2, max_length=100)
    passenger_count: int = Field(ge=1, le=8)
    assistance: bool = False
    payment_method: str = "mada"


class BookingDecision(BaseModel):
    status: str
    driver_note: str = Field(default="", max_length=180)
    actor_role: str


class ScenarioSimulationRequest(BaseModel):
    scenario_id: str
    saving_factor: float = Field(ge=0.05, le=0.95)


def _read_generated(name: str) -> list[dict]:
    path = GENERATED_DIR / f"{name}.csv"
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


@app.post("/api/auth/login")
def login(payload: LoginRequest):
    """Local identity gateway for the demo product; production replaces this with Nafath."""
    if payload.role not in {"rider", "driver", "station", "ops"}:
        raise HTTPException(status_code=400, detail="Unknown platform role.")
    if not payload.phone_number.isdigit():
        raise HTTPException(status_code=400, detail="رقم الجوال يجب أن يحتوي على أرقام فقط.")
    if payload.role in {"driver", "station", "ops"}:
        email = (payload.official_email or "").strip().lower()
        if not email.endswith("@masar.sa"):
            raise HTTPException(status_code=400, detail="يتطلب هذا الدور بريدًا رسميًا ينتهي بـ @masar.sa.")
    profiles = {
        "rider": "سارة أحمد",
        "driver": "خالد العتيبي",
        "station": "موظف محطة السوق",
        "ops": "مركز التحكم",
    }
    return {"user_id": payload.phone_number, "name": profiles[payload.role], "role": payload.role}


@app.get("/api/transit")
def transit_data():
    return {name: _read_generated(name) for name in ("routes", "stops", "trips", "stop_events")}


@app.get("/api/network")
def eastern_region_network():
    """Map-key route contract used by Masar's booking experience."""
    return {"routes": EASTERN_ROUTES, "fare_sar": 3.45, "city": "المنطقة الشرقية"}


@app.post("/api/bookings")
def book(payload: BookingRequest):
    route = ROUTES_BY_CODE.get(payload.route_code)
    if route is None:
        raise HTTPException(status_code=400, detail="خط الرحلة المختار غير موجود في خريطة المنطقة الشرقية.")
    if not route_allows(route, payload.origin_name, payload.destination_name):
        raise HTTPException(status_code=400, detail="محطتا الانطلاق والوصول لا تتطابقان مع طرفي الخط المختار في الخريطة الرسمية.")
    if payload.payment_method not in {"mada", "apple_pay", "card", "on_board"}:
        raise HTTPException(status_code=400, detail="The selected payment method is unavailable.")
    eta_minutes = 8 if route["type"] == "loop" else 12
    fare_sar = round(3.45 * payload.passenger_count, 2)
    return create_booking({
        **payload.model_dump(),
        "trip_id": payload.route_code,
        "origin_sequence": 1,
        "destination_sequence": 2,
        "assistance": int(payload.assistance),
        "eta_minutes": eta_minutes,
        "fare_sar": fare_sar,
    })


@app.get("/api/bookings")
def bookings(rider_id: str | None = None, status: str | None = None):
    return {"bookings": list_bookings(rider_id=rider_id, status=status)}


@app.patch("/api/bookings/{booking_id}")
def decide_booking(booking_id: str, payload: BookingDecision):
    if payload.actor_role != "driver":
        raise HTTPException(status_code=403, detail="Only a driver can update a passenger request.")
    if payload.status not in {"accepted", "declined", "boarded"}:
        raise HTTPException(status_code=400, detail="Invalid booking status.")
    booking = update_booking(booking_id, payload.status, payload.driver_note)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")
    return booking


@app.get("/")
def api_index():
    """Teaching index for students opening the backend root in a browser."""
    return {
        "name": "Masar API",
        "purpose": "Backend for the Team B guided repo. The frontend reads these endpoints to show the DSS journey.",
        "start_here": {
            "frontend": "http://127.0.0.1:5179",
            "api_docs": "/docs",
            "health": "/api/health",
        },
        "recommended_learning_path": [
            "Open /api/project to see the problem and decision context.",
            "Open /api/data-quality before trusting analysis.",
            "Open /api/kpis to inspect dashboard data.",
            "Open /api/scenarios to compare interventions.",
            "Open /api/recommendation to see the explainable DSS output.",
        ],
        "endpoints": {
            "GET /api/project": "Problem, route, decision owner, scope, and assumptions.",
            "GET /api/roles": "Stakeholder roles and permissions.",
            "GET /api/repo/tree": "Repo folders and files for the frontend file browser.",
            "GET /api/repo/file": "Read one text file safely from inside the repo.",
            "GET /api/data-model": "Tables and relationships.",
            "GET /api/tables/{table_name}": "Live preview rows for one generated table.",
            "POST /api/generate": "Regenerate synthetic training data and outputs.",
            "GET /api/data-quality": "Validation report and quality gate.",
            "GET /api/kpis": "Dashboard KPIs, stop ranking, and delay causes.",
            "GET /api/scenarios": "Scenario comparison results.",
            "GET /api/recommendation": "Recommended action, evidence, confidence, limitations, and next step.",
        },
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Masar API"}


@app.get("/api/project")
def get_project():
    return read_json(CONFIG_DIR / "problem_scope.json")


@app.get("/api/roles")
def get_roles():
    return read_json(CONFIG_DIR / "roles.json")


@app.get("/api/repo/tree")
def get_repo_tree():
    """Expose a safe repo tree so the frontend can teach file navigation."""
    return {"root": ROOT.name, "items": _build_tree(ROOT)}


@app.get("/api/repo/file")
def get_repo_file(path: str):
    """Read one safe text file for the in-app repo browser."""
    target = _safe_repo_path(path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail=f"Unknown file: {path}")
    if target.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".ipynb"}:
        return {
            "path": path,
            "name": target.name,
            "kind": "binary",
            "size_bytes": target.stat().st_size,
            "message": "Binary or notebook file. Open it from the repo directly.",
        }
    return {
        "path": path,
        "name": target.name,
        "kind": "text",
        "size_bytes": target.stat().st_size,
        "content": target.read_text(encoding="utf-8", errors="replace"),
    }


@app.get("/api/data-model")
def get_data_model():
    """Describe generated tables and their relationships for the ERD page."""
    result = run_full_pipeline(write_outputs=True)
    dataset = result["dataset"]
    return {
        "tables": [
            _table_schema(dataset, "routes", "Route identity and bus capacity.", "route_id", [], "Each row describes one bus route used by the DSS."),
            _table_schema(dataset, "stops", "Stop sequence and baseline boarding behavior.", "stop_id", [{"column": "route_id", "references": "routes.route_id"}], "Each row describes one stop on the route."),
            _table_schema(dataset, "trips", "Scheduled trips and final delay.", "trip_id", [{"column": "route_id", "references": "routes.route_id"}], "Each row describes one bus trip from start to finish."),
            _table_schema(
                dataset,
                "stop_events",
                "Stop-level operational events used for analysis.",
                ["trip_id", "stop_id"],
                [
                    {"column": "trip_id", "references": "trips.trip_id"},
                    {"column": "stop_id", "references": "stops.stop_id"},
                ],
                "Each row describes one bus reaching one stop during one trip.",
            ),
        ],
        "relationships": [
            {"from": "routes", "to": "trips", "cardinality": "1:N", "join": "route_id"},
            {"from": "routes", "to": "stops", "cardinality": "1:N", "join": "route_id"},
            {"from": "trips", "to": "stop_events", "cardinality": "1:N", "join": "trip_id"},
            {"from": "stops", "to": "stop_events", "cardinality": "1:N", "join": "stop_id"},
        ],
        "relationship": "routes -> trips -> stop_events <- stops",
    }


@app.get("/api/tables/{table_name}")
def get_table_preview(table_name: str, limit: int = 8):
    """Return a small table sample so students can inspect real generated rows."""
    result = run_full_pipeline(write_outputs=True)
    dataset = result["dataset"]
    if table_name not in dataset:
        raise HTTPException(status_code=404, detail=f"Unknown table: {table_name}")

    frame = dataset[table_name]
    return {
        "table": table_name,
        "row_count": int(len(frame)),
        "columns": list(frame.columns),
        "rows": frame.head(max(1, min(limit, 25))).to_dict(orient="records"),
    }


@app.post("/api/generate")
def generate():
    """Regenerate training data and derived outputs on demand."""
    result = run_full_pipeline(write_outputs=True)
    return {
        "message": "Synthetic dataset generated and outputs refreshed.",
        "tables": {name: len(frame) for name, frame in result["dataset"].items()},
        "synthetic_notice": result["project"]["assumptions"][0],
    }


@app.get("/api/data-quality")
def get_data_quality():
    return run_full_pipeline(write_outputs=True)["validation"]


@app.get("/api/kpis")
def get_kpis():
    return run_full_pipeline(write_outputs=True)["analysis"]


@app.get("/api/scenarios")
def get_scenarios():
    return run_full_pipeline(write_outputs=True)["scenarios"]


@app.post("/api/scenarios/simulate")
def simulate(payload: ScenarioSimulationRequest):
    """Run a user-selected scenario strength against a fresh baseline dataset."""
    result = run_full_pipeline(write_outputs=False)
    configured = read_json(CONFIG_DIR / "scenarios.json")["scenarios"]
    scenario = next((item for item in configured if item["scenario_id"] == payload.scenario_id), None)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Scenario not found.")
    custom = {**scenario, "saving_factor": payload.saving_factor}
    return simulate_scenario(result["dataset"], custom, read_json(CONFIG_DIR / "kpi_config.json"))


@app.get("/api/recommendation")
def get_recommendation():
    return run_full_pipeline(write_outputs=True)["recommendation"]


def _table_schema(dataset, name, purpose, primary_key, foreign_keys, grain):
    """Build a compact schema object from a generated DataFrame."""
    frame = dataset[name]
    return {
        "name": name,
        "purpose": purpose,
        "grain": grain,
        "row_count": int(len(frame)),
        "primary_key": primary_key,
        "foreign_keys": foreign_keys,
        "columns": [
            {
                "name": column,
                "type": str(frame[column].dtype),
                "nullable": bool(frame[column].isna().any()),
            }
            for column in frame.columns
        ],
    }


def _build_tree(path):
    """Build a nested file tree while hiding local caches and virtual envs."""
    excluded = {".git", "__pycache__", ".pytest_cache", "node_modules", "dist", ".venv", "venv"}
    children = []
    for child in sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name.lower())):
        if child.name in excluded or child.name.endswith(".pyc"):
            continue
        if child.is_dir():
            children.append(
                {
                    "name": child.name,
                    "path": child.relative_to(ROOT).as_posix(),
                    "type": "folder",
                    "children": _build_tree(child),
                }
            )
        else:
            children.append(
                {
                    "name": child.name,
                    "path": child.relative_to(ROOT).as_posix(),
                    "type": "file",
                    "size_bytes": child.stat().st_size,
                }
            )
    return children


def _safe_repo_path(path):
    """Prevent the browser endpoint from reading files outside this repo."""
    target = (ROOT / path).resolve()
    if ROOT not in target.parents and target != ROOT:
        raise HTTPException(status_code=400, detail="Path is outside the repo.")
    return target
