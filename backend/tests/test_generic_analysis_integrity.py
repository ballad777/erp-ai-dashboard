import pandas as pd
import pytest
from fastapi import HTTPException
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.services.data_understanding import (
    DataDiagnostics,
    AnalysisIntegrityValidator,
    build_dataset_understanding,
    plan_multi_table_strategy,
)
from app.services.dataset_analyzer import analyze_dataframe
from app.services.feature_name_resolver import FeatureNameResolver
from app.services.financial_analyzer import run_financial_analysis
from app.services.model_runner import run_model_analysis


def test_generic_teaching_classification_recommends_class_target_without_dataset_hardcode() -> None:
    df = pd.DataFrame(
        {
            "length_a": [5.1, 4.9, 6.2, 5.9, 7.1, 6.8, 5.4, 6.0, 7.2, 6.4],
            "width_a": [3.5, 3.0, 2.8, 3.0, 3.1, 3.2, 3.7, 2.9, 3.0, 3.2],
            "length_b": [1.4, 1.5, 4.3, 4.2, 5.9, 5.7, 1.7, 4.5, 6.0, 5.3],
            "width_b": [0.2, 0.2, 1.3, 1.5, 2.1, 2.3, 0.4, 1.5, 1.8, 2.0],
            "class_label": ["A", "A", "B", "B", "C", "C", "A", "B", "C", "C"],
        }
    )

    understanding = build_dataset_understanding(df, file_name="teaching_classification.csv")

    assert understanding["primary_domain"]["label"] == "待確認資料集"
    assert understanding["target_recommendations"][0]["column"] == "class_label"
    assert understanding["target_recommendations"][0]["task_type"] == "classification"
    assert understanding["task_recommendations"][1]["task"] == "classification"
    assert understanding["task_recommendations"][1]["can_run"] is True
    assert "鳶尾花" not in str(understanding)


def test_id_plus_target_dataset_is_blocked_before_modeling() -> None:
    df = pd.DataFrame(
        {
            "record_id": [f"R-{index}" for index in range(20)],
            "target": [index % 2 for index in range(20)],
        }
    )

    with pytest.raises(HTTPException) as exc:
        run_model_analysis(df, file_name="id_target.csv", target_column="target")

    assert exc.value.status_code == 400
    assert "可用特徵少於 2" in str(exc.value.detail)


def test_train_unlabeled_test_submission_structure_is_not_merged() -> None:
    train = pd.DataFrame(
        {
            "row_id": [1, 2, 3, 4, 5, 6],
            "feature_a": [1, 2, 3, 4, 5, 6],
            "feature_b": [6, 5, 4, 3, 2, 1],
            "target": [10, 12, 14, 16, 18, 20],
        }
    )
    test = pd.DataFrame(
        {
            "row_id": [7, 8, 9],
            "feature_a": [7, 8, 9],
            "feature_b": [1, 2, 3],
        }
    )
    submission = pd.DataFrame({"row_id": [7, 8, 9], "prediction": [0, 0, 0]})

    plan = plan_multi_table_strategy(
        [
            ("train.csv", train),
            ("test.csv", test),
            ("sample_submission.csv", submission),
        ]
    )

    assert plan["recommended_strategy"] == "train_predict_workflow"
    assert "不可把未標籤 test 或 submission format 當訓練資料合併" in plan["reason"]
    role_keys = {item["role_key"] for item in plan["table_roles"]}
    assert {"training_dataset", "submission_format"}.issubset(role_keys)


def test_price_alone_does_not_force_housing_label() -> None:
    df = pd.DataFrame(
        {
            "item": ["A", "B", "C", "D"],
            "price": [10.0, 12.0, 9.5, 13.0],
            "quantity": [2, 3, 1, 4],
        }
    )

    understanding = build_dataset_understanding(df, file_name="prices.csv")

    assert understanding["primary_domain"]["key"] != "housing_price"
    assert understanding["primary_domain"]["label"] == "待確認資料集"


def test_non_financial_date_dataset_does_not_run_financial_indicators() -> None:
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=12),
            "score": [60, 62, 61, 65, 64, 66, 67, 69, 70, 72, 71, 73],
            "team": ["A", "B"] * 6,
        }
    )

    with pytest.raises(HTTPException) as exc:
        run_financial_analysis(df, file_name="date_scores.csv")

    assert exc.value.status_code == 400
    assert "不適合金融技術分析" in str(exc.value.detail)


def test_multi_table_different_schema_keeps_separate() -> None:
    plan = plan_multi_table_strategy(
        [
            ("customers.csv", pd.DataFrame({"customer_id": [1, 2], "segment": ["A", "B"]})),
            ("events.csv", pd.DataFrame({"event_id": [10, 11], "timestamp": ["2024-01-01", "2024-01-02"], "value": [3, 4]})),
        ]
    )

    assert plan["recommended_strategy"] in {"keep_separate", "relational_analysis"}
    assert plan["recommended_strategy"] != "union"


def test_sequential_analysis_does_not_reuse_previous_schema_or_story() -> None:
    first = analyze_dataframe(
        pd.DataFrame({"customer_id": [1, 2, 3], "segment": ["A", "B", "A"], "churn": [0, 1, 0]}),
        file_name="customers.csv",
    )
    second = analyze_dataframe(
        pd.DataFrame({"date": ["2024-01-01", "2024-01-02"], "temperature": [21.5, 22.0], "humidity": [0.7, 0.72]}),
        file_name="weather.csv",
    )

    assert first["analysis_context"]["schema_fingerprint"] != second["analysis_context"]["schema_fingerprint"]
    assert "customer_id" not in str(second["plain_summary"])
    assert "segment" not in str(second["plain_summary"])


def test_feature_name_resolver_preserves_one_hot_names() -> None:
    df = pd.DataFrame(
        {
            "Amount": [10, 20, 30, 40],
            "Country": ["USA", "Taiwan", "Japan", "USA"],
        }
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", Pipeline([("scaler", StandardScaler())]), ["Amount"]),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), ["Country"]),
        ]
    )
    preprocessor.fit(df)

    names = FeatureNameResolver().resolve_preprocessor(preprocessor)

    assert "Amount" in names
    assert "Country=USA" in names
    assert "Country=Taiwan" in names
    assert not any(name.startswith(("feature_", "column_", "欄位")) for name in names)


def test_integrity_validator_rejects_nonexistent_columns() -> None:
    with pytest.raises(ValueError):
        AnalysisIntegrityValidator().validate_columns_exist(
            schema_columns=["a", "b"],
            referenced_columns=["a", "missing"],
            context="unit",
        )


def test_data_diagnostics_contains_required_generic_fields() -> None:
    diagnostics = DataDiagnostics().analyze(
        pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "category": ["A", "A", "B", "B"],
                "value": [10, 12, 11, 14],
            }
        )
    )

    for key in [
        "row_count",
        "column_count",
        "column_names",
        "dtypes",
        "missing_ratio",
        "duplicate_ratio",
        "unique_ratio",
        "constant_columns",
        "id_like_columns",
        "datetime_columns",
        "numeric_columns",
        "categorical_columns",
        "text_columns",
        "high_cardinality_columns",
        "candidate_target_columns",
        "possible_leakage_columns",
        "outlier_columns",
        "class_balance",
        "usable_feature_count",
    ]:
        assert key in diagnostics


def test_non_standard_ticker_price_column_is_financial_when_date_exists() -> None:
    df = pd.DataFrame(
        {
            "Date": pd.date_range("2014-01-01", periods=30),
            "AAPL": [90 + index * 0.3 for index in range(30)],
        }
    )

    understanding = build_dataset_understanding(df, file_name="apple_stock.csv")

    assert understanding["primary_domain"]["key"] == "financial_timeseries"
    assert understanding["financial_eligibility"]["eligible"] is True
    assert "AAPL" in understanding["financial_eligibility"]["price_columns"]


def test_weather_dataset_gets_specific_evidence_based_story() -> None:
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=30),
            "precipitation": [0, 1, 0.2, 0, 2, 0.5] * 5,
            "temp_max": [18, 19, 20, 21, 18, 17] * 5,
            "temp_min": [10, 11, 12, 13, 10, 9] * 5,
            "wind": [3.2, 2.8, 4.1, 3.9, 5.0, 2.5] * 5,
            "weather": ["sun", "rain", "sun", "cloud", "rain", "sun"] * 5,
        }
    )

    understanding = build_dataset_understanding(df, file_name="weather_observations.csv")

    assert understanding["primary_domain"]["key"] == "weather"
    assert "天氣" in understanding["dataset_story"]["one_sentence"]
    assert any("降雨" in item or "氣溫" in item for item in understanding["dataset_story"]["can_answer"])


def test_no_header_like_columns_are_flagged_for_human_review() -> None:
    df = pd.DataFrame(
        {
            "842302": [842517, 843009, 843483, 843584],
            "M": ["M", "B", "M", "B"],
            "17.99": [20.57, 19.69, 11.42, 20.29],
            "10.38": [17.77, 21.25, 20.38, 14.34],
            "122.8": [132.9, 130.0, 77.58, 135.1],
        }
    )

    understanding = build_dataset_understanding(df, file_name="wdbc.data")

    assert understanding["data_diagnostics"]["suspected_header_issue"] is True
    assert any("表頭" in reason for reason in understanding["not_suitable_reasons"])


def test_biology_columns_get_specific_story_without_dataset_name_hardcode() -> None:
    df = pd.DataFrame(
        {
            "species": ["A", "A", "B", "B", "C", "C"],
            "island": ["north", "south", "north", "south", "north", "south"],
            "bill_length_mm": [39.1, 40.3, 45.2, 46.1, 50.0, 51.3],
            "bill_depth_mm": [18.7, 18.2, 15.8, 15.2, 14.1, 14.5],
            "flipper_length_mm": [181, 186, 210, 215, 220, 225],
            "body_mass_g": [3750, 3800, 4500, 4550, 5100, 5200],
        }
    )

    understanding = build_dataset_understanding(df, file_name="field_measurements.csv")

    assert understanding["primary_domain"]["key"] == "biology"
    assert understanding["target_recommendations"][0]["column"] == "species"
    assert "生物" in understanding["dataset_story"]["one_sentence"]
    assert "待確認資料集" not in understanding["dataset_story"]["one_sentence"]
