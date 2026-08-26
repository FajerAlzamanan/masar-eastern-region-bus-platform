"""What-if scenario simulation for operational interventions."""

from typing import Any

import pandas as pd

from backend.analysis import analyze_dataset


def run_scenarios(
    dataset: dict[str, pd.DataFrame], scenarios_config: dict[str, Any], kpi_config: dict[str, Any]
) -> list[dict[str, Any]]:
    """Compare configured interventions against the baseline dataset."""
    baseline = analyze_dataset(dataset, kpi_config)["kpis"]
    baseline_events = dataset["stop_events"]
    dwell_threshold = kpi_config.get("dwell_excess_threshold_sec", 45)
    results = []

    for scenario in scenarios_config["scenarios"]:
        # A scenario changes stop_events, then recalculates trip-level delay so
        # every result is comparable with the baseline KPI.
        adjusted = _apply_scenario(dataset["stop_events"], scenario)
        scenario_dataset = {**dataset, "stop_events": adjusted, "trips": _recalculate_trips(dataset["trips"], adjusted)}
        scenario_kpis = analyze_dataset(scenario_dataset, kpi_config)["kpis"]
        improvement = baseline["avg_final_delay_sec"] - scenario_kpis["avg_final_delay_sec"]
        confidence = _confidence_score(improvement, scenario["feasibility"], scenario["cost_factor"])
        action_score = round((max(improvement, 0) * scenario["feasibility"] * confidence) / scenario["cost_factor"], 2)
        target_mask = baseline_events["stop_id"] == scenario["target_stop_id"]
        adjusted_target = adjusted[target_mask]
        baseline_target = baseline_events[target_mask]
        affected = _affected_rows(baseline_events, adjusted, scenario["target_stop_id"])

        results.append(
            {
                "scenario_id": scenario["scenario_id"],
                "name": scenario["name"],
                "description": scenario["description"],
                "target_stop_id": scenario["target_stop_id"],
                "target_stop_name": _target_stop_name(dataset["stops"], scenario["target_stop_id"]),
                "intervention_strength": scenario["saving_factor"],
                "cost_level": _cost_level(scenario["cost_factor"]),
                "baseline_avg_delay_sec": baseline["avg_final_delay_sec"],
                "scenario_avg_delay_sec": scenario_kpis["avg_final_delay_sec"],
                "baseline_dwell_sec": round(float(baseline_target["dwell_time_sec"].mean()), 1),
                "scenario_dwell_sec": round(float(adjusted_target["dwell_time_sec"].mean()), 1),
                "baseline_excessive_dwell_rate": round(float((baseline_target["dwell_excess_sec"] > dwell_threshold).mean()), 2),
                "scenario_excessive_dwell_rate": round(float((adjusted_target["dwell_excess_sec"] > dwell_threshold).mean()), 2),
                "affected_trips": int(affected["trip_id"].nunique()),
                "improvement_sec": round(improvement, 1),
                "confidence": confidence,
                "cost_factor": scenario["cost_factor"],
                "feasibility": scenario["feasibility"],
                "action_score": action_score,
                "assumptions": _scenario_assumptions(scenario),
                "affected_rows": _records(affected.head(6)),
            }
        )

    return sorted(results, key=lambda item: item["action_score"], reverse=True)


def simulate_scenario(
    dataset: dict[str, pd.DataFrame], scenario: dict[str, Any], kpi_config: dict[str, Any]
) -> dict[str, Any]:
    """Run one user-configured what-if simulation without mutating baseline data."""
    baseline = analyze_dataset(dataset, kpi_config)["kpis"]
    baseline_events = dataset["stop_events"]
    adjusted = _apply_scenario(baseline_events, scenario)
    scenario_dataset = {**dataset, "stop_events": adjusted, "trips": _recalculate_trips(dataset["trips"], adjusted)}
    scenario_kpis = analyze_dataset(scenario_dataset, kpi_config)["kpis"]
    improvement = baseline["avg_final_delay_sec"] - scenario_kpis["avg_final_delay_sec"]
    confidence = _confidence_score(improvement, scenario["feasibility"], scenario["cost_factor"])
    action_score = round((max(improvement, 0) * scenario["feasibility"] * confidence) / scenario["cost_factor"], 2)
    affected = _affected_rows(baseline_events, adjusted, scenario["target_stop_id"])
    return {
        "scenario_id": scenario["scenario_id"],
        "name": scenario["name"],
        "target_stop_id": scenario["target_stop_id"],
        "target_stop_name": _target_stop_name(dataset["stops"], scenario["target_stop_id"]),
        "intervention_strength": scenario["saving_factor"],
        "baseline_avg_delay_sec": baseline["avg_final_delay_sec"],
        "scenario_avg_delay_sec": scenario_kpis["avg_final_delay_sec"],
        "improvement_sec": round(improvement, 1),
        "confidence": confidence,
        "action_score": action_score,
        "affected_trips": int(affected["trip_id"].nunique()),
        "affected_rows": _records(affected.head(8)),
        "assumptions": _scenario_assumptions(scenario),
    }


def _apply_scenario(events: pd.DataFrame, scenario: dict[str, Any]) -> pd.DataFrame:
    """Apply one intervention to stop-level events without mutating baseline data."""
    adjusted = events.copy()
    float_columns = ["dwell_time_sec", "dwell_excess_sec", "added_delay_sec", "cumulative_delay_sec"]
    adjusted[float_columns] = adjusted[float_columns].astype(float)
    mask = adjusted["stop_id"] == scenario["target_stop_id"]
    saving = adjusted.loc[mask, "issue_wait_sec"] * scenario["saving_factor"]
    adjusted.loc[mask, "dwell_time_sec"] = (adjusted.loc[mask, "dwell_time_sec"] - saving).clip(lower=0)
    adjusted.loc[mask, "dwell_excess_sec"] = (
        adjusted.loc[mask, "dwell_time_sec"] - adjusted.loc[mask, "expected_dwell_sec"]
    ).clip(lower=0)
    adjusted.loc[mask, "added_delay_sec"] = (adjusted.loc[mask, "added_delay_sec"] - saving).clip(lower=0)
    adjusted["cumulative_delay_sec"] = adjusted.groupby("trip_id")["added_delay_sec"].cumsum()
    return adjusted


def _recalculate_trips(trips: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Rebuild trip final delay from the last stop_event in each trip."""
    final_delay = events.sort_values("sequence").groupby("trip_id").tail(1)[["trip_id", "cumulative_delay_sec"]]
    recalculated = trips.drop(columns=["final_delay_sec"]).merge(final_delay, on="trip_id")
    return recalculated.rename(columns={"cumulative_delay_sec": "final_delay_sec"})


def _confidence_score(improvement: float, feasibility: float, cost_factor: float) -> float:
    """Produce a simple confidence signal for teaching scenario comparison."""
    if improvement <= 0:
        return 0.2
    return round(min(0.95, 0.45 + feasibility * 0.35 + min(improvement / 600, 0.2) - cost_factor * 0.03), 2)


def _target_stop_name(stops: pd.DataFrame, stop_id: str) -> str:
    """Look up the human-readable stop name used by the frontend labels."""
    matches = stops.loc[stops["stop_id"] == stop_id, "stop_name"]
    if matches.empty:
        return stop_id
    return str(matches.iloc[0])


def _cost_level(cost_factor: float) -> str:
    """Convert a numeric cost factor into a simple label for the Scenario Lab UI."""
    if cost_factor >= 2:
        return "High"
    if cost_factor >= 1.5:
        return "Medium"
    return "Low"


def _scenario_assumptions(scenario: dict[str, Any]) -> list[str]:
    """Return visible assumptions so simulated results are not mistaken for measured truth."""
    name = scenario["name"]
    common = [
        "Synthetic training data only.",
        "Baseline remains unchanged; scenario runs on a copied stop_events table.",
        f"saving_factor = {scenario['saving_factor']}",
    ]
    if name == "Schedule Adjustment":
        return [
            "Improves schedule compliance without reducing actual passenger time.",
            "No road-speed change is assumed.",
            *common,
        ]
    if name == "Additional Bus":
        return [
            "Extra capacity is available during peak periods.",
            "Operational staffing and dispatching are feasible.",
            *common,
        ]
    if name == "Ticket Machine":
        return [
            "Passengers use the payment option enough to reduce boarding delay.",
            "The intervention mainly affects dwell time at the target stop.",
            *common,
        ]
    return [
        "Staff organization reduces waiting and boarding friction at the target stop.",
        "The intervention mainly affects issue_wait_sec and dwell_time_sec.",
        *common,
    ]


def _affected_rows(baseline_events: pd.DataFrame, adjusted_events: pd.DataFrame, target_stop_id: str) -> pd.DataFrame:
    """Build a small before/after table for the rows changed by the scenario."""
    columns = ["trip_id", "stop_id", "added_delay_sec"]
    before = baseline_events.loc[baseline_events["stop_id"] == target_stop_id, columns].copy()
    after = adjusted_events.loc[adjusted_events["stop_id"] == target_stop_id, columns].copy()
    merged = before.merge(after, on=["trip_id", "stop_id"], suffixes=("_before", "_after"))
    merged["improvement_sec"] = merged["added_delay_sec_before"] - merged["added_delay_sec_after"]
    merged = merged[merged["improvement_sec"] > 0].sort_values("improvement_sec", ascending=False)
    merged["reason"] = "target stop delay reduced by scenario"
    return merged.rename(
        columns={
            "added_delay_sec_before": "before_delay_sec",
            "added_delay_sec_after": "after_delay_sec",
        }
    )[["trip_id", "stop_id", "before_delay_sec", "after_delay_sec", "improvement_sec", "reason"]]


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert affected rows into JSON-safe records."""
    return frame.round(2).to_dict(orient="records")
