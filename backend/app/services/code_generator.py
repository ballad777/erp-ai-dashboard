from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
from fastapi import HTTPException, UploadFile

from app.services.artifact_access import create_artifact_url
from app.services.dataset_analyzer import merge_dataframes, read_uploaded_dataframe
from app.services.model_runner import (
    REPO_ROOT,
    _infer_problem_type,
    _model_catalog,
    _normalize_analysis_mode,
    _normalize_chart_types,
    _prepare_target,
    _problem_type_label,
    _resolve_model_key,
    _select_chart_types,
)

GENERATED_OUTPUTS_DIR = REPO_ROOT / "generated_outputs"
CODE_DIR = GENERATED_OUTPUTS_DIR / "code"
DATA_DIR = GENERATED_OUTPUTS_DIR / "data"

MODEL_NAME_ALIASES = {
    "linear_regression": "線性迴歸",
    "linear regression": "線性迴歸",
    "線性迴歸": "線性迴歸",
    "ridge": "Ridge 迴歸",
    "ridge_regression": "Ridge 迴歸",
    "ridge 迴歸": "Ridge 迴歸",
    "Ridge 迴歸": "Ridge 迴歸",
    "lasso": "Lasso 迴歸",
    "lasso_regression": "Lasso 迴歸",
    "lasso 迴歸": "Lasso 迴歸",
    "Lasso 迴歸": "Lasso 迴歸",
    "random_forest": "隨機森林",
    "random forest": "隨機森林",
    "隨機森林": "隨機森林",
}


async def generate_uploaded_code_artifacts(
    file: UploadFile,
    target_column: str,
    model_name: str,
    analysis_mode: str = "auto",
    chart_types: str = "auto",
) -> dict[str, Any]:
    df, file_name = await read_uploaded_dataframe(file)
    return generate_code_artifacts(
        df=df,
        file_name=file_name,
        target_column=target_column,
        model_name=model_name,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        notes=[],
    )


async def generate_uploaded_merged_code_artifacts(
    files: list[UploadFile],
    target_column: str,
    model_name: str,
    analysis_mode: str = "auto",
    chart_types: str = "auto",
) -> dict[str, Any]:
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="合併程式碼生成至少需要 2 個檔案。")

    loaded_datasets: list[tuple[str, pd.DataFrame]] = []
    skipped_files: list[str] = []

    for file in files:
        file_name = file.filename or "未命名檔案"
        try:
            df, parsed_file_name = await read_uploaded_dataframe(file)
            loaded_datasets.append((parsed_file_name, df))
        except HTTPException as exc:
            skipped_files.append(f"{file_name}：{exc.detail}")

    if len(loaded_datasets) < 2:
        raise HTTPException(
            status_code=400,
            detail="成功讀取的檔案不足 2 個，無法產生合併分析程式碼。",
        )

    merged_df, merge_metadata = merge_dataframes(loaded_datasets)
    notes = [
        *merge_metadata["merge_notes"],
        *([f"以下檔案無法讀取，已略過：{'；'.join(skipped_files)}"] if skipped_files else []),
    ]
    return generate_code_artifacts(
        df=merged_df,
        file_name="merged_dataset.csv",
        target_column=target_column,
        model_name=model_name,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        notes=notes,
    )


def generate_code_artifacts(
    df: pd.DataFrame,
    file_name: str,
    target_column: str,
    model_name: str,
    analysis_mode: str = "auto",
    chart_types: str = "auto",
    notes: list[str] | None = None,
) -> dict[str, Any]:
    CODE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if target_column not in df.columns:
        raise HTTPException(status_code=400, detail="指定的目標欄位不存在，無法生成程式碼。")

    requested_mode = _normalize_analysis_mode(analysis_mode)
    requested_chart_types = _normalize_chart_types(chart_types)

    working_df = df.dropna(subset=[target_column]).copy()
    if working_df.empty:
        raise HTTPException(status_code=400, detail="目標欄位全部都是缺失值，無法生成程式碼。")

    inferred_problem_type = _infer_problem_type(working_df[target_column])
    problem_type = inferred_problem_type if requested_mode == "auto" else requested_mode
    _prepare_target(working_df[target_column], problem_type)
    normalized_model_name = _normalize_model_name(model_name, problem_type)

    generation_notes = list(notes or [])
    if requested_mode == "auto":
        generation_notes.append(
            f"系統自動判斷生成程式碼適合使用「{_problem_type_label(problem_type)}」分析。"
        )
    elif requested_mode != inferred_problem_type:
        generation_notes.append(
            f"系統原本判斷較適合「{_problem_type_label(inferred_problem_type)}」，"
            f"本次依使用者選擇生成「{_problem_type_label(problem_type)}」程式碼。"
        )

    selected_chart_types = _select_chart_types(
        requested_chart_types=requested_chart_types,
        problem_type=problem_type,
        working_df=working_df,
        notes=generation_notes,
    )

    run_id = uuid4().hex
    safe_name = _safe_stem(file_name)
    data_path = DATA_DIR / f"{safe_name}_{run_id}.csv"
    python_path = CODE_DIR / f"generated_code_{run_id}.py"
    notebook_path = CODE_DIR / f"notebook_{run_id}.ipynb"

    df.to_csv(data_path, index=False)

    code = _build_python_code(
        data_path=data_path,
        target_column=target_column,
        model_name=normalized_model_name,
        problem_type=problem_type,
        selected_chart_types=selected_chart_types,
    )
    notebook_content = _build_notebook_content(
        code=code,
        file_name=file_name,
        target_column=target_column,
        model_name=normalized_model_name,
    )
    python_path.write_text(code, encoding="utf-8")
    notebook_path.write_text(notebook_content, encoding="utf-8")

    return {
        "file_name": file_name,
        "target_column": target_column,
        "model_name": normalized_model_name,
        "analysis_mode": requested_mode,
        "problem_type": problem_type,
        "selected_chart_types": selected_chart_types,
        "python_path": str(python_path.relative_to(REPO_ROOT)),
        "python_url": create_artifact_url(
            python_path,
            root=GENERATED_OUTPUTS_DIR,
        ),
        "python_content": code,
        "notebook_path": str(notebook_path.relative_to(REPO_ROOT)),
        "notebook_url": create_artifact_url(
            notebook_path,
            root=GENERATED_OUTPUTS_DIR,
        ),
        "notebook_content": notebook_content,
        "dataset_path": str(data_path.relative_to(REPO_ROOT)),
        "notes": generation_notes,
    }


def _normalize_model_name(model_name: str, problem_type: str) -> str:
    resolved_key = _resolve_model_key(model_name, problem_type)
    for spec in _model_catalog():
        if spec.problem_type == problem_type and spec.key == resolved_key:
            return spec.label

    supported = "、".join(
        spec.label for spec in _model_catalog() if spec.problem_type == problem_type
    )
    raise HTTPException(status_code=400, detail=f"不支援的模型名稱，請選擇：{supported}。")


def _safe_stem(file_name: str) -> str:
    stem = Path(file_name).stem or "dataset"
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_")
    return safe or "dataset"


def _build_python_code(
    data_path: Path,
    target_column: str,
    model_name: str,
    problem_type: str,
    selected_chart_types: list[str],
) -> str:
    relative_data_path = data_path.relative_to(REPO_ROOT).as_posix()
    return f'''# Generated by 智能金融資料分析
# 這份程式碼可在專案根目錄或 generated_outputs/code/ 內執行。
from __future__ import annotations

import os
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
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
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


MPLCONFIGDIR = Path.cwd() / "generated_outputs" / ".matplotlib"
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = [
    "Heiti TC",
    "Arial Unicode MS",
    "Hiragino Sans",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


DATA_RELATIVE_PATH = Path({json.dumps(relative_data_path, ensure_ascii=False)})
TARGET_COLUMN = {json.dumps(target_column, ensure_ascii=False)}
PRIMARY_MODEL_NAME = {json.dumps(model_name, ensure_ascii=False)}
PROBLEM_TYPE = {json.dumps(problem_type, ensure_ascii=False)}
REQUESTED_CHARTS = {json.dumps(selected_chart_types, ensure_ascii=False)}
RANDOM_STATE = 42


def find_project_root() -> Path:
    candidates = []
    try:
        candidates.append(Path(__file__).resolve().parents[2])
    except NameError:
        pass

    cwd = Path.cwd().resolve()
    candidates.extend([cwd, *cwd.parents])
    for candidate in candidates:
        if (candidate / DATA_RELATIVE_PATH).exists():
            return candidate

    return candidates[0]


PROJECT_ROOT = find_project_root()
DATA_PATH = PROJECT_ROOT / DATA_RELATIVE_PATH
CHART_DIR = PROJECT_ROOT / "generated_outputs" / "charts"


def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"找不到資料檔：{{DATA_PATH}}")
    return pd.read_csv(DATA_PATH)


def prepare_target(target: pd.Series) -> np.ndarray:
    if PROBLEM_TYPE == "classification":
        encoded_target, _ = pd.factorize(target.astype("string"), sort=True)
        return encoded_target.astype(float)

    numeric_target = pd.to_numeric(target, errors="coerce")
    if numeric_target.isna().any():
        raise ValueError("回歸目標欄位包含無法轉換成數值的資料。")
    return numeric_target.to_numpy(dtype=float)


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    numeric_features = features.select_dtypes(include=[np.number, "bool"]).columns.tolist()
    categorical_features = [
        column for column in features.columns if column not in numeric_features
    ]

    transformers = []
    if numeric_features:
        transformers.append(
            (
                "numeric",
                Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))]),
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
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            )
        )

    return ColumnTransformer(transformers=transformers, remainder="drop")


def build_models() -> dict[str, object]:
    if PROBLEM_TYPE == "classification":
        return {{
            "Logistic Regression": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
            "決策樹分類": DecisionTreeClassifier(max_depth=6, min_samples_leaf=3, random_state=RANDOM_STATE),
            "隨機森林分類": RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                min_samples_leaf=3,
                max_features="sqrt",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            "Extra Trees 分類": ExtraTreesClassifier(
                n_estimators=100,
                max_depth=12,
                min_samples_leaf=3,
                max_features="sqrt",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            "Gradient Boosting 分類": GradientBoostingClassifier(random_state=RANDOM_STATE),
            "KNN 分類": KNeighborsClassifier(n_neighbors=3),
            "SVC 支援向量分類": SVC(kernel="rbf", C=1.0, gamma="scale"),
        }}

    return {{
        "線性迴歸": LinearRegression(),
        "Ridge 迴歸": Ridge(alpha=1.0, random_state=RANDOM_STATE),
        "Lasso 迴歸": Lasso(alpha=0.01, random_state=RANDOM_STATE, max_iter=10000),
        "ElasticNet 迴歸": ElasticNet(
            alpha=0.01,
            l1_ratio=0.35,
            random_state=RANDOM_STATE,
            max_iter=10000,
        ),
        "決策樹迴歸": DecisionTreeRegressor(max_depth=6, min_samples_leaf=3, random_state=RANDOM_STATE),
        "隨機森林": RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            min_samples_leaf=3,
            max_features="sqrt",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "Extra Trees 迴歸": ExtraTreesRegressor(
            n_estimators=100,
            max_depth=12,
            min_samples_leaf=3,
            max_features="sqrt",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "Gradient Boosting 迴歸": GradientBoostingRegressor(random_state=RANDOM_STATE),
        "KNN 迴歸": KNeighborsRegressor(n_neighbors=3),
        "SVR 支援向量迴歸": SVR(kernel="rbf", C=1.0, epsilon=0.1),
    }}


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {{
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
    }}


def get_feature_names(model: Pipeline) -> list[str]:
    preprocessor = model.named_steps["preprocess"]
    try:
        return [
            str(name).replace("numeric__", "").replace("categorical__", "")
            for name in preprocessor.get_feature_names_out()
        ]
    except Exception:
        return []


def save_model_comparison(model_results: pd.DataFrame) -> Path:
    chart_path = CHART_DIR / "generated_model_comparison.png"
    x_positions = np.arange(len(model_results))
    width = 0.36

    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.bar(
        x_positions - width / 2,
        model_results["rmse"],
        width,
        label="RMSE",
        color="#1d4ed8",
    )
    ax.bar(
        x_positions + width / 2,
        model_results["mae"],
        width,
        label="MAE",
        color="#0f766e",
    )
    ax.set_title("模型比較圖", fontsize=18)
    ax.set_ylabel("誤差數值")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(model_results["model_name"], rotation=12, ha="right")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
    return chart_path


def save_feature_importance(model: Pipeline) -> Path | None:
    estimator = model.named_steps["model"]
    feature_names = get_feature_names(model)
    values = None
    title = "特徵重要性"

    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        values = np.ravel(np.abs(estimator.coef_))
        title = "模型係數重要性"

    if values is None:
        print("此模型沒有可視覺化的特徵重要性，已略過。")
        return None

    if len(feature_names) != len(values):
        feature_names = [f"特徵 {{index + 1}}" for index in range(len(values))]

    importance_df = (
        pd.DataFrame({{"feature": feature_names, "importance": values}})
        .sort_values("importance", ascending=False)
        .head(12)
        .sort_values("importance", ascending=True)
    )

    chart_path = CHART_DIR / "generated_feature_importance.png"
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(importance_df["feature"], importance_df["importance"], color="#0f766e")
    ax.set_title(title, fontsize=18)
    ax.set_xlabel("重要性")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
    return chart_path


def save_predicted_vs_actual(y_test: np.ndarray, predictions: np.ndarray) -> Path:
    chart_path = CHART_DIR / "generated_predicted_vs_actual.png"
    fig, ax = plt.subplots(figsize=(10.5, 7))
    ax.scatter(y_test, predictions, color="#1d4ed8", alpha=0.78, s=70)
    min_value = float(min(np.min(y_test), np.min(predictions)))
    max_value = float(max(np.max(y_test), np.max(predictions)))
    ax.plot([min_value, max_value], [min_value, max_value], color="#b7791f", linestyle="--")
    ax.set_title(f"預測值與實際值：{{PRIMARY_MODEL_NAME}}", fontsize=18)
    ax.set_xlabel("實際值")
    ax.set_ylabel("預測值")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
    return chart_path


def save_residual_plot(y_test: np.ndarray, predictions: np.ndarray) -> Path | None:
    if PROBLEM_TYPE != "regression":
        print("分類分析不適合殘差圖，已略過。")
        return None

    chart_path = CHART_DIR / "generated_residual_plot.png"
    residuals = y_test - predictions
    fig, ax = plt.subplots(figsize=(10.5, 7))
    ax.scatter(predictions, residuals, color="#0f766e", alpha=0.78, s=70)
    ax.axhline(0, color="#b7791f", linestyle="--")
    ax.set_title(f"殘差圖：{{PRIMARY_MODEL_NAME}}", fontsize=18)
    ax.set_xlabel("預測值")
    ax.set_ylabel("殘差")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
    return chart_path


def main() -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    df = load_dataset()
    working_df = df.dropna(subset=[TARGET_COLUMN]).copy()
    y = prepare_target(working_df[TARGET_COLUMN])
    x = working_df.drop(columns=[TARGET_COLUMN]).dropna(axis=1, how="all")

    if x.empty:
        raise ValueError("除了目標欄位外沒有可用特徵。")

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
    )

    models = build_models()
    if PRIMARY_MODEL_NAME not in models:
        raise ValueError(f"不支援的模型：{{PRIMARY_MODEL_NAME}}")

    model_results = []
    fitted_models = {{}}
    predictions_by_model = {{}}

    for model_name, estimator in models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocess", build_preprocessor(x)),
                ("model", estimator),
            ]
        )
        started_at = perf_counter()
        pipeline.fit(x_train, y_train)
        training_time = perf_counter() - started_at
        predictions = np.asarray(pipeline.predict(x_test), dtype=float)
        metrics = evaluate_model(y_test, predictions)
        model_results.append(
            {{
                "model_name": model_name,
                **metrics,
                "training_time_seconds": training_time,
            }}
        )
        fitted_models[model_name] = pipeline
        predictions_by_model[model_name] = predictions

    model_results_df = pd.DataFrame(model_results)
    primary_model = fitted_models[PRIMARY_MODEL_NAME]
    primary_predictions = predictions_by_model[PRIMARY_MODEL_NAME]

    print("模型評估結果")
    print(model_results_df)

    if "model_comparison" in REQUESTED_CHARTS:
        print(f"已產生：{{save_model_comparison(model_results_df)}}")
    if "feature_importance" in REQUESTED_CHARTS:
        chart_path = save_feature_importance(primary_model)
        if chart_path:
            print(f"已產生：{{chart_path}}")
    if "predicted_vs_actual" in REQUESTED_CHARTS:
        print(f"已產生：{{save_predicted_vs_actual(y_test, primary_predictions)}}")
    if "residual_plot" in REQUESTED_CHARTS:
        chart_path = save_residual_plot(y_test, primary_predictions)
        if chart_path:
            print(f"已產生：{{chart_path}}")


if __name__ == "__main__":
    main()
'''


def _build_notebook_content(
    code: str,
    file_name: str,
    target_column: str,
    model_name: str,
) -> str:
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# 智能金融資料分析自動生成 Notebook\\n",
                    f"資料集：{file_name}\\n",
                    f"目標欄位：{target_column}\\n",
                    f"主要模型：{model_name}\\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + "\n" for line in code.splitlines()],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return json.dumps(notebook, ensure_ascii=False, indent=2)
