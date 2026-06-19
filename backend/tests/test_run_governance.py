import base64
import json
from pathlib import Path
from urllib.parse import unquote

from fastapi.testclient import TestClient

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]


def _decode_payload_from_artifact_url(url: str) -> dict[str, object]:
    token = unquote(url.removeprefix("/api/artifacts/"))
    payload_part = token.split(".", maxsplit=1)[0]
    padding = "=" * (-len(payload_part) % 4)
    return json.loads(base64.urlsafe_b64decode(payload_part + padding))


def test_dataset_analysis_persists_run_and_quality_report() -> None:
    payload = b'[{"date":"2026-01-01","sales":100,"region":"north"},{"date":"2026-01-02","sales":150,"region":"north"}]'

    response = TestClient(app).post(
        "/api/datasets/analyze",
        files={"file": ("sales.json", payload, "application/json")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["file_name"] == "sales.json"
    assert body["row_count"] == 2
    assert body["run_id"].startswith("run_")
    assert body["dataset_id"].startswith("dataset_")
    assert body["schema_fingerprint"]
    assert body["dataset_hash"]
    assert body["quality_report"]["quality_score"] >= 0
    assert body["run_manifest"]["input_files"][0]["file_name"] == "sales.json"


def test_model_artifact_token_is_bound_to_run_context() -> None:
    dataset_path = REPO_ROOT / "sample_datasets" / "housing_sample.csv"

    with dataset_path.open("rb") as dataset_file:
        response = TestClient(app).post(
            "/api/models/analyze",
            files={"file": (dataset_path.name, dataset_file, "text/csv")},
            data={
                "target_column": "price_usd",
                "analysis_mode": "auto",
                "chart_types": "model_comparison",
                "model_selection_mode": "custom",
                "selected_models": "ridge",
                "automl_mode": "off",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"].startswith("run_")
    assert body["dataset_id"].startswith("dataset_")
    assert body["run_manifest"]["combined_input_hash"]
    assert body["model_results"][0]["model_key"].startswith("baseline_")

    payload = _decode_payload_from_artifact_url(body["model_results_url"])
    assert payload["run_id"] == body["run_id"]
    assert payload["project_id"]
    assert payload["artifact_id"]
