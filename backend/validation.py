"""Data-quality checks used before analysis and recommendation."""

from typing import Any

import pandas as pd


def validate_dataset(dataset: dict[str, pd.DataFrame], rules: dict[str, Any]) -> dict[str, Any]:
    """Validate generated data before analysis.

    Teaching note:
    A DSS should fail safely. If the data does not pass quality checks, the
    system should block recommendation instead of producing confident nonsense.
    """
    checks = []
    expected_tables = {"routes", "stops", "trips", "stop_events"}
    checks.append(
        _check(
            "required_tables",
            expected_tables.issubset(dataset.keys()),
            "All expected tables exist.",
            "Identity and completeness",
            failed_row_count=len(expected_tables.difference(dataset.keys())),
        )
    )

    # Pull tables defensively so validation can report failure instead of
    # crashing when a table is missing during student experiments.
    events = dataset.get("stop_events", pd.DataFrame())
    trips = dataset.get("trips", pd.DataFrame())
    stops = dataset.get("stops", pd.DataFrame())
    has_trip_keys = "trip_id" in events and "trip_id" in trips
    has_stop_keys = "stop_id" in events and "stop_id" in stops

    missing_trip_refs = (
        len(events)
        if not events.empty and not has_trip_keys
        else 0
        if events.empty
        else int((~events["trip_id"].isin(set(trips["trip_id"]))).sum())
    )
    checks.append(
        _check(
            "valid_trip_references",
            missing_trip_refs == 0,
            "Every stop event references an existing trip.",
            "Foreign keys",
            failed_row_count=missing_trip_refs,
        )
    )
    missing_stop_refs = (
        len(events)
        if not events.empty and not has_stop_keys
        else 0
        if events.empty
        else int((~events["stop_id"].isin(set(stops["stop_id"]))).sum())
    )
    checks.append(
        _check(
            "valid_stop_references",
            missing_stop_refs == 0,
            "Every stop event references an existing stop.",
            "Foreign keys",
            failed_row_count=missing_stop_refs,
        )
    )

    numeric_cols = ["dwell_time_sec", "added_delay_sec", "cumulative_delay_sec", "passenger_load"]
    # Negative time or passenger load is a data problem, not a UI problem.
    negative_masks = [(events[col] < 0) for col in numeric_cols if col in events]
    failed_negative_rows = int(pd.concat(negative_masks, axis=1).any(axis=1).sum()) if negative_masks else 0
    checks.append(
        _check(
            "non_negative_time",
            failed_negative_rows == 0,
            "Time, load, and delay values are not negative.",
            "Time and numeric values",
            failed_row_count=failed_negative_rows,
        )
    )

    capacity_ok = events.empty or (events["passenger_load"] <= events["bus_capacity"]).all()
    checks.append(
        _check(
            "capacity_not_exceeded",
            capacity_ok,
            "Passenger load does not exceed bus capacity.",
            "Passenger capacity",
            severity="warning",
            failed_row_count=0 if events.empty else int((events["passenger_load"] > events["bus_capacity"]).sum()),
        )
    )

    ordered = True
    unordered_trip_count = 0
    if not events.empty:
        # A trip should move through stops in sequence. This protects analysis
        # that depends on cumulative delay over the route.
        for _, group in events.sort_values(["trip_id", "sequence"]).groupby("trip_id"):
            if not group["sequence"].is_monotonic_increasing:
                ordered = False
                unordered_trip_count += 1
                break
    checks.append(
        _check(
            "ordered_stop_sequence",
            ordered,
            "Stop sequence increases within each trip.",
            "Stop sequence",
            failed_row_count=unordered_trip_count,
        )
    )

    passed = sum(1 for check in checks if check["passed"])
    score = round(passed / len(checks), 2)
    passing_score = rules["passing_score"]

    return {
        "quality_score": score,
        "passing_score": passing_score,
        "passed": score >= passing_score and all(c["passed"] for c in checks if c["severity"] == "critical"),
        "passed_checks": passed,
        "failed_checks_count": len([check for check in checks if not check["passed"]]),
        "analysis_gate": "allowed"
        if score >= passing_score and all(c["passed"] for c in checks if c["severity"] == "critical")
        else "blocked",
        "checks": checks,
        "failed_checks": [check for check in checks if not check["passed"]],
    }


def _check(
    check_id: str,
    passed: bool,
    message: str,
    category: str,
    severity: str = "critical",
    failed_row_count: int = 0,
) -> dict[str, Any]:
    """Return one normalized quality-check result for the API."""
    return {
        "id": check_id,
        "passed": bool(passed),
        "category": category,
        "severity": severity,
        "failed_row_count": failed_row_count,
        "message": message,
    }
