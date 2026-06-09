import json
import runpy
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.services.code_generator import generate_code_artifacts
from app.services.model_runner import REPO_ROOT


client = TestClient(app)


def test_generate_code_artifacts_creates_executable_python_and_notebook() -> None:
    df = pd.DataFrame(
        {
            "area_sqft": [650, 820, 980, 1200, 1500, 1750, 900, 1320, 2100, 2400],
            "bedrooms": [1, 2, 2, 3, 3, 4, 2, 3, 4, 5],
            "near_mrt": [1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            "price_usd": [
                325000,
                430000,
                455000,
                680000,
                710000,
                920000,
                390000,
                640000,
                1050000,
                1360000,
            ],
        }
    )

    result = generate_code_artifacts(
        df=df,
        file_name="unit.csv",
        target_column="price_usd",
        model_name="Ridge 迴歸",
        analysis_mode="regression",
        chart_types="model_comparison,feature_importance,predicted_vs_actual,residual_plot",
    )

    python_path = REPO_ROOT / Path(result["python_path"])
    notebook_path = REPO_ROOT / Path(result["notebook_path"])
    dataset_path = REPO_ROOT / Path(result["dataset_path"])

    assert python_path.exists()
    assert notebook_path.exists()
    assert dataset_path.exists()
    assert result["model_name"] == "Ridge 迴歸"
    assert result["selected_chart_types"] == [
        "model_comparison",
        "feature_importance",
        "predicted_vs_actual",
        "residual_plot",
    ]
    assert result["python_content"] == python_path.read_text(encoding="utf-8")
    assert result["notebook_content"] == notebook_path.read_text(encoding="utf-8")

    generated_code = python_path.read_text(encoding="utf-8")
    assert "train_test_split" in generated_code
    assert "SimpleImputer" in generated_code
    assert "save_predicted_vs_actual" in generated_code

    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert notebook["cells"][0]["cell_type"] == "markdown"
    assert notebook["cells"][1]["cell_type"] == "code"

    runpy.run_path(str(python_path), run_name="__main__")


def test_generate_code_api_returns_downloadable_artifacts() -> None:
    sample_path = REPO_ROOT / "sample_datasets" / "housing_sample.csv"

    with sample_path.open("rb") as file:
        response = client.post(
            "/api/code/generate",
            data={
                "target_column": "price_usd",
                "model_name": "Ridge 迴歸",
                "analysis_mode": "regression",
                "chart_types": "model_comparison,feature_importance,predicted_vs_actual,residual_plot",
            },
            files={"file": ("housing_sample.csv", file, "text/csv")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["python_url"].endswith(".py")
    assert payload["notebook_url"].endswith(".ipynb")
    assert "train_test_split" in payload["python_content"]
    assert "智能金融資料分析自動生成 Notebook" in payload["notebook_content"]
    assert (REPO_ROOT / payload["python_path"]).exists()
    assert (REPO_ROOT / payload["notebook_path"]).exists()


def test_generate_merged_code_api_returns_downloadable_artifacts() -> None:
    housing_path = REPO_ROOT / "sample_datasets" / "housing_sample.csv"
    stock_path = REPO_ROOT / "sample_datasets" / "stock_prices_sample.csv"

    with housing_path.open("rb") as housing_file, stock_path.open("rb") as stock_file:
        response = client.post(
            "/api/code/generate-merged",
            data={
                "target_column": "price_usd",
                "model_name": "隨機森林",
                "analysis_mode": "auto",
                "chart_types": "auto",
            },
            files=[
                ("files", ("housing_sample.csv", housing_file, "text/csv")),
                ("files", ("stock_prices_sample.csv", stock_file, "text/csv")),
            ],
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["file_name"] == "merged_dataset.csv"
    assert payload["model_name"] == "隨機森林"
    assert "residual_plot" in payload["selected_chart_types"]
    assert (REPO_ROOT / payload["python_path"]).exists()
    assert (REPO_ROOT / payload["notebook_path"]).exists()
