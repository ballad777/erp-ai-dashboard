from pathlib import Path
from time import perf_counter

import pandas as pd

from app.services.model_runner import MAX_AUTO_MODEL_TRAIN_ROWS, REPO_ROOT, run_model_analysis


def test_run_model_analysis_auto_recommends_regression_models() -> None:
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

    result = run_model_analysis(df, file_name="unit.csv", target_column="price_usd")

    assert result["problem_type"] == "regression"
    assert result["target_column"] == "price_usd"
    assert result["model_selection_mode"] == "auto"
    assert len(result["model_results"]) > 4
    assert "ridge" in result["selected_model_keys"]
    assert "gradient_boosting_regressor" in result["selected_model_keys"]
    assert result["recommended_models"]
    assert result["available_models"]
    assert result["plain_summary"]["headline"]
    assert result["confidence"]["level"] in {"high", "medium", "low"}
    assert result["evidence"]
    assert any(term["term"] == "RMSE" for term in result["terms"])
    assert result["model_guidance"]["recommended_models"]
    assert result["research_details"]["parameters"]["train_test_split"] == "75/25"
    assert Path(result["chart_path"]).suffix == ".png"
    assert (REPO_ROOT / Path(result["chart_path"])).exists()


def test_run_model_analysis_detects_classification_target() -> None:
    df = pd.DataFrame(
        {
            "area_sqft": [650, 820, 980, 1200, 1500, 1750, 900, 1320, 2100, 2400],
            "bedrooms": [1, 2, 2, 3, 3, 4, 2, 3, 4, 5],
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
            "near_mrt": [1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        }
    )

    result = run_model_analysis(df, file_name="unit.csv", target_column="near_mrt")

    assert result["problem_type"] == "classification"
    assert len(result["model_results"]) >= 4
    assert "accuracy" in result["model_results"][0]
    assert result["recommended_models"]
    assert result["notes"]


def test_run_model_analysis_generates_requested_charts() -> None:
    df = pd.DataFrame(
        {
            "area_sqft": [650, 820, 980, 1200, 1500, 1750, 900, 1320, 2100, 2400],
            "bedrooms": [1, 2, 2, 3, 3, 4, 2, 3, 4, 5],
            "distance_to_mrt": [0.4, 0.7, 1.8, 0.5, 2.4, 0.6, 1.7, 0.8, 2.1, 0.9],
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

    result = run_model_analysis(
        df,
        file_name="unit.csv",
        target_column="price_usd",
        analysis_mode="regression",
        chart_types=(
            "model_comparison,feature_importance,predicted_vs_actual,residual_plot"
        ),
        model_selection_mode="custom",
        selected_models="ridge,random_forest,gradient_boosting_regressor",
    )

    assert result["analysis_mode"] == "regression"
    assert result["model_selection_mode"] == "custom"
    assert result["selected_model_keys"] == [
        "ridge",
        "random_forest",
        "gradient_boosting_regressor",
    ]
    assert len(result["model_results"]) == 4
    assert result["model_results"][0]["model_key"] == "baseline_regressor"
    assert result["selected_chart_types"] == [
        "model_comparison",
        "feature_importance",
        "predicted_vs_actual",
        "residual_plot",
    ]
    assert len(result["charts"]) == 4
    assert len(result["chart_stories"]) == 4
    assert "不能" in result["chart_stories"][0]["what_it_cannot_prove"]
    for chart in result["charts"]:
        assert Path(chart["chart_path"]).suffix == ".png"
        assert (REPO_ROOT / Path(chart["chart_path"])).exists()


def test_run_model_analysis_rejects_invalid_manual_model() -> None:
    df = pd.DataFrame(
        {
            "feature_a": [1, 2, 3, 4, 5],
            "feature_b": [10, 20, 30, 40, 50],
            "target": [12, 24, 36, 48, 60],
        }
    )

    try:
        run_model_analysis(
            df,
            file_name="unit.csv",
            target_column="target",
            model_selection_mode="custom",
            selected_models="not_a_model",
        )
    except Exception as exc:
        assert "模型不支援" in str(exc)
    else:
        raise AssertionError("invalid custom model should not be supported")


def test_run_model_analysis_accepts_manual_alias_for_custom_selection() -> None:
    df = pd.DataFrame(
        {
            "feature_a": [1, 2, 3, 4, 5, 6],
            "feature_b": [10, 20, 30, 40, 50, 60],
            "target": [12, 24, 36, 48, 60, 72],
        }
    )

    result = run_model_analysis(
        df,
        file_name="unit.csv",
        target_column="target",
        model_selection_mode="manual",
        selected_models="ridge",
    )

    assert result["model_selection_mode"] == "custom"
    assert result["selected_model_keys"] == ["ridge"]
    assert len(result["model_results"]) == 2
    assert result["model_results"][0]["model_key"] == "baseline_regressor"


def test_run_model_analysis_handles_mixed_type_categorical_features() -> None:
    df = pd.DataFrame(
        {
            "mixed_category": ["north", 2, "south", 4, "north", 6, "south", 8],
            "feature": [1, 2, 3, 4, 5, 6, 7, 8],
            "target": [10, 12, 18, 21, 24, 30, 35, 39],
        }
    )

    result = run_model_analysis(
        df,
        file_name="mixed.csv",
        target_column="target",
        analysis_mode="regression",
        model_selection_mode="custom",
        selected_models="ridge",
        chart_types="model_comparison",
    )

    assert result["problem_type"] == "regression"
    assert [item["model_key"] for item in result["model_results"]] == [
        "baseline_regressor",
        "ridge",
    ]


def test_run_model_analysis_keeps_large_high_cardinality_data_fast() -> None:
    row_count = MAX_AUTO_MODEL_TRAIN_ROWS + 4_000
    df = pd.DataFrame(
        {
            "customer_id": [f"CUST-{index:06d}" for index in range(row_count)],
            "region": [["north", "south", "west", "east"][index % 4] for index in range(row_count)],
            "product": [["A", "B", "C"][index % 3] for index in range(row_count)],
            "units": [(index % 8) + 1 for index in range(row_count)],
            "unit_price": [95 + (index % 11) * 2 for index in range(row_count)],
            "revenue": [
                ((index % 8) + 1) * (95 + (index % 11) * 2) + (index % 5)
                for index in range(row_count)
            ],
        }
    )

    started = perf_counter()
    result = run_model_analysis(
        df,
        file_name="large_sales.csv",
        target_column="revenue",
        chart_types="model_comparison",
    )
    elapsed = perf_counter() - started

    assert elapsed < 45
    assert result["source_row_count"] == row_count
    assert result["row_count_used"] == MAX_AUTO_MODEL_TRAIN_ROWS
    assert result["feature_count_used"] == 4
    assert "customer_id" not in result["selected_model_keys"]
    assert "svr" not in result["selected_model_keys"]
    assert "knn_regressor" not in result["selected_model_keys"]
    assert any("抽樣" in note for note in result["notes"])
    assert any("customer_id" in note for note in result["notes"])
    assert result["charts"]


def test_run_model_analysis_rejects_heatmap_chart() -> None:
    df = pd.DataFrame(
        {
            "feature_a": [1, 2, 3, 4, 5],
            "feature_b": [10, 20, 30, 40, 50],
            "target": [12, 24, 36, 48, 60],
        }
    )

    try:
        run_model_analysis(
            df,
            file_name="unit.csv",
            target_column="target",
            chart_types="correlation_heatmap",
        )
    except Exception as exc:
        assert "圖表類型不支援" in str(exc)
    else:
        raise AssertionError("heatmap chart should not be supported")
