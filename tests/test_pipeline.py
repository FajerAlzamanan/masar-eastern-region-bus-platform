from backend.pipeline import run_full_pipeline
from backend.main import get_data_model, get_repo_file, get_repo_tree, get_table_preview


def test_pipeline_generates_expected_tables():
    result = run_full_pipeline(write_outputs=False)
    assert set(result["dataset"].keys()) == {"routes", "stops", "trips", "stop_events"}
    assert len(result["dataset"]["trips"]) >= 10
    assert len(result["dataset"]["stop_events"]) > len(result["dataset"]["trips"])
    assert "route_id" in result["dataset"]["stops"].columns


def test_validation_passes_for_generated_dataset():
    result = run_full_pipeline(write_outputs=False)
    assert result["validation"]["passed"] is True
    assert result["validation"]["quality_score"] >= 0.85
    assert result["validation"]["analysis_gate"] == "allowed"
    assert result["validation"]["passed_checks"] >= 5
    assert result["validation"]["failed_checks_count"] == 0
    first_check = result["validation"]["checks"][0]
    assert {"category", "severity", "failed_row_count"}.issubset(first_check)


def test_analysis_returns_required_kpis():
    result = run_full_pipeline(write_outputs=False)
    kpis = result["analysis"]["kpis"]
    assert kpis["trips_analyzed"] >= 10
    assert "worst_stop" in kpis
    assert kpis["avg_final_delay_sec"] > 0


def test_recommendation_is_explainable():
    result = run_full_pipeline(write_outputs=False)
    recommendation = result["recommendation"]
    assert recommendation["status"] in {"recommendation_ready", "needs_review"}
    assert recommendation["recommended_action"]
    assert recommendation["evidence"]["quality_score"] >= 0.85


def test_data_model_endpoint_describes_tables_and_relationships():
    model = get_data_model()
    table_names = {table["name"] for table in model["tables"]}
    assert table_names == {"routes", "stops", "trips", "stop_events"}
    assert len(model["relationships"]) == 4
    stop_events = next(table for table in model["tables"] if table["name"] == "stop_events")
    stops = next(table for table in model["tables"] if table["name"] == "stops")
    assert stop_events["row_count"] > 0
    assert stop_events["primary_key"] == ["trip_id", "stop_id"]
    assert {key["column"] for key in stop_events["foreign_keys"]} == {"trip_id", "stop_id"}
    assert "route_id" in {column["name"] for column in stops["columns"]}
    assert {"trip_id", "stop_id", "added_delay_sec"}.issubset({column["name"] for column in stop_events["columns"]})


def test_table_preview_returns_live_generated_rows():
    preview = get_table_preview("stop_events", limit=3)
    assert preview["table"] == "stop_events"
    assert preview["row_count"] >= 3
    assert len(preview["rows"]) == 3
    assert {"trip_id", "stop_id", "delay_cause"}.issubset(set(preview["columns"]))


def test_repo_browser_exposes_tree_and_text_files():
    tree = get_repo_tree()
    names = {item["name"] for item in tree["items"]}
    assert {"backend", "frontend", "README.md"}.issubset(names)

    readme = get_repo_file("README.md")
    assert readme["kind"] == "text"
    assert "Bus Delay DSS" in readme["content"]
