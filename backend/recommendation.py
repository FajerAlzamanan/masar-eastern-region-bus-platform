"""Recommendation assembly for the DSS.

This module intentionally separates the final decision output from raw KPI
calculation. A recommendation should include evidence, confidence, limitations,
and a next step.
"""

from typing import Any


def generate_recommendation(
    project: dict[str, Any],
    decision_card: dict[str, Any],
    validation_report: dict[str, Any],
    analysis: dict[str, Any],
    scenario_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create an explainable recommendation or a safe failure response."""
    # A DSS should fail safely when quality gates fail. This is better than
    # showing a confident recommendation built on unreliable data.
    if not validation_report["passed"]:
        return {
            "status": "blocked",
            "reason": decision_card["safe_failure_message"],
            "evidence": {
                "quality_score": validation_report["quality_score"],
                "failed_checks": validation_report["failed_checks"],
            },
            "next_step": "Fix data-quality issues before analysis and recommendation.",
        }

    # Minimum evidence prevents the system from recommending with too few trips.
    trips_analyzed = analysis["kpis"]["trips_analyzed"]
    if trips_analyzed < decision_card["minimum_trips_for_recommendation"]:
        return {
            "status": "blocked",
            "reason": "Not enough trips to support a recommendation.",
            "evidence": {"trips_analyzed": trips_analyzed},
            "next_step": "Generate more trips or reduce the minimum threshold only with supervisor approval.",
        }

    # Scenario results are pre-sorted by action_score, so the first item is the
    # current best candidate for a pilot or review.
    best = scenario_results[0]
    confidence = best["confidence"]
    status = "recommendation_ready" if confidence >= 0.65 else "needs_review"

    return {
        "status": status,
        "project": project["project_name"],
        "decision_question": decision_card["decision_question"],
        "recommended_action": best["name"],
        "target_stop_id": best["target_stop_id"],
        "expected_improvement_sec": best["improvement_sec"],
        "confidence": confidence,
        "action_score": best["action_score"],
        "evidence": {
            "quality_score": validation_report["quality_score"],
            "worst_stop": analysis["kpis"]["worst_stop"],
            "baseline_avg_delay_sec": best["baseline_avg_delay_sec"],
            "scenario_avg_delay_sec": best["scenario_avg_delay_sec"],
            "scenario_description": best["description"],
        },
        "limitations": [
            "Synthetic training data only.",
            "No live AVL feed.",
            "Cost and feasibility are simplified for learning.",
            "Recommendation should be piloted before operational adoption.",
        ],
        "next_step": "Run a controlled pilot and compare before/after KPIs.",
        "audit_note": "Recommendation generated from config, synthetic data, validation, analysis, and scenario comparison.",
    }
