import asyncio
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.analysis_jobs import (
    cancel_analysis_job,
    create_analysis_job,
    get_analysis_job,
)
from app.services.analysis_progress import AnalysisCancelledError

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_analysis_job_reports_real_progress_and_result() -> None:
    async def scenario() -> dict[str, object]:
        def runner(progress, should_cancel):
            progress("training_models", "正在訓練模型。", 1, 2)
            assert should_cancel() is False
            progress("training_models", "正在訓練模型。", 2, 2)
            return {"value": 42}

        job = create_analysis_job("models", runner)
        for _ in range(100):
            status = get_analysis_job(job.job_id)
            if status["status"] == "completed":
                return status
            await asyncio.sleep(0.01)
        raise AssertionError("analysis job did not complete")

    result = asyncio.run(scenario())

    assert result["stage"] == "completed"
    assert result["result"] == {"value": 42}
    assert result["completed_items"] == 2
    assert result["total_items"] == 2
    assert result["elapsed_seconds"] >= 0


def test_analysis_job_can_be_cancelled_cooperatively() -> None:
    async def scenario() -> dict[str, object]:
        def runner(progress, should_cancel):
            for index in range(100):
                if should_cancel():
                    raise AnalysisCancelledError()
                progress("training_models", "正在訓練模型。", index, 100)
                time.sleep(0.005)
            return {"unexpected": True}

        job = create_analysis_job("models", runner)
        await asyncio.sleep(0.02)
        cancel_analysis_job(job.job_id)
        for _ in range(100):
            status = get_analysis_job(job.job_id)
            if status["status"] == "cancelled":
                return status
            await asyncio.sleep(0.01)
        raise AssertionError("analysis job did not cancel")

    result = asyncio.run(scenario())

    assert result["stage"] == "cancelled"
    assert result["result"] is None


def test_model_job_endpoint_runs_real_dataset_analysis() -> None:
    dataset_path = REPO_ROOT / "sample_datasets" / "housing_sample.csv"

    with TestClient(app) as client:
        with dataset_path.open("rb") as dataset_file:
            response = client.post(
                "/api/jobs/models",
                files={"files": (dataset_path.name, dataset_file, "text/csv")},
                data={
                    "target_column": "price_usd",
                    "analysis_mode": "auto",
                    "chart_types": "model_comparison",
                    "model_selection_mode": "auto",
                    "selected_models": "auto",
                    "automl_mode": "off",
                },
            )

        assert response.status_code == 200
        job_id = response.json()["job_id"]
        states: list[str] = []
        payload: dict[str, object] | None = None
        for _ in range(300):
            status_response = client.get(f"/api/jobs/{job_id}")
            assert status_response.status_code == 200
            payload = status_response.json()
            states.append(str(payload["stage"]))
            if payload["status"] in {"completed", "failed", "cancelled"}:
                break
            time.sleep(0.02)

    assert payload is not None
    assert payload["status"] == "completed"
    assert any(
        stage in states
        for stage in ("detecting_problem", "selecting_models", "training_models")
    )
    result = payload["result"]
    assert isinstance(result, dict)
    assert result["target_column"] == "price_usd"
    assert result["problem_type"] == "regression"
    assert len(result["model_results"]) >= 2
    assert result["selected_model_keys"]
    assert result["charts"][0]["chart_type"] == "model_comparison"
    assert result["charts"][0]["chart_url"].startswith("/api/artifacts/")
    assert Path(result["charts"][0]["chart_path"]).suffix == ".png"
    assert result["model_results"][0]["model_url"] == ""
    assert result["model_results"][0]["model_path"] == ""
    assert result["model_results"][0]["model_save_status"]["saved"] is False
    assert result["model_save_policy"]["save_model"] is False
