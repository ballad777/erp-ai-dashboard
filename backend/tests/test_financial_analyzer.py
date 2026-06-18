from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.services.financial_analyzer import REPO_ROOT, run_financial_analysis

client = TestClient(app)


def test_run_financial_analysis_detects_columns_and_creates_outputs() -> None:
    df = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=12, freq="D"),
            "ticker": ["DPF"] * 12,
            "close": [100, 101, 103, 102, 106, 108, 107, 111, 113, 112, 116, 118],
            "volume": [1000, 1200, 1250, 1180, 1400, 1500, 1320, 1600, 1700, 1660, 1800, 1900],
        }
    )

    result = run_financial_analysis(df, file_name="finance_unit.csv")

    assert result["date_column"] == "date"
    assert result["price_column"] == "close"
    assert result["row_count_used"] == 12
    assert result["latest_price"] == 118
    assert result["trend_label"]
    assert len(result["summary"]) == 4
    assert result["var_95"] is not None
    assert result["var_99"] is not None
    assert len(result["forecast_points"]) == 5
    assert len(result["charts"]) == 4
    assert result["plain_summary"]["headline"]
    assert result["forecast_reliability"]["level"] in {"medium", "low"}
    assert result["forecast_reliability"]["should_show_warning"] is True
    assert any(term["term"] == "RSI" for term in result["terms"])
    assert result["research_details"]["method"]
    assert (REPO_ROOT / Path(result["indicator_path"])).exists()
    for chart in result["charts"]:
        assert Path(chart["chart_path"]).suffix == ".png"
        assert (REPO_ROOT / Path(chart["chart_path"])).exists()


def test_financial_analysis_api_returns_real_chart_paths() -> None:
    sample_path = REPO_ROOT / "sample_datasets" / "stock_prices_sample.csv"

    with sample_path.open("rb") as file:
        response = client.post(
            "/api/finance/analyze",
            files={"file": ("stock_prices_sample.csv", file, "text/csv")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["date_column"] == "date"
    assert payload["price_column"] == "close"
    assert Path(payload["indicator_path"]).suffix == ".csv"
    assert payload["indicator_url"].startswith("/api/artifacts/")
    assert payload["var_95"] is not None
    assert len(payload["forecast_points"]) == 5
    assert len(payload["charts"]) == 4
    assert payload["forecast_reliability"]["forecast_label"] == "基準情境估計"
    assert payload["plain_summary"]["risk"]
    for chart in payload["charts"]:
        assert Path(chart["chart_path"]).suffix == ".png"
        assert chart["chart_url"].startswith("/api/artifacts/")
        assert (REPO_ROOT / Path(chart["chart_path"])).exists()


def test_financial_analysis_rejects_non_financial_dataset() -> None:
    df = pd.DataFrame(
        {
            "feature_a": [1, 2, 3, 4, 5, 6],
            "feature_b": [10, 20, 30, 40, 50, 60],
        }
    )

    try:
        run_financial_analysis(df, file_name="not_finance.csv")
    except Exception as exc:
        assert "日期欄位" in str(exc)
    else:
        raise AssertionError("non-financial dataset should not pass auto detection")
