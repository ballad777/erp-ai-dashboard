from pathlib import Path

from fastapi.testclient import TestClient
from docx import Document

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
    assert Path(payload["model_analysis"]["model_results_path"]).suffix == ".xlsx"
    assert payload["model_analysis"]["model_results_url"].startswith("/api/artifacts/")
    assert (REPO_ROOT / Path(payload["model_analysis"]["model_results_path"])).exists()
    assert payload["financial_analysis"]["var_95"] is not None
    assert payload["decision_brief"]["priority_findings"]
    assert payload["decision_brief"]["chart_interpretations"]
    assert payload["decision_brief"]["model_guidance"]["recommended_models"]
    assert payload["model_analysis"]["recommended_models"][0]["purpose"]


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
    assert Path(payload["report_path"]).suffix == ".docx"
    assert payload["report_url"].startswith("/api/artifacts/")
    report_path = REPO_ROOT / Path(payload["report_path"])
    assert report_path.exists()
    assert payload["workflow"]["executive_summary"]
    assert payload["workflow"]["decision_brief"]["plain_language_summary"]["next_step"]
    document = Document(report_path)
    report_text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "商業意義" in report_text
    assert "建議行動" in report_text
    assert "圖表說明" in report_text
    assert "不能證明什麼" in report_text
    assert "AI 結論摘要" in report_text
