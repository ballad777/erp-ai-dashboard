from __future__ import annotations

import os
import json
import importlib
import importlib.util
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Callable
from uuid import uuid4

import joblib

REPO_ROOT = Path(__file__).resolve().parents[3]
MPL_CACHE_DIR = REPO_ROOT / "generated_outputs" / ".matplotlib"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastapi import HTTPException, UploadFile
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from app.services.artifact_access import create_artifact_url
from app.services.dataset_analyzer import analyze_dataframe, merge_dataframes, read_uploaded_dataframe
from app.services.insight_narrative import build_model_brief, enrich_model_option
from app.services.analysis_progress import (
    CancelCheck,
    ProgressCallback,
    emit_progress,
    ensure_not_cancelled,
)

GENERATED_OUTPUTS_DIR = REPO_ROOT / "generated_outputs"
CHART_DIR = GENERATED_OUTPUTS_DIR / "charts"
DATA_DIR = GENERATED_OUTPUTS_DIR / "data"
MODEL_DIR = GENERATED_OUTPUTS_DIR / "models"
REPORT_DIR = GENERATED_OUTPUTS_DIR / "reports"
MODEL_RANDOM_STATE = 42
MAX_AUTO_MODEL_TRAIN_ROWS = 2_000
MAX_CUSTOM_MODEL_TRAIN_ROWS = 20_000
MAX_ONE_HOT_CATEGORIES = 32
SLOW_MODEL_ROW_LIMIT = 1_500
SLOW_MODEL_FEATURE_LIMIT = 24
HIGH_CARDINALITY_MIN_UNIQUE = 1_000
HIGH_CARDINALITY_RATIO = 0.45
SLOW_MODEL_KEYS = {"svr", "svc", "knn_regressor", "knn_classifier"}
ID_LIKE_COLUMN_NAMES = {
    "id",
    "index",
    "row_id",
    "uuid",
    "guid",
    "customer_id",
    "user_id",
    "order_id",
    "transaction_id",
    "source_row_number",
}
ANALYSIS_MODES = {"auto", "regression", "classification"}
MODEL_SELECTION_MODES = {"auto", "custom"}
MODEL_SELECTION_ALIASES = {"manual": "custom"}
AUTOML_MODES = {"off", "quick"}
SUPPORTED_CHART_TYPES = {
    "auto",
    "model_comparison",
    "feature_importance",
    "predicted_vs_actual",
    "residual_plot",
}
CHART_TITLES = {
    "model_comparison": "模型比較圖",
    "feature_importance": "特徵重要性",
    "predicted_vs_actual": "預測值與實際值",
    "residual_plot": "殘差圖",
}

plt.rcParams["font.sans-serif"] = [
    "Heiti TC",
    "Arial Unicode MS",
    "Hiragino Sans",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False

def _package_dir(package_name: str) -> Path | None:
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return None
    if spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations)))
    if spec.origin:
        return Path(spec.origin).parent
    return None


def _repair_macos_openmp_link(package_name: str, relative_dylib: str) -> bool:
    if sys.platform != "darwin":
        return False

    install_name_tool = shutil.which("install_name_tool")
    package_dir = _package_dir(package_name)
    sklearn_dir = _package_dir("sklearn")
    if not install_name_tool or package_dir is None or sklearn_dir is None:
        return False

    target_dylib = package_dir / relative_dylib
    libomp_dylib = sklearn_dir / ".dylibs" / "libomp.dylib"
    if not target_dylib.exists() or not libomp_dylib.exists():
        return False

    completed = subprocess.run(
        [
            install_name_tool,
            "-change",
            "@rpath/libomp.dylib",
            str(libomp_dylib),
            str(target_dylib),
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    return completed.returncode == 0


def _import_optional_module(package_name: str, relative_dylib: str) -> Any | None:
    try:
        return importlib.import_module(package_name)
    except Exception:  # noqa: BLE001 - optional dependency fallback keeps the API usable
        if not _repair_macos_openmp_link(package_name, relative_dylib):
            return None

    sys.modules.pop(package_name, None)
    try:
        return importlib.import_module(package_name)
    except Exception:  # noqa: BLE001 - optional dependency availability is reported in model options
        return None


_xgboost_module = _import_optional_module("xgboost", "lib/libxgboost.dylib")
XGBClassifier = getattr(_xgboost_module, "XGBClassifier", None)
XGBRegressor = getattr(_xgboost_module, "XGBRegressor", None)

_lightgbm_module = _import_optional_module("lightgbm", "lib/lib_lightgbm.dylib")
LGBMClassifier = getattr(_lightgbm_module, "LGBMClassifier", None)
LGBMRegressor = getattr(_lightgbm_module, "LGBMRegressor", None)


@dataclass(frozen=True)
class ModelSpec:
    key: str
    label: str
    problem_type: str
    family: str
    description: str
    complexity: str
    estimator_factory: Callable[[], Any]
    param_grid_factory: Callable[[int], dict[str, list[Any]]] | None = None


async def run_uploaded_model_analysis(
    file: UploadFile,
    target_column: str,
    analysis_mode: str = "auto",
    chart_types: str = "auto",
    model_selection_mode: str = "auto",
    selected_models: str = "auto",
    automl_mode: str = "off",
    progress_callback: ProgressCallback | None = None,
    should_cancel: CancelCheck | None = None,
) -> dict[str, Any]:
    emit_progress(progress_callback, "reading_data", "正在讀取資料。")
    ensure_not_cancelled(should_cancel)
    df, file_name = await read_uploaded_dataframe(file)
    return run_model_analysis(
        df=df,
        file_name=file_name,
        target_column=target_column,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        model_selection_mode=model_selection_mode,
        selected_models=selected_models,
        automl_mode=automl_mode,
        progress_callback=progress_callback,
        should_cancel=should_cancel,
    )


async def run_uploaded_merged_model_analysis(
    files: list[UploadFile],
    target_column: str,
    analysis_mode: str = "auto",
    chart_types: str = "auto",
    model_selection_mode: str = "auto",
    selected_models: str = "auto",
    automl_mode: str = "off",
    progress_callback: ProgressCallback | None = None,
    should_cancel: CancelCheck | None = None,
) -> dict[str, Any]:
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="合併模型分析至少需要 2 個檔案。")

    loaded_datasets: list[tuple[str, pd.DataFrame]] = []
    skipped_files: list[str] = []

    for index, file in enumerate(files):
        ensure_not_cancelled(should_cancel)
        emit_progress(
            progress_callback,
            "reading_data",
            "正在讀取合併資料來源。",
            index,
            len(files),
        )
        file_name = file.filename or "未命名檔案"
        try:
            df, parsed_file_name = await read_uploaded_dataframe(file)
            loaded_datasets.append((parsed_file_name, df))
        except HTTPException as exc:
            skipped_files.append(f"{file_name}：{exc.detail}")

    if len(loaded_datasets) < 2:
        detail = "成功讀取的檔案不足 2 個，無法執行合併模型分析。"
        if skipped_files:
            detail += f" 已略過：{'；'.join(skipped_files)}"
        raise HTTPException(status_code=400, detail=detail)

    merged_df, merge_metadata = merge_dataframes(loaded_datasets)
    result = run_model_analysis(
        df=merged_df,
        file_name="merged_dataset.csv",
        target_column=target_column,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        model_selection_mode=model_selection_mode,
        selected_models=selected_models,
        automl_mode=automl_mode,
        progress_callback=progress_callback,
        should_cancel=should_cancel,
    )
    result["notes"] = [
        *merge_metadata["merge_notes"],
        *([f"以下檔案無法讀取，已略過：{'；'.join(skipped_files)}"] if skipped_files else []),
        *result["notes"],
    ]
    return result


def run_model_analysis(
    df: pd.DataFrame,
    file_name: str,
    target_column: str,
    analysis_mode: str = "auto",
    chart_types: str = "auto",
    model_selection_mode: str = "auto",
    selected_models: str = "auto",
    automl_mode: str = "off",
    progress_callback: ProgressCallback | None = None,
    should_cancel: CancelCheck | None = None,
) -> dict[str, Any]:
    ensure_not_cancelled(should_cancel)
    requested_mode = _normalize_analysis_mode(analysis_mode)
    requested_chart_types = _normalize_chart_types(chart_types)
    requested_model_selection_mode = _normalize_model_selection_mode(model_selection_mode)
    requested_automl_mode = _normalize_automl_mode(automl_mode)

    if target_column not in df.columns:
        raise HTTPException(status_code=400, detail="指定的目標欄位不存在。")

    notes: list[str] = []
    source_row_count = int(len(df))
    source_working_df = df.dropna(subset=[target_column]).copy()
    if source_working_df.empty:
        raise HTTPException(status_code=400, detail="目標欄位全部都是缺失值，無法訓練模型。")

    dropped_target_rows = source_row_count - int(len(source_working_df))
    if dropped_target_rows:
        notes.append(f"目標欄位缺失的 {dropped_target_rows} 筆資料未納入模型訓練；原始資料摘要仍保留完整資料。")

    emit_progress(progress_callback, "detecting_problem", "正在判斷問題類型。")
    full_target = source_working_df[target_column]
    inferred_problem_type = _infer_problem_type(full_target)
    problem_type = inferred_problem_type if requested_mode == "auto" else requested_mode

    if requested_mode == "auto":
        notes.append(f"系統自動判斷此資料適合使用「{_problem_type_label(problem_type)}」分析。")
    elif requested_mode != inferred_problem_type:
        notes.append(
            f"系統原本判斷較適合「{_problem_type_label(inferred_problem_type)}」，"
            f"本次依使用者選擇改用「{_problem_type_label(problem_type)}」。"
        )

    working_df = _prepare_modeling_dataframe(
        source_working_df,
        target_column=target_column,
        problem_type=problem_type,
        model_selection_mode=requested_model_selection_mode,
        notes=notes,
    )
    y_raw = working_df[target_column]
    x_raw = working_df.drop(columns=[target_column]).dropna(axis=1, how="all")

    if x_raw.empty:
        raise HTTPException(status_code=400, detail="除了目標欄位外沒有可用特徵。")

    y, target_notes = _prepare_target(y_raw, problem_type)
    notes.extend(target_notes)
    if x_raw.isna().any().any():
        notes.append("模型管線僅在訓練時計算缺失值補值；不會改寫原始資料、資料摘要或下載資料。")

    if len(np.unique(y)) < 2:
        raise HTTPException(status_code=400, detail="目標欄位有效類別或數值不足，至少需要兩種值。")

    if len(working_df) < 5:
        raise HTTPException(status_code=400, detail="資料列太少，至少需要 5 筆有效資料才能訓練模型。")

    stratify_target = None
    if problem_type == "classification":
        class_counts = pd.Series(y).value_counts()
        if len(class_counts) >= 2 and int(class_counts.min()) >= 2:
            stratify_target = y
            notes.append("分類任務已使用 stratified train/test split，降低類別分布偏移。")
        else:
            notes.append("分類任務類別樣本數不足，無法安全使用 stratified split，已改用固定 random split。")

    x_train, x_test, y_train, y_test = train_test_split(
        x_raw,
        y,
        test_size=0.25,
        random_state=MODEL_RANDOM_STATE,
        stratify=stratify_target,
    )

    if len(x_train) < 2 or len(x_test) < 1:
        raise HTTPException(status_code=400, detail="資料切分後訓練或測試資料不足。")

    ensure_not_cancelled(should_cancel)
    emit_progress(progress_callback, "selecting_models", "正在選擇候選模型。")
    model_specs = _select_model_specs(
        model_selection_mode=requested_model_selection_mode,
        selected_models=selected_models,
        problem_type=problem_type,
        features=x_raw,
        target=y_raw,
        notes=notes,
    )
    available_models = get_model_options(problem_type)
    recommendation_notes: list[str] = []
    recommended_specs = _filter_resource_intensive_specs(
        _recommend_model_specs(problem_type, x_raw, y_raw),
        features=x_raw,
        manual_selection=False,
        notes=recommendation_notes,
    )
    recommended_models = [
        _model_option_payload(spec) for spec in recommended_specs
    ]
    model_results: list[dict[str, Any]] = []
    fitted_models: dict[str, Pipeline] = {}
    predictions_by_model: dict[str, np.ndarray] = {}

    baseline_result, baseline_predictions = _fit_baseline_model(
        x_train=x_train,
        x_test=x_test,
        y_train=y_train,
        y_test=y_test,
        problem_type=problem_type,
    )
    model_results.append(baseline_result)
    predictions_by_model[str(baseline_result["model_name"])] = baseline_predictions
    notes.append("已加入 baseline model，作為判斷候選模型是否真的改善的比較基準。")

    for index, spec in enumerate(model_specs):
        ensure_not_cancelled(should_cancel)
        emit_progress(
            progress_callback,
            "training_models",
            f"正在訓練模型：{spec.label}",
            index,
            len(model_specs),
        )
        pipeline = Pipeline(
            steps=[
                ("preprocess", _build_preprocessor(x_raw)),
                ("model", spec.estimator_factory()),
            ]
        )

        try:
            pipeline, best_params, training_time_seconds = _fit_pipeline(
                pipeline=pipeline,
                spec=spec,
                x_train=x_train,
                y_train=y_train,
                problem_type=problem_type,
                automl_mode=requested_automl_mode,
                notes=notes,
            )
            predictions = np.asarray(pipeline.predict(x_test), dtype=float)
            model_path = _save_trained_model(pipeline, spec.key)
            result_payload: dict[str, Any] = {
                "model_key": spec.key,
                "model_name": spec.label,
                "model_family": spec.family,
                "r2": round(float(r2_score(y_test, predictions)), 6),
                "rmse": round(float(_root_mean_squared_error(y_test, predictions)), 6),
                "mae": round(float(mean_absolute_error(y_test, predictions)), 6),
                "training_time_seconds": round(training_time_seconds, 6),
                "automl_best_params": best_params,
                "model_path": str(model_path.relative_to(REPO_ROOT)),
                "model_url": create_artifact_url(
                    model_path,
                    root=GENERATED_OUTPUTS_DIR,
                ),
            }

            if problem_type == "classification":
                rounded_predictions = np.rint(predictions).astype(int)
                result_payload["accuracy"] = round(float(accuracy_score(y_test, rounded_predictions)), 6)
                result_payload["f1_score"] = round(
                    float(f1_score(y_test, rounded_predictions, average="weighted", zero_division=0)),
                    6,
                )
            else:
                result_payload["accuracy"] = None
                result_payload["f1_score"] = None

            fitted_models[spec.label] = pipeline
            predictions_by_model[spec.label] = predictions
            model_results.append(result_payload)
            emit_progress(
                progress_callback,
                "training_models",
                f"已完成模型：{spec.label}",
                index + 1,
                len(model_specs),
            )
        except Exception as exc:  # noqa: BLE001 - one failed model should not fail the full analysis
            notes.append(f"{spec.label} 訓練失敗，已略過：{_safe_model_error(exc)}")

    if not fitted_models:
        raise HTTPException(
            status_code=422,
            detail="所有候選模型都無法完成訓練，請更換目標欄位或移除無效特徵後再試一次。",
        )

    ensure_not_cancelled(should_cancel)
    emit_progress(
        progress_callback,
        "evaluating_models",
        "正在比較模型結果。",
        len(model_results),
        len(model_specs) + 1,
    )
    selected_chart_types = _select_chart_types(
        requested_chart_types=requested_chart_types,
        problem_type=problem_type,
        working_df=working_df,
        notes=notes,
    )
    if problem_type == "classification":
        best_result = max(
            model_results,
            key=lambda result: (
                float(result["accuracy"] or 0),
                -float(result["rmse"]),
            ),
        )
    else:
        best_result = min(model_results, key=lambda result: float(result["rmse"]))
    best_model_name = str(best_result["model_name"])
    best_predictions = predictions_by_model[best_model_name]
    feature_model_name, feature_model = _select_feature_model(fitted_models, model_results)

    ensure_not_cancelled(should_cancel)
    emit_progress(
        progress_callback,
        "generating_charts",
        "正在產生模型圖表。",
        0,
        len(selected_chart_types),
    )
    charts = _create_selected_charts(
        selected_chart_types=selected_chart_types,
        model_results=model_results,
        working_df=working_df,
        target_column=target_column,
        y_test=np.asarray(y_test, dtype=float),
        best_predictions=best_predictions,
        best_model_name=best_model_name,
        feature_model_name=feature_model_name,
        feature_model=feature_model,
        notes=notes,
    )

    if problem_type == "classification":
        notes.append(
            "此版本依需求顯示 R2、RMSE、MAE；分類目標欄位會先轉成數值標籤後計算這些指標。"
        )

    ensure_not_cancelled(should_cancel)
    emit_progress(
        progress_callback,
        "building_outputs",
        "正在保存模型結果與清理後資料。",
    )
    primary_chart = charts[0] if charts else None
    model_results_path = _save_model_results(model_results)
    cleaned_dataset_path = _save_cleaned_dataset(source_working_df, file_name)

    result = {
        "file_name": file_name,
        "target_column": target_column,
        "analysis_mode": requested_mode,
        "problem_type": problem_type,
        "row_count_used": int(len(working_df)),
        "source_row_count": source_row_count,
        "feature_count_used": int(x_raw.shape[1]),
        "model_results": model_results,
        "model_selection_mode": requested_model_selection_mode,
        "automl_mode": requested_automl_mode,
        "selected_model_keys": [spec.key for spec in model_specs],
        "available_models": available_models,
        "recommended_models": recommended_models,
        "model_results_path": str(model_results_path.relative_to(REPO_ROOT)),
        "model_results_url": create_artifact_url(
            model_results_path,
            root=GENERATED_OUTPUTS_DIR,
        ),
        "cleaned_dataset_path": str(cleaned_dataset_path.relative_to(REPO_ROOT)),
        "cleaned_dataset_url": create_artifact_url(
            cleaned_dataset_path,
            root=GENERATED_OUTPUTS_DIR,
        ),
        "chart_path": primary_chart["chart_path"] if primary_chart else "",
        "chart_url": primary_chart["chart_url"] if primary_chart else "",
        "charts": charts,
        "selected_chart_types": selected_chart_types,
        "notes": notes,
    }
    dataset_summary = analyze_dataframe(df, file_name=file_name)
    result.update(
        build_model_brief(
            dataset_summary=dataset_summary,
            model_analysis=result,
        )
    )
    return result


def _normalize_analysis_mode(analysis_mode: str) -> str:
    normalized = analysis_mode.strip().lower()
    if normalized not in ANALYSIS_MODES:
        raise HTTPException(
            status_code=400,
            detail="分析模式不支援，請選擇自動、回歸或分類。",
        )
    return normalized


def _normalize_model_selection_mode(model_selection_mode: str) -> str:
    normalized = MODEL_SELECTION_ALIASES.get(model_selection_mode.strip().lower(), model_selection_mode.strip().lower())
    if normalized not in MODEL_SELECTION_MODES:
        raise HTTPException(
            status_code=400,
            detail="模型選擇模式不支援，請選擇 auto、custom 或 manual。",
        )
    return normalized


def _normalize_automl_mode(automl_mode: str) -> str:
    normalized = automl_mode.strip().lower()
    if normalized not in AUTOML_MODES:
        raise HTTPException(
            status_code=400,
            detail="AutoML 模式不支援，請選擇 off 或 quick。",
        )
    return normalized


def _normalize_chart_types(chart_types: str) -> list[str]:
    parsed = [
        chart_type.strip().lower()
        for chart_type in chart_types.split(",")
        if chart_type.strip()
    ]
    if not parsed:
        return ["auto"]

    unsupported = [chart_type for chart_type in parsed if chart_type not in SUPPORTED_CHART_TYPES]
    if unsupported:
        raise HTTPException(
            status_code=400,
            detail=f"圖表類型不支援：{', '.join(unsupported)}。",
        )

    if "auto" in parsed:
        return ["auto"]

    return list(dict.fromkeys(parsed))


def get_model_options(problem_type: str | None = None) -> list[dict[str, Any]]:
    catalog = _model_catalog()
    if problem_type:
        catalog = [spec for spec in catalog if spec.problem_type == problem_type]
    return [_model_option_payload(spec) for spec in catalog]


def _model_option_payload(spec: ModelSpec) -> dict[str, Any]:
    return enrich_model_option({
        "key": spec.key,
        "label": spec.label,
        "problem_type": spec.problem_type,
        "family": spec.family,
        "description": spec.description,
        "complexity": spec.complexity,
    })


def _model_catalog() -> list[ModelSpec]:
    specs = [
        ModelSpec(
            key="linear_regression",
            label="線性迴歸",
            problem_type="regression",
            family="linear",
            description="快速、可解釋，適合作為連續數值預測基準。",
            complexity="low",
            estimator_factory=lambda: LinearRegression(),
        ),
        ModelSpec(
            key="ridge",
            label="Ridge 迴歸",
            problem_type="regression",
            family="linear",
            description="對多重共線性較穩定，適合中小型數值資料。",
            complexity="low",
            estimator_factory=lambda: Ridge(alpha=1.0, solver="lsqr"),
            param_grid_factory=lambda _: {"alpha": [0.1, 1.0, 10.0]},
        ),
        ModelSpec(
            key="lasso",
            label="Lasso 迴歸",
            problem_type="regression",
            family="linear",
            description="具特徵篩選效果，適合欄位較多且需要簡化模型時。",
            complexity="low",
            estimator_factory=lambda: Lasso(alpha=0.01, random_state=MODEL_RANDOM_STATE, max_iter=10000),
            param_grid_factory=lambda _: {"alpha": [0.001, 0.01, 0.1]},
        ),
        ModelSpec(
            key="elastic_net",
            label="ElasticNet 迴歸",
            problem_type="regression",
            family="linear",
            description="結合 Ridge 與 Lasso，適合欄位多且相關性高的資料。",
            complexity="medium",
            estimator_factory=lambda: ElasticNet(
                alpha=0.01,
                l1_ratio=0.35,
                random_state=MODEL_RANDOM_STATE,
                max_iter=10000,
            ),
            param_grid_factory=lambda _: {
                "alpha": [0.001, 0.01],
                "l1_ratio": [0.2, 0.5, 0.8],
            },
        ),
        ModelSpec(
            key="decision_tree_regressor",
            label="決策樹迴歸",
            problem_type="regression",
            family="tree",
            description="可捕捉非線性規則，適合探索局部決策結構。",
            complexity="medium",
            estimator_factory=lambda: DecisionTreeRegressor(
                max_depth=6,
                random_state=MODEL_RANDOM_STATE,
            ),
            param_grid_factory=lambda _: {"max_depth": [3, 6, None]},
        ),
        ModelSpec(
            key="random_forest",
            label="隨機森林",
            problem_type="regression",
            family="ensemble",
            description="穩健的非線性模型，適合混合欄位與一般表格資料。",
            complexity="medium",
            estimator_factory=lambda: RandomForestRegressor(
                n_estimators=35,
                random_state=MODEL_RANDOM_STATE,
                n_jobs=-1,
            ),
            param_grid_factory=lambda _: {
                "n_estimators": [80, 160],
                "max_depth": [6, None],
            },
        ),
        ModelSpec(
            key="extra_trees_regressor",
            label="Extra Trees 迴歸",
            problem_type="regression",
            family="ensemble",
            description="隨機化更強，常用來檢查特徵訊號與穩健性。",
            complexity="medium",
            estimator_factory=lambda: ExtraTreesRegressor(
                n_estimators=40,
                random_state=MODEL_RANDOM_STATE,
                n_jobs=-1,
            ),
            param_grid_factory=lambda _: {
                "n_estimators": [80, 160],
                "max_depth": [6, None],
            },
        ),
        ModelSpec(
            key="gradient_boosting_regressor",
            label="Gradient Boosting 迴歸",
            problem_type="regression",
            family="boosting",
            description="逐步修正誤差，常適合中小型表格資料的高精度建模。",
            complexity="high",
            estimator_factory=lambda: GradientBoostingRegressor(random_state=MODEL_RANDOM_STATE),
            param_grid_factory=lambda _: {
                "n_estimators": [80, 120],
                "learning_rate": [0.05, 0.1],
                "max_depth": [2, 3],
            },
        ),
        ModelSpec(
            key="knn_regressor",
            label="KNN 迴歸",
            problem_type="regression",
            family="distance",
            description="依鄰近樣本推估，適合低維度且樣本分布平滑的資料。",
            complexity="medium",
            estimator_factory=lambda: KNeighborsRegressor(n_neighbors=3),
            param_grid_factory=lambda train_size: {"n_neighbors": _neighbor_candidates(train_size)},
        ),
        ModelSpec(
            key="svr",
            label="SVR 支援向量迴歸",
            problem_type="regression",
            family="kernel",
            description="可捕捉非線性邊界，適合中小型低維資料探索。",
            complexity="high",
            estimator_factory=lambda: SVR(kernel="rbf", C=1.0, epsilon=0.1),
            param_grid_factory=lambda _: {"C": [0.5, 1.0], "epsilon": [0.05, 0.1]},
        ),
        ModelSpec(
            key="logistic_regression",
            label="Logistic Regression",
            problem_type="classification",
            family="linear",
            description="快速、可解釋，適合分類基準模型。",
            complexity="low",
            estimator_factory=lambda: LogisticRegression(max_iter=2000, random_state=MODEL_RANDOM_STATE),
            param_grid_factory=lambda _: {"C": [0.5, 1.0, 2.0]},
        ),
        ModelSpec(
            key="decision_tree_classifier",
            label="決策樹分類",
            problem_type="classification",
            family="tree",
            description="可解釋的非線性分類模型，適合探索規則。",
            complexity="medium",
            estimator_factory=lambda: DecisionTreeClassifier(max_depth=6, random_state=MODEL_RANDOM_STATE),
            param_grid_factory=lambda _: {"max_depth": [3, 6, None]},
        ),
        ModelSpec(
            key="random_forest_classifier",
            label="隨機森林分類",
            problem_type="classification",
            family="ensemble",
            description="穩健的表格資料分類模型，可處理非線性關係。",
            complexity="medium",
            estimator_factory=lambda: RandomForestClassifier(
                n_estimators=35,
                random_state=MODEL_RANDOM_STATE,
                n_jobs=-1,
            ),
            param_grid_factory=lambda _: {
                "n_estimators": [80, 160],
                "max_depth": [6, None],
            },
        ),
        ModelSpec(
            key="extra_trees_classifier",
            label="Extra Trees 分類",
            problem_type="classification",
            family="ensemble",
            description="強隨機化集成模型，適合檢查分類特徵穩定性。",
            complexity="medium",
            estimator_factory=lambda: ExtraTreesClassifier(
                n_estimators=40,
                random_state=MODEL_RANDOM_STATE,
                n_jobs=-1,
            ),
            param_grid_factory=lambda _: {
                "n_estimators": [80, 160],
                "max_depth": [6, None],
            },
        ),
        ModelSpec(
            key="gradient_boosting_classifier",
            label="Gradient Boosting 分類",
            problem_type="classification",
            family="boosting",
            description="逐步修正分類錯誤，適合中小型高訊號資料。",
            complexity="high",
            estimator_factory=lambda: GradientBoostingClassifier(random_state=MODEL_RANDOM_STATE),
            param_grid_factory=lambda _: {
                "n_estimators": [80, 120],
                "learning_rate": [0.05, 0.1],
                "max_depth": [2, 3],
            },
        ),
        ModelSpec(
            key="knn_classifier",
            label="KNN 分類",
            problem_type="classification",
            family="distance",
            description="依鄰近樣本投票，適合低維度且類別邊界平滑的資料。",
            complexity="medium",
            estimator_factory=lambda: KNeighborsClassifier(n_neighbors=3),
            param_grid_factory=lambda train_size: {"n_neighbors": _neighbor_candidates(train_size)},
        ),
        ModelSpec(
            key="svc",
            label="SVC 支援向量分類",
            problem_type="classification",
            family="kernel",
            description="可建立非線性分類邊界，適合中小型低維資料。",
            complexity="high",
            estimator_factory=lambda: SVC(kernel="rbf", C=1.0, gamma="scale"),
            param_grid_factory=lambda _: {"C": [0.5, 1.0, 2.0]},
        ),
    ]
    if XGBRegressor is not None:
        specs.append(
            ModelSpec(
                key="xgboost_regressor",
                label="XGBoost 迴歸",
                problem_type="regression",
                family="boosting",
                description="高效梯度提升模型，適合表格資料的高精度回歸。",
                complexity="high",
                estimator_factory=lambda: XGBRegressor(
                    n_estimators=60,
                    learning_rate=0.08,
                    max_depth=3,
                    objective="reg:squarederror",
                    random_state=MODEL_RANDOM_STATE,
                ),
                param_grid_factory=lambda _: {
                    "n_estimators": [80, 140],
                    "learning_rate": [0.05, 0.1],
                    "max_depth": [2, 3],
                },
            )
        )
    if LGBMRegressor is not None:
        specs.append(
            ModelSpec(
                key="lightgbm_regressor",
                label="LightGBM 迴歸",
                problem_type="regression",
                family="boosting",
                description="輕量化梯度提升模型，適合較大的表格資料。",
                complexity="high",
                estimator_factory=lambda: LGBMRegressor(
                    n_estimators=60,
                    learning_rate=0.08,
                    max_depth=4,
                    random_state=MODEL_RANDOM_STATE,
                    verbose=-1,
                ),
                param_grid_factory=lambda _: {
                    "n_estimators": [80, 140],
                    "learning_rate": [0.05, 0.1],
                    "max_depth": [3, 5],
                },
            )
        )
    if XGBClassifier is not None:
        specs.append(
            ModelSpec(
                key="xgboost_classifier",
                label="XGBoost 分類",
                problem_type="classification",
                family="boosting",
                description="高效梯度提升分類模型，適合表格資料分類。",
                complexity="high",
                estimator_factory=lambda: XGBClassifier(
                    n_estimators=60,
                    learning_rate=0.08,
                    max_depth=3,
                    random_state=MODEL_RANDOM_STATE,
                    eval_metric="logloss",
                ),
                param_grid_factory=lambda _: {
                    "n_estimators": [80, 140],
                    "learning_rate": [0.05, 0.1],
                    "max_depth": [2, 3],
                },
            )
        )
    if LGBMClassifier is not None:
        specs.append(
            ModelSpec(
                key="lightgbm_classifier",
                label="LightGBM 分類",
                problem_type="classification",
                family="boosting",
                description="輕量化梯度提升分類模型，適合較大的表格資料。",
                complexity="high",
                estimator_factory=lambda: LGBMClassifier(
                    n_estimators=60,
                    learning_rate=0.08,
                    max_depth=4,
                    random_state=MODEL_RANDOM_STATE,
                    verbose=-1,
                ),
                param_grid_factory=lambda _: {
                    "n_estimators": [80, 140],
                    "learning_rate": [0.05, 0.1],
                    "max_depth": [3, 5],
                },
            )
        )

    return specs


def _select_model_specs(
    model_selection_mode: str,
    selected_models: str,
    problem_type: str,
    features: pd.DataFrame,
    target: pd.Series,
    notes: list[str],
) -> list[ModelSpec]:
    if model_selection_mode == "auto" or selected_models.strip().lower() == "auto":
        specs = _recommend_model_specs(problem_type, features, target)
        specs = _filter_resource_intensive_specs(
            specs,
            features=features,
            manual_selection=False,
            notes=notes,
        )
        notes.append(
            "系統已依資料列數、特徵數、欄位型態、缺失比例與問題類型自動推薦模型。"
        )
        return specs

    catalog = {spec.key: spec for spec in _model_catalog() if spec.problem_type == problem_type}
    parsed = [
        item.strip()
        for item in selected_models.split(",")
        if item.strip()
    ]
    if not parsed:
        raise HTTPException(status_code=400, detail="手動模型選擇至少需要 1 個模型。")

    selected_specs: list[ModelSpec] = []
    unsupported: list[str] = []
    for item in parsed:
        key = _resolve_model_key(item, problem_type)
        spec = catalog.get(key)
        if spec is None:
            unsupported.append(item)
        elif spec not in selected_specs:
            selected_specs.append(spec)

    if unsupported:
        raise HTTPException(
            status_code=400,
            detail=f"模型不支援或不適合目前問題型態：{', '.join(unsupported)}。",
        )

    selected_specs = _filter_resource_intensive_specs(
        selected_specs,
        features=features,
        manual_selection=True,
        notes=notes,
    )
    notes.append(f"本次依使用者手動選擇執行 {len(selected_specs)} 個模型。")
    return selected_specs


def _filter_resource_intensive_specs(
    specs: list[ModelSpec],
    *,
    features: pd.DataFrame,
    manual_selection: bool,
    notes: list[str],
) -> list[ModelSpec]:
    row_count = int(features.shape[0])
    feature_count = int(features.shape[1])
    categorical_count = len(
        [column for column in features.columns if not pd.api.types.is_numeric_dtype(features[column])]
    )
    should_skip_slow_models = (
        row_count > SLOW_MODEL_ROW_LIMIT
        or feature_count > SLOW_MODEL_FEATURE_LIMIT
        or categorical_count > 0
    )
    if not should_skip_slow_models:
        return specs

    skipped = [spec for spec in specs if spec.key in SLOW_MODEL_KEYS]
    if not skipped:
        return specs

    retained = [spec for spec in specs if spec.key not in SLOW_MODEL_KEYS]
    skipped_labels = "、".join(spec.label for spec in skipped)
    if manual_selection and not retained:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{skipped_labels} 不適合目前資料規模或欄位型態，容易造成分析逾時。"
                "請改選樹模型、線性模型或先縮小資料後再試。"
            ),
        )

    notes.append(
        f"為避免大型或含類別欄位的資料分析逾時，已略過高成本模型：{skipped_labels}。"
    )
    return retained


def _recommend_model_specs(
    problem_type: str,
    features: pd.DataFrame,
    target: pd.Series,
) -> list[ModelSpec]:
    catalog = {spec.key: spec for spec in _model_catalog() if spec.problem_type == problem_type}
    row_count = int(features.shape[0])
    feature_count = int(features.shape[1])
    categorical_count = len([column for column in features.columns if not pd.api.types.is_numeric_dtype(features[column])])
    missing_ratio = float(features.isna().mean().mean()) if feature_count > 0 else 0
    target_unique_count = int(target.dropna().nunique())
    is_large_dataset = row_count > SLOW_MODEL_ROW_LIMIT
    is_wide_or_sparse = feature_count >= 20 or missing_ratio > 0.15

    if problem_type == "regression":
        if row_count <= 80:
            keys = ["ridge", "lasso", "elastic_net", "random_forest", "gradient_boosting_regressor", "xgboost_regressor"]
            if feature_count <= 8:
                keys.append("knn_regressor")
        elif is_large_dataset:
            keys = [
                "decision_tree_regressor",
                "random_forest",
                "extra_trees_regressor",
            ]
        elif is_wide_or_sparse:
            keys = [
                "ridge",
                "elastic_net",
                "random_forest",
                "extra_trees_regressor",
                "gradient_boosting_regressor",
                "lightgbm_regressor",
            ]
        else:
            keys = [
                "linear_regression",
                "ridge",
                "random_forest",
                "extra_trees_regressor",
                "gradient_boosting_regressor",
                "xgboost_regressor",
                "lightgbm_regressor",
            ]
            if row_count <= SLOW_MODEL_ROW_LIMIT and feature_count <= 12 and categorical_count == 0:
                keys.append("svr")
    else:
        if row_count <= 80 or target_unique_count <= 5:
            keys = [
                "logistic_regression",
                "decision_tree_classifier",
                "random_forest_classifier",
                "gradient_boosting_classifier",
                "xgboost_classifier",
            ]
            if feature_count <= 10:
                keys.append("knn_classifier")
        elif is_large_dataset:
            keys = [
                "decision_tree_classifier",
                "random_forest_classifier",
                "extra_trees_classifier",
            ]
        elif categorical_count > 0 or missing_ratio > 0.15:
            keys = [
                "logistic_regression",
                "random_forest_classifier",
                "extra_trees_classifier",
                "gradient_boosting_classifier",
                "lightgbm_classifier",
            ]
        else:
            keys = [
                "logistic_regression",
                "random_forest_classifier",
                "extra_trees_classifier",
                "gradient_boosting_classifier",
                "xgboost_classifier",
                "lightgbm_classifier",
            ]
            if row_count <= SLOW_MODEL_ROW_LIMIT and feature_count <= 12 and categorical_count == 0:
                keys.append("svc")

    return [catalog[key] for key in keys if key in catalog]


def _resolve_model_key(model_name_or_key: str, problem_type: str) -> str:
    normalized = model_name_or_key.strip().lower()
    for spec in _model_catalog():
        if spec.problem_type != problem_type:
            continue
        if normalized in {spec.key.lower(), spec.label.lower()}:
            return spec.key

    aliases = {
        "linear regression": "linear_regression",
        "線性迴歸": "linear_regression",
        "ridge": "ridge",
        "ridge 迴歸": "ridge",
        "lasso": "lasso",
        "lasso 迴歸": "lasso",
        "elasticnet": "elastic_net",
        "elastic net": "elastic_net",
        "隨機森林": "random_forest" if problem_type == "regression" else "random_forest_classifier",
        "random forest": "random_forest" if problem_type == "regression" else "random_forest_classifier",
        "gradient boosting": "gradient_boosting_regressor" if problem_type == "regression" else "gradient_boosting_classifier",
        "xgboost": "xgboost_regressor" if problem_type == "regression" else "xgboost_classifier",
        "xgb": "xgboost_regressor" if problem_type == "regression" else "xgboost_classifier",
        "lightgbm": "lightgbm_regressor" if problem_type == "regression" else "lightgbm_classifier",
        "lgbm": "lightgbm_regressor" if problem_type == "regression" else "lightgbm_classifier",
        "knn": "knn_regressor" if problem_type == "regression" else "knn_classifier",
        "svm": "svr" if problem_type == "regression" else "svc",
    }
    return aliases.get(normalized, model_name_or_key.strip())


def _select_chart_types(
    requested_chart_types: list[str],
    problem_type: str,
    working_df: pd.DataFrame,
    notes: list[str],
) -> list[str]:
    if requested_chart_types != ["auto"]:
        selected = requested_chart_types
    else:
        selected = ["model_comparison", "feature_importance", "predicted_vs_actual"]
        if problem_type == "regression":
            selected.append("residual_plot")
        notes.append("系統已依資料型態自動選擇最適合的圖表組合。")

    final_selection: list[str] = []
    for chart_type in selected:
        if chart_type == "residual_plot" and problem_type != "regression":
            notes.append("分類分析不適合殘差圖，已略過殘差圖。")
            continue
        final_selection.append(chart_type)

    return final_selection or ["model_comparison"]


def _prepare_modeling_dataframe(
    source_df: pd.DataFrame,
    *,
    target_column: str,
    problem_type: str,
    model_selection_mode: str,
    notes: list[str],
) -> pd.DataFrame:
    modeling_df = source_df.copy()
    feature_columns = [column for column in modeling_df.columns if column != target_column]
    columns_to_drop: list[str] = []
    drop_reasons: list[str] = []

    for column in feature_columns:
        series = modeling_df[column]
        column_name = str(column)
        if series.isna().all():
            columns_to_drop.append(column)
            drop_reasons.append(f"{column_name}：全欄位缺失")
            continue

        if _is_id_like_column(column_name):
            columns_to_drop.append(column)
            drop_reasons.append(f"{column_name}：識別碼欄位，不適合直接作為預測特徵")
            continue

        if not pd.api.types.is_numeric_dtype(series):
            non_null = series.dropna()
            unique_count = int(non_null.nunique(dropna=True))
            unique_ratio = unique_count / max(1, int(len(non_null)))
            if unique_count >= HIGH_CARDINALITY_MIN_UNIQUE and unique_ratio >= HIGH_CARDINALITY_RATIO:
                columns_to_drop.append(column)
                drop_reasons.append(f"{column_name}：高基數文字欄位，避免產生過大的 one-hot 矩陣")

    if columns_to_drop:
        modeling_df = modeling_df.drop(columns=columns_to_drop)
        preview = "；".join(drop_reasons[:6])
        if len(drop_reasons) > 6:
            preview += f"；另有 {len(drop_reasons) - 6} 欄"
        notes.append(f"模型訓練已排除不適合建模的欄位：{preview}。原始資料與摘要未被刪改。")

    max_rows = (
        MAX_AUTO_MODEL_TRAIN_ROWS
        if model_selection_mode == "auto"
        else MAX_CUSTOM_MODEL_TRAIN_ROWS
    )
    if len(modeling_df) > max_rows:
        sampled_df = _sample_modeling_dataframe(
            modeling_df,
            target_column=target_column,
            problem_type=problem_type,
            max_rows=max_rows,
        )
        notes.append(
            f"原始有效訓練資料 {len(modeling_df)} 筆；為避免雲端服務逾時，"
            f"模型比較使用固定 random seed 從真實資料抽樣 {len(sampled_df)} 筆。"
        )
        modeling_df = sampled_df

    return modeling_df


def _sample_modeling_dataframe(
    df: pd.DataFrame,
    *,
    target_column: str,
    problem_type: str,
    max_rows: int,
) -> pd.DataFrame:
    stratify_target: pd.Series | None = None
    if problem_type == "classification":
        target_counts = df[target_column].value_counts(dropna=False)
        if (
            len(target_counts) >= 2
            and int(target_counts.min()) >= 2
            and len(target_counts) <= max(2, max_rows // 2)
        ):
            stratify_target = df[target_column]

    sampled_df, _ = train_test_split(
        df,
        train_size=max_rows,
        random_state=MODEL_RANDOM_STATE,
        stratify=stratify_target,
    )
    return sampled_df.sort_index()


def _is_id_like_column(column_name: str) -> bool:
    normalized = column_name.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in ID_LIKE_COLUMN_NAMES:
        return True
    return normalized.endswith("_id") or normalized.endswith("_uuid") or normalized.endswith("_guid")


def _infer_problem_type(target: pd.Series) -> str:
    non_null_target = target.dropna()

    if not pd.api.types.is_numeric_dtype(non_null_target):
        return "classification"

    unique_count = int(non_null_target.nunique())
    row_count = int(non_null_target.shape[0])
    if unique_count <= 10 and unique_count / max(row_count, 1) <= 0.2:
        return "classification"

    return "regression"


def _prepare_target(target: pd.Series, problem_type: str) -> tuple[np.ndarray, list[str]]:
    notes: list[str] = []

    if problem_type == "classification":
        encoded_target, uniques = pd.factorize(target.astype("string"), sort=True)
        notes.append(f"分類目標欄位已轉換為 {len(uniques)} 個數值標籤。")
        return encoded_target.astype(float), notes

    numeric_target = pd.to_numeric(target, errors="coerce")
    valid_mask = numeric_target.notna()
    if not valid_mask.all():
        raise HTTPException(status_code=400, detail="回歸目標欄位包含無法轉換成數值的資料。")

    return numeric_target.to_numpy(dtype=float), notes


def _build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    numeric_features = features.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    categorical_features = [column for column in features.columns if column not in numeric_features]

    transformers: list[tuple[str, Pipeline, list[str]]] = []
    if numeric_features:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            )
        )

    if categorical_features:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("to_string", FunctionTransformer(_to_string_array)),
                        (
                            "encoder",
                            OneHotEncoder(
                                handle_unknown="infrequent_if_exist",
                                max_categories=MAX_ONE_HOT_CATEGORIES,
                            ),
                        ),
                    ]
                ),
                categorical_features,
            )
        )

    return ColumnTransformer(transformers=transformers, remainder="drop")


def _to_string_array(values: Any) -> np.ndarray:
    return np.asarray(values).astype(str)


def _fit_pipeline(
    pipeline: Pipeline,
    spec: ModelSpec,
    x_train: pd.DataFrame,
    y_train: np.ndarray,
    problem_type: str,
    automl_mode: str,
    notes: list[str],
) -> tuple[Pipeline, dict[str, Any], float]:
    started_at = perf_counter()
    best_params: dict[str, Any] = {}

    if automl_mode == "quick" and spec.param_grid_factory is not None:
        param_grid = spec.param_grid_factory(len(x_train))
        param_grid = {
            f"model__{key}": value
            for key, value in param_grid.items()
            if value
        }
        cv_folds = _cv_folds(problem_type, y_train)
        if param_grid and cv_folds >= 2:
            scoring = "accuracy" if problem_type == "classification" else "neg_root_mean_squared_error"
            try:
                search = GridSearchCV(
                    estimator=pipeline,
                    param_grid=param_grid,
                    scoring=scoring,
                    cv=cv_folds,
                    n_jobs=1,
                    error_score="raise",
                )
                search.fit(x_train, y_train)
                training_time_seconds = perf_counter() - started_at
                best_params = {
                    key.replace("model__", ""): _jsonable_param(value)
                    for key, value in search.best_params_.items()
                }
                return search.best_estimator_, best_params, training_time_seconds
            except Exception as exc:  # noqa: BLE001 - AutoML fallback must keep the main model run usable
                notes.append(f"{spec.label} AutoML 調參失敗，已改用預設參數訓練：{exc}")

    pipeline.fit(x_train, y_train)
    training_time_seconds = perf_counter() - started_at
    return pipeline, best_params, training_time_seconds


def _safe_model_error(exc: Exception) -> str:
    message = str(exc).strip().splitlines()[0] if str(exc).strip() else exc.__class__.__name__
    if len(message) > 180:
        message = f"{message[:177]}..."
    return message


def _cv_folds(problem_type: str, y_train: np.ndarray) -> int:
    if len(y_train) < 6:
        return 2

    if problem_type == "classification":
        _, counts = np.unique(y_train, return_counts=True)
        if int(counts.min()) < 2:
            return 1
        return max(2, min(3, int(counts.min())))

    return 3


def _neighbor_candidates(train_size: int) -> list[int]:
    candidates = [3, 5, 7]
    max_neighbors = max(1, train_size - 1)
    return [candidate for candidate in candidates if candidate <= max_neighbors] or [1]


def _jsonable_param(value: Any) -> Any:
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    return value


def _save_trained_model(model: Pipeline, model_key: str) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / f"{model_key}_{uuid4().hex}.joblib"
    joblib.dump(model, model_path)
    return model_path


def _save_model_results(model_results: list[dict[str, Any]]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    model_results_path = REPORT_DIR / f"model_results_{uuid4().hex}.xlsx"
    rows = []
    for result in model_results:
        row = dict(result)
        row["automl_best_params"] = json.dumps(row.get("automl_best_params") or {}, ensure_ascii=False)
        rows.append(row)
    pd.DataFrame(rows).to_excel(model_results_path, index=False)
    return model_results_path


def _save_cleaned_dataset(working_df: pd.DataFrame, file_name: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file_name).stem.replace(" ", "_") or "dataset"
    cleaned_dataset_path = DATA_DIR / f"cleaned_{safe_name}_{uuid4().hex}.csv"
    working_df.to_csv(cleaned_dataset_path, index=False)
    return cleaned_dataset_path


def _fit_baseline_model(
    *,
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: np.ndarray,
    y_test: np.ndarray,
    problem_type: str,
) -> tuple[dict[str, Any], np.ndarray]:
    started = perf_counter()
    if problem_type == "classification":
        estimator = DummyClassifier(strategy="most_frequent")
        model_key = "baseline_classifier"
        model_name = "Baseline 分類"
        family = "baseline"
    else:
        estimator = DummyRegressor(strategy="median")
        model_key = "baseline_regressor"
        model_name = "Baseline 回歸"
        family = "baseline"

    estimator.fit(x_train, y_train)
    predictions = np.asarray(estimator.predict(x_test), dtype=float)
    training_time_seconds = perf_counter() - started
    model_path = _save_trained_model(estimator, model_key)
    payload: dict[str, Any] = {
        "model_key": model_key,
        "model_name": model_name,
        "model_family": family,
        "r2": round(float(r2_score(y_test, predictions)), 6),
        "rmse": round(float(_root_mean_squared_error(y_test, predictions)), 6),
        "mae": round(float(mean_absolute_error(y_test, predictions)), 6),
        "training_time_seconds": round(training_time_seconds, 6),
        "automl_best_params": {},
        "model_path": str(model_path.relative_to(REPO_ROOT)),
        "model_url": create_artifact_url(
            model_path,
            root=GENERATED_OUTPUTS_DIR,
        ),
    }
    if problem_type == "classification":
        rounded_predictions = np.rint(predictions).astype(int)
        payload["accuracy"] = round(float(accuracy_score(y_test, rounded_predictions)), 6)
        payload["f1_score"] = round(
            float(f1_score(y_test, rounded_predictions, average="weighted", zero_division=0)),
            6,
        )
    else:
        payload["accuracy"] = None
        payload["f1_score"] = None
    return payload, predictions


def _root_mean_squared_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def _select_feature_model(
    fitted_models: dict[str, Pipeline],
    model_results: list[dict[str, Any]],
) -> tuple[str, Pipeline | None]:
    ordered_results = sorted(
        model_results,
        key=lambda result: (
            -float(result.get("accuracy") or 0),
            float(result["rmse"]),
        ),
    )
    for result in ordered_results:
        model_name = str(result["model_name"])
        model = fitted_models.get(model_name)
        if model is None:
            continue
        estimator = model.named_steps["model"]
        if hasattr(estimator, "feature_importances_") or hasattr(estimator, "coef_"):
            return model_name, model

    return "", None


def _create_selected_charts(
    selected_chart_types: list[str],
    model_results: list[dict[str, float | str]],
    working_df: pd.DataFrame,
    target_column: str,
    y_test: np.ndarray,
    best_predictions: np.ndarray,
    best_model_name: str,
    feature_model_name: str,
    feature_model: Pipeline | None,
    notes: list[str],
) -> list[dict[str, str]]:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    charts: list[dict[str, str]] = []

    for chart_type in selected_chart_types:
        chart_path: Path | None = None
        if chart_type == "model_comparison":
            chart_path = _create_model_comparison_chart(model_results)
        elif chart_type == "feature_importance":
            chart_path = _create_feature_importance_chart(feature_model, feature_model_name)
        elif chart_type == "predicted_vs_actual":
            chart_path = _create_predicted_vs_actual_chart(
                y_test=y_test,
                predictions=best_predictions,
                model_name=best_model_name,
            )
        elif chart_type == "residual_plot":
            chart_path = _create_residual_plot(
                y_test=y_test,
                predictions=best_predictions,
                model_name=best_model_name,
            )

        if chart_path is None:
            notes.append(f"{CHART_TITLES.get(chart_type, chart_type)} 無法產生，已略過。")
            continue

        charts.append(_chart_payload(chart_type, chart_path))

    if not charts:
        chart_path = _create_model_comparison_chart(model_results)
        charts.append(_chart_payload("model_comparison", chart_path))
        notes.append("指定圖表皆無法產生，已改用模型比較圖。")

    return charts


def _chart_payload(chart_type: str, chart_path: Path) -> dict[str, str]:
    return {
        "chart_type": chart_type,
        "title": CHART_TITLES[chart_type],
        "chart_path": str(chart_path.relative_to(REPO_ROOT)),
        "chart_url": create_artifact_url(
            chart_path,
            root=GENERATED_OUTPUTS_DIR,
        ),
    }


def _create_model_comparison_chart(
    model_results: list[dict[str, float | str]],
) -> Path:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    chart_path = CHART_DIR / f"model_comparison_{uuid4().hex}.png"

    model_names = [str(result["model_name"]) for result in model_results]
    rmse_values = [float(result["rmse"]) for result in model_results]
    mae_values = [float(result["mae"]) for result in model_results]

    x_positions = np.arange(len(model_names))
    width = 0.36

    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.bar(x_positions - width / 2, rmse_values, width, label="RMSE", color="#1d4ed8")
    ax.bar(x_positions + width / 2, mae_values, width, label="MAE", color="#0f766e")
    ax.set_title("模型比較圖", fontsize=18)
    ax.set_ylabel("誤差數值", fontsize=13)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_names, rotation=12, ha="right", fontsize=12)
    ax.tick_params(axis="y", labelsize=11)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=12)
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)

    return chart_path


def _create_feature_importance_chart(
    model: Pipeline | None,
    model_name: str,
) -> Path | None:
    if model is None:
        return None

    estimator = model.named_steps["model"]
    values = getattr(estimator, "feature_importances_", None)
    chart_title = f"特徵重要性：{model_name}"
    if values is None and hasattr(estimator, "coef_"):
        values = np.ravel(np.abs(estimator.coef_))
        chart_title = f"係數重要性：{model_name}"

    if values is None:
        return None

    feature_names = _get_feature_names(model)
    if len(feature_names) != len(values):
        feature_names = [f"特徵 {index + 1}" for index in range(len(values))]

    importance_df = (
        pd.DataFrame({"feature": feature_names, "importance": values})
        .sort_values("importance", ascending=False)
        .head(12)
        .sort_values("importance", ascending=True)
    )

    chart_path = CHART_DIR / f"feature_importance_{uuid4().hex}.png"
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(importance_df["feature"], importance_df["importance"], color="#0f766e")
    ax.set_title(chart_title, fontsize=18)
    ax.set_xlabel("重要性", fontsize=13)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)

    return chart_path


def _create_predicted_vs_actual_chart(
    y_test: np.ndarray,
    predictions: np.ndarray,
    model_name: str,
) -> Path:
    chart_path = CHART_DIR / f"predicted_vs_actual_{uuid4().hex}.png"
    fig, ax = plt.subplots(figsize=(10.5, 7))
    ax.scatter(y_test, predictions, color="#1d4ed8", alpha=0.78, s=70)
    min_value = float(min(np.min(y_test), np.min(predictions)))
    max_value = float(max(np.max(y_test), np.max(predictions)))
    ax.plot([min_value, max_value], [min_value, max_value], color="#b7791f", linestyle="--")
    ax.set_title(f"預測值與實際值：{model_name}", fontsize=18)
    ax.set_xlabel("實際值", fontsize=13)
    ax.set_ylabel("預測值", fontsize=13)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)

    return chart_path


def _create_residual_plot(
    y_test: np.ndarray,
    predictions: np.ndarray,
    model_name: str,
) -> Path:
    chart_path = CHART_DIR / f"residual_plot_{uuid4().hex}.png"
    residuals = y_test - predictions

    fig, ax = plt.subplots(figsize=(10.5, 7))
    ax.scatter(predictions, residuals, color="#0f766e", alpha=0.78, s=70)
    ax.axhline(0, color="#b7791f", linestyle="--")
    ax.set_title(f"殘差圖：{model_name}", fontsize=18)
    ax.set_xlabel("預測值", fontsize=13)
    ax.set_ylabel("殘差", fontsize=13)
    ax.tick_params(axis="both", labelsize=11)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)

    return chart_path


def _get_feature_names(model: Pipeline) -> list[str]:
    preprocessor = model.named_steps["preprocess"]
    try:
        return [str(name).replace("numeric__", "").replace("categorical__", "") for name in preprocessor.get_feature_names_out()]
    except Exception:  # noqa: BLE001 - fallback only for feature-name compatibility
        return []


def _problem_type_label(problem_type: str) -> str:
    return "分類" if problem_type == "classification" else "回歸"
