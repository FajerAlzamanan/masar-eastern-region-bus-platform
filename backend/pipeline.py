"""Pipeline orchestration for the DSS.

This module is the backend spine. It loads config, generates data, validates it,
calculates KPIs, runs scenarios, and produces the recommendation object consumed
by the frontend.
"""

from typing import Any

from backend.analysis import analyze_dataset
from backend.generator import generate_dataset
from backend.paths import CONFIG_DIR, GENERATED_DIR, OUTPUT_DIR
from backend.recommendation import generate_recommendation
from backend.scenarios import run_scenarios
from backend.utils import read_json, write_json
from backend.validation import validate_dataset


def run_full_pipeline(write_outputs: bool = True) -> dict[str, Any]:
    """Run the complete learning pipeline from config to recommendation."""
    # Config files keep assumptions reviewable and easy to change.
    project = read_json(CONFIG_DIR / "problem_scope.json")
    decision_card = read_json(CONFIG_DIR / "decision_card.json")
    generation_rules = read_json(CONFIG_DIR / "generation_rules.json")
    validation_rules = read_json(CONFIG_DIR / "validation_rules.json")
    kpi_config = read_json(CONFIG_DIR / "kpi_config.json")
    scenarios_config = read_json(CONFIG_DIR / "scenarios.json")

    # The order matters: do not recommend before data exists, passes validation,
    # and has been analyzed.
    dataset = generate_dataset(generation_rules)
    validation_report = validate_dataset(dataset, validation_rules)
    analysis = analyze_dataset(dataset, kpi_config)
    scenario_results = run_scenarios(dataset, scenarios_config, kpi_config)
    recommendation = generate_recommendation(project, decision_card, validation_report, analysis, scenario_results)

    result = {
        "project": project,
        "dataset": dataset,
        "validation": validation_report,
        "analysis": analysis,
        "scenarios": scenario_results,
        "recommendation": recommendation,
    }

    if write_outputs:
        # Persist outputs so students can inspect files, collect screenshots,
        # and compare API responses with generated artifacts.
        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        for name, frame in dataset.items():
            frame.to_csv(GENERATED_DIR / f"{name}.csv", index=False)
        write_json(OUTPUT_DIR / "validation_report.json", validation_report)
        write_json(OUTPUT_DIR / "analysis_summary.json", analysis)
        write_json(OUTPUT_DIR / "scenario_results.json", scenario_results)
        write_json(OUTPUT_DIR / "recommendation.json", recommendation)

    return result
