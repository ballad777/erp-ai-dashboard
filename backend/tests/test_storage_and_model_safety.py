from pathlib import Path

import pandas as pd

from app.services.model_runner import MODEL_DIR, _model_catalog, run_model_analysis
from app.utils.storage_guard import cleanup_old_models, safe_save_model


def test_save_model_false_does_not_create_joblib() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    before = {path.name for path in MODEL_DIR.glob("*.joblib")}
    df = pd.DataFrame(
        {
            "feature_a": [1, 2, 3, 4, 5, 6, 7, 8],
            "feature_b": [3, 1, 4, 1, 5, 9, 2, 6],
            "target": [11, 13, 18, 20, 26, 31, 35, 39],
        }
    )

    result = run_model_analysis(
        df,
        file_name="unit.csv",
        target_column="target",
        model_selection_mode="custom",
        selected_models="ridge",
        chart_types="model_comparison",
        save_model=False,
    )

    after = {path.name for path in MODEL_DIR.glob("*.joblib")}
    assert after == before
    assert all(metric["model_path"] == "" for metric in result["model_results"])
    assert all(metric["model_save_status"]["saved"] is False for metric in result["model_results"])


def test_save_model_true_uses_safe_save_model(tmp_path: Path) -> None:
    path = tmp_path / "safe_model.joblib"
    status = safe_save_model({"model": "small"}, path, enabled=True, max_mb=200)

    assert status["saved"] is True
    assert path.exists()


def test_safe_save_model_deletes_files_over_limit(tmp_path: Path) -> None:
    path = tmp_path / "too_large.joblib"
    status = safe_save_model({"model": "small"}, path, enabled=True, max_mb=0)

    assert status["saved"] is False
    assert "超過 0MB" in status["warning"]
    assert not path.exists()


def test_cleanup_old_models_keeps_latest_five(tmp_path: Path) -> None:
    for index in range(8):
        path = tmp_path / f"model_{index}.joblib"
        path.write_bytes(b"model")

    result = cleanup_old_models(tmp_path, keep_latest=5)

    assert result["deleted_count"] == 3
    assert len(list(tmp_path.glob("*.joblib"))) == 5


def test_random_forest_and_extra_trees_use_safe_parameters() -> None:
    specs = {
        spec.key: spec
        for spec in _model_catalog()
        if spec.key in {
            "random_forest",
            "extra_trees_regressor",
            "random_forest_classifier",
            "extra_trees_classifier",
        }
    }

    assert set(specs) == {
        "random_forest",
        "extra_trees_regressor",
        "random_forest_classifier",
        "extra_trees_classifier",
    }
    for spec in specs.values():
        model = spec.estimator_factory()
        params = model.get_params()
        assert params["n_estimators"] <= 100
        assert params["max_depth"] is not None
        assert params["max_depth"] <= 12
        assert params["min_samples_leaf"] >= 3
        assert params["max_features"] == "sqrt"


def test_source_row_number_is_not_used_as_feature_and_leakage_is_warned() -> None:
    df = pd.DataFrame(
        {
            "source_row_number": [1, 2, 3, 4, 5, 6, 7, 8],
            "copied_target": [10, 12, 15, 18, 21, 25, 28, 32],
            "signal": [2, 3, 5, 7, 11, 13, 17, 19],
            "target": [10, 12, 15, 18, 21, 25, 28, 32],
        }
    )

    result = run_model_analysis(
        df,
        file_name="leakage.csv",
        target_column="target",
        model_selection_mode="custom",
        selected_models="ridge",
        chart_types="model_comparison",
    )

    joined_notes = " ".join(result["notes"])
    assert "source_row_number" in joined_notes
    assert "資料洩漏" in joined_notes
    assert result["feature_count_used"] == 1


def test_near_perfect_metric_adds_leakage_warning() -> None:
    df = pd.DataFrame(
        {
            "feature_a": [1, 2, 3, 4, 5, 6, 7, 8],
            "feature_b": [2, 4, 6, 8, 10, 12, 14, 16],
            "target": [3, 6, 9, 12, 15, 18, 21, 24],
        }
    )

    result = run_model_analysis(
        df,
        file_name="near_perfect.csv",
        target_column="target",
        model_selection_mode="custom",
        selected_models="linear_regression",
        chart_types="model_comparison",
    )

    assert any("R² 異常接近 1" in warning for warning in result["leakage_warnings"])
