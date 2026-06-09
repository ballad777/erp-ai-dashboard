from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.model_runner import REPO_ROOT

client = TestClient(app)


def test_agent_workflow_api_runs_real_agents() -> None:
    sample_path = REPO_ROOT / "sample_datasets" / "stock_prices_sample.csv"

    with sample_path.open("rb") as file:
        response = client.post(
            "/api/agents/analyze",
            data={
                "target_column": "close",
                "analysis_mode": "regression",
                "chart_types": "model_comparison",
                "model_selection_mode": "custom",
                "selected_models": "ridge,random_forest",
                "automl_mode": "off",
            },
            files={"file": ("stock_prices_sample.csv", file, "text/csv")},
        )

    assert response.status_code == 200
    payload = response.json()
    agent_names = [step["agent_name"] for step in payload["agent_steps"]]
    assert "資料理解代理" in agent_names
    assert "模型分析代理" in agent_names
    assert "金融分析代理" in agent_names
    assert payload["model_analysis"]["model_results_path"].endswith(".xlsx")
    assert (REPO_ROOT / Path(payload["model_analysis"]["model_results_path"])).exists()
    assert payload["financial_analysis"]["var_95"] is not None


def test_report_api_generates_docx_report() -> None:
    sample_path = REPO_ROOT / "sample_datasets" / "stock_prices_sample.csv"

    with sample_path.open("rb") as file:
        response = client.post(
            "/api/reports/generate",
            data={
                "target_column": "close",
                "analysis_mode": "regression",
                "chart_types": "model_comparison",
                "model_selection_mode": "custom",
                "selected_models": "ridge,random_forest",
                "automl_mode": "off",
            },
            files={"file": ("stock_prices_sample.csv", file, "text/csv")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["report_url"].endswith(".docx")
    assert (REPO_ROOT / Path(payload["report_path"])).exists()
    assert payload["workflow"]["executive_summary"]
