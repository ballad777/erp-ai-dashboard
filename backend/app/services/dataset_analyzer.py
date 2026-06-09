from __future__ import annotations

from io import BytesIO
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd
from fastapi import HTTPException, UploadFile

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


async def analyze_uploaded_dataset(file: UploadFile) -> dict[str, Any]:
    df, file_name = await read_uploaded_dataframe(file)

    started_at = perf_counter()
    result = _summarize_dataframe(df)
    elapsed = perf_counter() - started_at

    result["file_name"] = file_name
    result["analysis_time_seconds"] = round(elapsed, 4)
    return result


async def analyze_multiple_uploaded_datasets(files: list[UploadFile]) -> dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="請至少上傳一個檔案。")

    dataset_results: list[dict[str, Any]] = []
    loaded_datasets: list[tuple[str, pd.DataFrame]] = []

    for file in files:
        file_name = file.filename or "未命名檔案"
        try:
            df, parsed_file_name = await read_uploaded_dataframe(file)
            analysis = analyze_dataframe(df, file_name=parsed_file_name)
            dataset_results.append(
                {
                    "file_name": parsed_file_name,
                    "success": True,
                    "analysis": analysis,
                    "error": None,
                }
            )
            loaded_datasets.append((parsed_file_name, df))
        except HTTPException as exc:
            dataset_results.append(
                {
                    "file_name": file_name,
                    "success": False,
                    "analysis": None,
                    "error": str(exc.detail),
                }
            )

    merged_analysis: dict[str, Any] | None = None
    notes: list[str] = []

    if len(loaded_datasets) >= 2:
        merged_df, merge_metadata = merge_dataframes(loaded_datasets)
        merged_analysis = analyze_dataframe(merged_df, file_name="merged_dataset.csv")
        merged_analysis.update(merge_metadata)
    elif len(loaded_datasets) == 1:
        notes.append("只有 1 個檔案成功讀取，因此尚未建立合併分析。")
    else:
        notes.append("沒有檔案成功讀取，請檢查檔案格式與內容。")

    return {
        "datasets": dataset_results,
        "merged": merged_analysis,
        "notes": notes,
    }


async def read_uploaded_dataframe(file: UploadFile) -> tuple[pd.DataFrame, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="缺少上傳檔案名稱。")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="不支援的檔案格式，請上傳 CSV、XLSX 或 XLS 檔案。",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="上傳檔案是空的。")

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="上傳檔案過大，最大限制為 25 MB。",
        )

    df = _read_dataset(content, suffix)

    if df.empty:
        raise HTTPException(status_code=400, detail="資料集沒有任何資料列。")

    return df, file.filename


def analyze_dataframe(df: pd.DataFrame, file_name: str = "dataset.csv") -> dict[str, Any]:
    if df.empty:
        raise ValueError("資料集沒有任何資料列。")

    result = _summarize_dataframe(df)
    result["file_name"] = file_name
    result["analysis_time_seconds"] = 0
    return result


def merge_dataframes(
    datasets: list[tuple[str, pd.DataFrame]],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if len(datasets) < 2:
        raise ValueError("合併分析至少需要 2 個資料集。")

    source_file_column = _unique_metadata_column(
        datasets=datasets,
        preferred_name="source_file",
    )
    source_row_column = _unique_metadata_column(
        datasets=datasets,
        preferred_name="source_row_number",
    )

    prepared_frames: list[pd.DataFrame] = []
    source_row_counts: dict[str, int] = {}
    column_sets: list[set[str]] = []

    for file_name, df in datasets:
        prepared = df.copy()
        prepared[source_file_column] = file_name
        prepared[source_row_column] = np.arange(1, len(prepared) + 1)
        prepared_frames.append(prepared)
        source_row_counts[file_name] = int(len(prepared))
        column_sets.append(set(str(column) for column in df.columns))

    merged_df = pd.concat(prepared_frames, ignore_index=True, sort=False)
    common_columns = sorted(set.intersection(*column_sets)) if column_sets else []
    union_columns = sorted(set.union(*column_sets)) if column_sets else []
    unique_column_count = len(union_columns) - len(common_columns)

    notes = [
        f"已依欄位名稱垂直合併 {len(datasets)} 個檔案。",
        f"共同欄位 {len(common_columns)} 個，合併後原始欄位 {len(union_columns)} 個。",
        "不同檔案缺少的欄位會保留為缺失值，模型訓練時會由系統自動補值。",
    ]

    if unique_column_count > 0:
        notes.append(f"偵測到 {unique_column_count} 個只存在於部分檔案的欄位。")

    if not common_columns:
        notes.append("這批檔案沒有共同欄位，合併分析會以欄位聯集進行，請優先選擇資料較完整的目標欄位。")

    return merged_df, {
        "source_files": [file_name for file_name, _ in datasets],
        "source_file_count": len(datasets),
        "source_row_counts": source_row_counts,
        "merge_strategy": "依欄位名稱垂直合併，保留欄位聯集",
        "merge_notes": notes,
        "source_file_column": source_file_column,
        "source_row_column": source_row_column,
        "common_columns": common_columns,
    }


def _read_dataset(content: bytes, suffix: str) -> pd.DataFrame:
    buffer = BytesIO(content)

    try:
        if suffix == ".csv":
            return _read_csv_with_fallbacks(content)

        if suffix == ".xlsx":
            return pd.read_excel(buffer, engine="openpyxl")

        if suffix == ".xls":
            return pd.read_excel(buffer)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 - converts parser errors into API-safe messages
        raise HTTPException(
            status_code=422,
            detail=f"無法解析上傳資料集：{exc}",
        ) from exc

    raise HTTPException(status_code=400, detail="不支援的檔案格式。")


def _read_csv_with_fallbacks(content: bytes) -> pd.DataFrame:
    last_error: Exception | None = None

    for encoding in ("utf-8-sig", "utf-8", "big5"):
        try:
            return pd.read_csv(BytesIO(content), encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
        except pd.errors.ParserError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"無法解析 CSV 檔案：{exc}",
            ) from exc

    raise HTTPException(
        status_code=422,
        detail=f"無法解碼 CSV 檔案。最後錯誤：{last_error}",
    )


def _summarize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    numeric_df = df.select_dtypes(include=[np.number])
    numeric_summary: dict[str, dict[str, float | int | None]] = {}

    if not numeric_df.empty:
        described = numeric_df.describe().transpose()
        for column, stats in described.iterrows():
            numeric_summary[str(column)] = {
                "count": _safe_number(stats.get("count")),
                "mean": _safe_number(stats.get("mean")),
                "std": _safe_number(stats.get("std")),
                "min": _safe_number(stats.get("min")),
                "25%": _safe_number(stats.get("25%")),
                "50%": _safe_number(stats.get("50%")),
                "75%": _safe_number(stats.get("75%")),
                "max": _safe_number(stats.get("max")),
            }

    return {
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "columns": [str(column) for column in df.columns],
        "data_types": {str(column): str(dtype) for column, dtype in df.dtypes.items()},
        "missing_values": {
            str(column): int(missing_count)
            for column, missing_count in df.isna().sum().items()
        },
        "numeric_summary": numeric_summary,
        "recommended_target_columns": _recommend_target_columns(df),
    }


def _safe_number(value: Any) -> float | int | None:
    if value is None or pd.isna(value):
        return None

    if isinstance(value, (np.integer, int)):
        return int(value)

    if isinstance(value, (np.floating, float)):
        number = float(value)
        if number.is_integer():
            return int(number)
        return round(number, 6)

    return value


def _recommend_target_columns(df: pd.DataFrame) -> list[str]:
    excluded_names = {"id", "index", "source_file", "source_row_number"}
    scored_columns: list[tuple[int, str]] = []

    for column in df.columns:
        column_name = str(column)
        normalized = column_name.strip().lower()
        if normalized in excluded_names or normalized.endswith("_id"):
            continue

        non_null = df[column].dropna()
        if non_null.empty:
            continue

        score = 0
        if pd.api.types.is_numeric_dtype(non_null):
            score += 30
            if non_null.nunique() > min(10, max(3, int(len(non_null) * 0.3))):
                score += 20
        else:
            score += 8
            if 2 <= non_null.nunique() <= 20:
                score += 15

        if any(
            keyword in normalized
            for keyword in (
                "target",
                "label",
                "price",
                "close",
                "sales",
                "revenue",
                "profit",
                "return",
                "risk",
                "score",
                "amount",
                "value",
            )
        ) or normalized == "y":
            score += 30

        scored_columns.append((score, column_name))

    scored_columns.sort(key=lambda item: (-item[0], item[1]))
    return [column for _, column in scored_columns[:5]]


def _unique_metadata_column(
    datasets: list[tuple[str, pd.DataFrame]],
    preferred_name: str,
) -> str:
    existing_columns = {
        str(column)
        for _, df in datasets
        for column in df.columns
    }
    if preferred_name not in existing_columns:
        return preferred_name

    index = 2
    while f"{preferred_name}_{index}" in existing_columns:
        index += 1

    return f"{preferred_name}_{index}"
