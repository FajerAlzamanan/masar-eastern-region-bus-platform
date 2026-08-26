"""Synthetic data generation for the training DSS.

The generated tables are not real operations data. They are controlled training
data that lets students learn the full software path: config -> generated
tables -> validation -> analysis -> scenario -> recommendation -> UI.
"""

import random
from datetime import datetime, timedelta
from typing import Any

import pandas as pd


def generate_dataset(rules: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Generate a reproducible synthetic route dataset.

    Teaching note:
    The seed is configurable so students can reproduce exactly the same dataset
    during testing, screenshots, and final presentations.
    """
    rng = random.Random(rules["seed"])
    stops_config = rules["stops"]
    route_id = rules["route_id"]
    bus_capacity = rules["bus_capacity"]
    start_time = datetime(2026, 8, 3, rules["service_start_hour"], 0)

    routes = pd.DataFrame(
        [
            {
                "route_id": route_id,
                "route_name": "North Station to Civic Center",
                "bus_capacity": bus_capacity,
                "synthetic": True,
            }
        ]
    )

    stops = pd.DataFrame(
        [
            {
                "stop_id": stop["stop_id"],
                "route_id": route_id,
                "stop_name": stop["stop_name"],
                "sequence": index + 1,
                "base_boarding": stop["base_boarding"],
            }
            for index, stop in enumerate(stops_config)
        ]
    )

    trips_rows = []
    event_rows = []

    for trip_index in range(rules["trip_count"]):
      # Each trip is a complete bus run from the first stop to the last stop.
      departure = start_time + timedelta(minutes=trip_index * rules["headway_minutes"])
      hour = departure.hour
      is_peak = hour in rules["peak_hours"]
      trip_id = f"T{trip_index + 1:03d}"
      cumulative_delay = 0
      passenger_load = 0

      for stop_index, stop in enumerate(stops_config):
        # Each stop_event is the most important grain for analysis: one trip
        # reaching one stop, with passenger load and delay evidence attached.
        cause = _choose_delay_cause(rng, stop["problem_weight"], is_peak)
        boarding = max(0, int(rng.gauss(stop["base_boarding"] * (1.35 if is_peak else 1.0), 4)))
        alighting = max(0, int(rng.gauss(4 + stop_index, 2)))
        passenger_load = min(bus_capacity, max(0, passenger_load + boarding - alighting))
        expected_dwell = 25 + boarding * 1.4
        issue_wait = _cause_delay_seconds(rng, rules["delay_causes"][cause], stop["problem_weight"], is_peak)
        dwell_time = int(expected_dwell + issue_wait)
        traffic_delay = int(max(0, rng.gauss(35 if is_peak else 15, 12)))
        added_delay = issue_wait + traffic_delay
        cumulative_delay += int(added_delay)

        event_rows.append(
            {
                "trip_id": trip_id,
                "route_id": route_id,
                "stop_id": stop["stop_id"],
                "stop_name": stop["stop_name"],
                "sequence": stop_index + 1,
                "scheduled_arrival_min": stop_index * 6,
                "actual_arrival_min": stop_index * 6 + round(cumulative_delay / 60, 1),
                "passengers_boarding": boarding,
                "passengers_alighting": alighting,
                "passenger_load": passenger_load,
                "bus_capacity": bus_capacity,
                "expected_dwell_sec": round(expected_dwell, 1),
                "dwell_time_sec": dwell_time,
                "dwell_excess_sec": round(max(0, dwell_time - expected_dwell), 1),
                "issue_wait_sec": int(issue_wait),
                "traffic_delay_sec": traffic_delay,
                "added_delay_sec": int(added_delay),
                "cumulative_delay_sec": cumulative_delay,
                "delay_cause": cause,
                "is_peak": is_peak,
            }
        )

      trips_rows.append(
          {
              "trip_id": trip_id,
              "route_id": route_id,
              "departure_time": departure.isoformat(timespec="minutes"),
              "is_peak": is_peak,
              "final_delay_sec": cumulative_delay,
          }
      )

    return {
        "routes": routes,
        "stops": stops,
        "trips": pd.DataFrame(trips_rows),
        "stop_events": pd.DataFrame(event_rows),
    }


def _choose_delay_cause(rng: random.Random, problem_weight: float, is_peak: bool) -> str:
    """Pick a plausible delay cause using station risk and peak-period pressure."""
    boarding_probability = min(0.75, 0.25 + problem_weight * 0.45 + (0.15 if is_peak else 0))
    roll = rng.random()
    if roll < boarding_probability:
        return "boarding"
    if roll < boarding_probability + 0.18:
        return "traffic"
    return "schedule_gap"


def _cause_delay_seconds(
    rng: random.Random, cause_config: dict[str, float], problem_weight: float, is_peak: bool
) -> int:
    """Estimate added delay from the selected cause.

    The model is intentionally simple: it teaches controllable assumptions, not
    real-world prediction accuracy.
    """
    base = cause_config["base_seconds"]
    variability = cause_config["variability"]
    peak_factor = 1.35 if is_peak else 1.0
    return max(0, int(rng.gauss(base * problem_weight * peak_factor, variability)))
