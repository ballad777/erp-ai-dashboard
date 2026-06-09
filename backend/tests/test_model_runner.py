from pathlib import Path

import pandas as pd

from app.services.model_runner import REPO_ROOT, run_model_analysis


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
    assert len(result["model_results"]) == 3
    assert result["selected_chart_types"] == [
        "model_comparison",
        "feature_importance",
        "predicted_vs_actual",
        "residual_plot",
    ]
    assert len(result["charts"]) == 4
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
    assert len(result["model_results"]) == 1


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
