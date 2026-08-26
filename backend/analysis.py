"""KPI and evidence calculations for the Bus Delay DSS.

This file is where generated operational records become decision signals. The
frontend should read these outputs from the API instead of recalculating the
same formulas in React.
"""

from typing import Any

import pandas as pd


def analyze_dataset(dataset: dict[str, pd.DataFrame], kpi_config: dict[str, Any]) -> dict[str, Any]:
    """Calculate dashboard KPIs and supporting evidence tables."""
    trips = dataset["trips"]
    events = dataset["stop_events"]
    threshold = kpi_config["on_time_threshold_sec"]

    # Stop-level grouping answers: where is delay accumulating most often?
    stop_summary = (
        events.groupby(["stop_id", "stop_name"], as_index=False)
        .agg(
            avg_added_delay_sec=("added_delay_sec", "mean"),
            avg_dwell_excess_sec=("dwell_excess_sec", "mean"),
            avg_passenger_load=("passenger_load", "mean"),
            peak_events=("is_peak", "sum"),
        )
        .sort_values("avg_added_delay_sec", ascending=False)
    )

    worst_stop = stop_summary.iloc[0].to_dict()

    # Cause-level grouping answers: what operational issue appears most costly?
    cause_summary = (
        events.groupby("delay_cause", as_index=False)
        .agg(total_added_delay_sec=("added_delay_sec", "sum"), events=("trip_id", "count"))
        .sort_values("total_added_delay_sec", ascending=False)
    )

    return {
        "kpis": {
            "trips_analyzed": int(len(trips)),
            "on_time_rate": round(float((trips["final_delay_sec"] <= threshold).mean()), 2),
            "avg_final_delay_sec": round(float(trips["final_delay_sec"].mean()), 1),
            "avg_dwell_time_sec": round(float(events["dwell_time_sec"].mean()), 1),
            "worst_stop": worst_stop["stop_name"],
            "worst_stop_id": worst_stop["stop_id"],
        },
        "stop_summary": _records(stop_summary),
        "cause_summary": _records(cause_summary),
        "trip_summary": _records(trips.sort_values("final_delay_sec", ascending=False).head(10)),
    }


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert DataFrame rows into JSON-friendly dictionaries for the API."""
    return frame.round(2).to_dict(orient="records")
