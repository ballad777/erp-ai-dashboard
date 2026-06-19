from __future__ import annotations

import csv
import hashlib
import json
import logging
from io import BytesIO
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd
from fastapi import HTTPException, UploadFile

from app.services.insight_narrative import build_dataset_brief

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_UPLOAD_FILES = 20
MAX_BATCH_UPLOAD_BYTES = 100 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}
CSV_ENCODINGS = ("utf-8-sig", "utf-8", "big5", "cp950", "latin1")
CSV_DELIMITERS = (",", ";", "\t", "|")
PROFILE_ROW_LIMIT = 50_000

logger = logging.getLogger(__name__)


async def analyze_uploaded_dataset(file: UploadFile) -> dict[str, Any]:
    df, file_name = await read_uploaded_dataframe(file)

    started_at = perf_counter()
    result = _summarize_dataframe_safely(df, file_name=file_name)
    elapsed = perf_counter() - started_at

    result["file_name"] = file_name
    result["analysis_time_seconds"] = round(elapsed, 4)
    return result


async def analyze_multiple_uploaded_datasets(files: list[UploadFile]) -> dict[str, Any]:
    validate_upload_batch(files)

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
        except Exception as exc:  # noqa: BLE001 - one bad file must not fail the batch
            logger.exception("Unexpected dataset profile failure for %s", file_name)
            dataset_results.append(
                {
                    "file_name": file_name,
                    "success": False,
                    "analysis": None,
                    "error": _profile_error_detail(),
                }
            )

    merged_analysis: dict[str, Any] | None = None
    notes: list[str] = []

    if len(loaded_datasets) >= 2:
        try:
            merged_df, merge_metadata = merge_dataframes(loaded_datasets)
            merged_analysis = analyze_dataframe(merged_df, file_name="merged_dataset.csv")
            merged_analysis.update(merge_metadata)
        except Exception as exc:  # noqa: BLE001 - keep successful single-file results visible
            logger.exception("Merged dataset profile failure")
            notes.append(f"合併分析暫時無法建立：{_safe_exception_message(exc)}")
    elif len(loaded_datasets) == 1:
        notes.append("只有 1 個檔案成功讀取，因此尚未建立合併分析。")
    else:
        notes.append("沒有檔案成功讀取，請檢查檔案格式與內容。")

    return {
        "datasets": dataset_results,
        "merged": merged_analysis,
        "notes": notes,
    }


def validate_upload_batch(files: list[UploadFile]) -> None:
    if not files:
        raise HTTPException(status_code=400, detail="請至少上傳一個檔案。")

    if len(files) > MAX_UPLOAD_FILES:
        raise HTTPException(
            status_code=413,
            detail=f"單次最多可上傳 {MAX_UPLOAD_FILES} 個檔案。",
        )

    known_total_size = sum(file.size or 0 for file in files)
    if known_total_size > MAX_BATCH_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="單次上傳總容量不可超過 100 MB。",
        )


async def read_uploaded_dataframe(file: UploadFile) -> tuple[pd.DataFrame, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="缺少上傳檔案名稱。")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="不支援的檔案格式，請上傳 CSV、XLSX、XLS 或 JSON 檔案。",
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

    df.attrs["dataset_hash"] = hashlib.sha256(content).hexdigest()
    return df, file.filename


def analyze_dataframe(df: pd.DataFrame, file_name: str = "dataset.csv") -> dict[str, Any]:
    if df.empty:
        raise ValueError("資料集沒有任何資料列。")

    result = _summarize_dataframe_safely(df, file_name=file_name)
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
    schema_conflicts = _detect_schema_conflicts(datasets, common_columns)
    join_key_candidates = _detect_join_key_candidates(datasets, common_columns)
    common_ratio = len(common_columns) / max(1, len(union_columns))
    recommended_strategy = "append" if common_ratio >= 0.45 else "separate_analysis"

    notes = [
        f"已依欄位名稱垂直合併 {len(datasets)} 個檔案。",
        f"共同欄位 {len(common_columns)} 個，合併後原始欄位 {len(union_columns)} 個。",
        "不同檔案缺少的欄位會保留為缺失值，模型訓練時會由系統自動補值。",
    ]

    if unique_column_count > 0:
        notes.append(f"偵測到 {unique_column_count} 個只存在於部分檔案的欄位。")

    if not common_columns:
        notes.append("這批檔案沒有共同欄位，合併分析會以欄位聯集進行，請優先選擇資料較完整的目標欄位。")
    if schema_conflicts:
        notes.append("部分共同欄位在不同檔案中的資料型別不一致，已列入合併策略檢查。")
    if recommended_strategy == "separate_analysis":
        notes.append("共同欄位比例偏低，系統建議先分開分析，再由使用者確認是否合併。")

    return merged_df, {
        "source_files": [file_name for file_name, _ in datasets],
        "source_file_count": len(datasets),
        "source_row_counts": source_row_counts,
        "merge_strategy": "依欄位名稱垂直合併，保留欄位聯集",
        "merge_notes": notes,
        "merge_plan": {
            "recommended_strategy": recommended_strategy,
            "available_strategies": [
                {
                    "key": "append",
                    "label": "垂直合併",
                    "description": "適合欄位結構相近的同類資料。",
                    "enabled": bool(common_columns),
                },
                {
                    "key": "join",
                    "label": "依鍵值 Join",
                    "description": "適合有共同 ID、日期或主鍵欄位的資料。",
                    "enabled": bool(join_key_candidates),
                },
                {
                    "key": "separate_analysis",
                    "label": "分開分析",
                    "description": "適合欄位差異大或尚未確認資料關聯的檔案。",
                    "enabled": True,
                },
            ],
            "common_column_ratio": round(common_ratio, 4),
            "join_key_candidates": join_key_candidates,
            "schema_conflicts": schema_conflicts,
        },
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

        if suffix == ".json":
            return _read_json_dataset(content)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 - converts parser errors into API-safe messages
        raise HTTPException(
            status_code=422,
            detail="無法解析上傳資料集，請確認檔案未損毀且內容格式正確。",
        ) from exc

    raise HTTPException(status_code=400, detail="不支援的檔案格式。")


def _read_csv_with_fallbacks(content: bytes) -> pd.DataFrame:
    parser_errors: list[str] = []

    for encoding in CSV_ENCODINGS:
        sample = _decode_csv_sample(content, encoding)
        if sample is None:
            continue

        delimiters = _candidate_csv_delimiters(sample)
        for delimiter in delimiters:
            try:
                df = pd.read_csv(
                    BytesIO(content),
                    encoding=encoding,
                    sep=delimiter,
                    low_memory=False,
                )
            except UnicodeDecodeError:
                break
            except pd.errors.ParserError as exc:
                parser_errors.append(str(exc))
                continue

            if _csv_parse_is_suspicious(df, sample, delimiter):
                continue

            return _attach_csv_metadata(
                df,
                encoding=encoding,
                delimiter=delimiter,
                warnings=[],
            )

        for delimiter in delimiters:
            try:
                df = pd.read_csv(
                    BytesIO(content),
                    encoding=encoding,
                    sep=delimiter,
                    engine="python",
                    on_bad_lines="skip",
                )
            except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as exc:
                parser_errors.append(str(exc))
                continue

            if _csv_parse_is_suspicious(df, sample, delimiter):
                continue

            return _attach_csv_metadata(
                df,
                encoding=encoding,
                delimiter=delimiter,
                warnings=[
                    "CSV 含有格式異常列，系統已略過無法安全解析的列並保留可讀取資料。"
                ],
            )

    detail = (
        "無法解析 CSV 檔案，請確認編碼、分隔符與各列欄位數是否一致。"
        if parser_errors
        else "無法解碼 CSV 檔案，請使用 UTF-8、Big5/CP950 或常見文字編碼。"
    )
    raise HTTPException(status_code=422, detail=detail)


def _decode_csv_sample(content: bytes, encoding: str) -> str | None:
    try:
        return content[:65_536].decode(encoding)
    except UnicodeDecodeError:
        return None


def _candidate_csv_delimiters(sample: str) -> list[str]:
    candidates: list[str] = []

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(CSV_DELIMITERS))
        candidates.append(dialect.delimiter)
    except csv.Error:
        pass

    counted = sorted(
        ((sample.count(delimiter), delimiter) for delimiter in CSV_DELIMITERS),
        key=lambda item: (-item[0], item[1]),
    )
    candidates.extend(delimiter for count, delimiter in counted if count > 0)
    candidates.extend(CSV_DELIMITERS)

    ordered: list[str] = []
    for delimiter in candidates:
        if delimiter not in ordered:
            ordered.append(delimiter)
    return ordered


def _csv_parse_is_suspicious(
    df: pd.DataFrame,
    sample: str,
    delimiter: str,
) -> bool:
    if df.shape[1] != 1:
        return False

    selected_count = sample.count(delimiter)
    other_counts = [
        sample.count(candidate)
        for candidate in CSV_DELIMITERS
        if candidate != delimiter
    ]
    return bool(other_counts and max(other_counts) > selected_count)


def _attach_csv_metadata(
    df: pd.DataFrame,
    *,
    encoding: str,
    delimiter: str,
    warnings: list[str],
) -> pd.DataFrame:
    df.attrs["parser_metadata"] = {
        "encoding": encoding,
        "delimiter": delimiter,
    }
    if warnings:
        df.attrs["parser_warnings"] = warnings
    return df


def _summarize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    profile_df = _profile_dataframe(df)
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

    summary = {
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "columns": [str(column) for column in df.columns],
        "data_types": {str(column): str(dtype) for column, dtype in df.dtypes.items()},
        "missing_values": {
            str(column): int(missing_count)
            for column, missing_count in df.isna().sum().items()
        },
        "numeric_summary": numeric_summary,
        "recommended_target_columns": _recommend_target_columns(profile_df),
    }
    parser_warnings = df.attrs.get("parser_warnings")
    if isinstance(parser_warnings, list) and parser_warnings:
        summary["parser_warnings"] = [str(warning) for warning in parser_warnings]

    summary["quality_report"] = _build_quality_report(df, profile_df=profile_df)
    summary["schema_fingerprint"] = _schema_fingerprint(summary)
    dataset_hash = df.attrs.get("dataset_hash")
    if isinstance(dataset_hash, str):
        summary["dataset_hash"] = dataset_hash
    summary.update(build_dataset_brief(summary))
    return summary


def _summarize_dataframe_safely(
    df: pd.DataFrame,
    *,
    file_name: str,
) -> dict[str, Any]:
    try:
        return _summarize_dataframe(df)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Dataset profile summary failed for %s", file_name)
        raise HTTPException(status_code=422, detail=_profile_error_detail()) from exc


def _profile_error_detail() -> str:
    return (
        "資料已讀取，但建立資料摘要時失敗。請檢查欄位是否過多、資料型態是否混雜，"
        "或先縮小資料集後再試一次。"
    )


def _safe_exception_message(exc: Exception) -> str:
    if isinstance(exc, HTTPException):
        return str(exc.detail)
    return _profile_error_detail()


def _profile_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) <= PROFILE_ROW_LIMIT:
        return df
    return df.head(PROFILE_ROW_LIMIT)


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


def _read_json_dataset(content: bytes) -> pd.DataFrame:
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail="無法解碼 JSON 檔案，請確認檔案使用 UTF-8 編碼。",
        ) from exc

    try:
        parsed = json.loads(decoded)
    except json.JSONDecodeError as exc:
        return _read_json_lines_dataset(decoded, original_error=exc)

    if isinstance(parsed, list):
        return pd.json_normalize(parsed)

    if isinstance(parsed, dict):
        for key in ("data", "records", "items", "rows"):
            value = parsed.get(key)
            if isinstance(value, list):
                return pd.json_normalize(value)
        return pd.json_normalize(parsed)

    raise HTTPException(
        status_code=422,
        detail="JSON 檔案必須是物件、物件陣列，或包含 data/records/items/rows 陣列。",
    )


def _read_json_lines_dataset(
    decoded: str,
    *,
    original_error: json.JSONDecodeError,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    lines = [line.strip() for line in decoded.splitlines() if line.strip()]
    if not lines:
        raise HTTPException(status_code=422, detail="JSON 檔案沒有可讀取的資料。") from original_error

    try:
        for line in lines:
            parsed_line = json.loads(line)
            if isinstance(parsed_line, dict):
                records.append(parsed_line)
            elif isinstance(parsed_line, list) and all(isinstance(item, dict) for item in parsed_line):
                records.extend(parsed_line)
            else:
                raise ValueError("JSON Lines 每一列必須是物件或物件陣列。")
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail="無法解析 JSON 檔案，請確認內容是有效 JSON、JSON Lines 或 NDJSON。",
        ) from exc

    if not records:
        raise HTTPException(status_code=422, detail="JSON Lines 檔案沒有可讀取的物件資料。")

    df = pd.json_normalize(records)
    df.attrs["parser_warnings"] = ["已偵測 JSON Lines/NDJSON 格式，系統已逐列解析資料。"]
    return df


def _build_quality_report(
    df: pd.DataFrame,
    *,
    profile_df: pd.DataFrame | None = None,
) -> dict[str, Any]:
    row_count = int(len(df))
    column_count = int(df.shape[1])
    profile = profile_df if profile_df is not None else _profile_dataframe(df)
    profile_row_count = int(len(profile))
    is_profiled_sample = profile_row_count < row_count
    missing_counts = df.isna().sum()
    missing_total = int(missing_counts.sum())
    duplicate_rows = int(profile.duplicated().sum())
    constant_columns: list[str] = []
    high_cardinality_columns: list[dict[str, Any]] = []
    id_like_columns: list[str] = []
    class_imbalance: list[dict[str, Any]] = []

    for column in profile.columns:
        column_name = str(column)
        series = profile[column].dropna()
        if series.empty:
            constant_columns.append(column_name)
            continue

        unique_count = int(series.nunique(dropna=True))
        unique_ratio = unique_count / max(1, len(series))
        normalized = column_name.strip().lower()
        if unique_count <= 1:
            constant_columns.append(column_name)
        if unique_ratio >= 0.9 and len(series) >= 10:
            high_cardinality_columns.append(
                {
                    "column": column_name,
                    "unique_count": unique_count,
                    "unique_ratio": round(unique_ratio, 4),
                }
            )
        if normalized == "id" or normalized.endswith("_id") or unique_ratio >= 0.98:
            id_like_columns.append(column_name)

        if unique_count <= min(20, max(2, row_count // 2)):
            top_ratio = float(series.value_counts(normalize=True).iloc[0])
            if top_ratio >= 0.8 and unique_count >= 2:
                class_imbalance.append(
                    {
                        "column": column_name,
                        "top_class_ratio": round(top_ratio, 4),
                        "unique_count": unique_count,
                    }
                )

    outliers = _detect_numeric_outliers(profile)
    date_frequency = _detect_date_frequency(profile)
    leakage_candidates = _detect_leakage_candidates(profile)
    issue_count = (
        len(constant_columns)
        + len(high_cardinality_columns)
        + len(outliers)
        + len(class_imbalance)
        + len(leakage_candidates)
        + (1 if duplicate_rows else 0)
        + (1 if missing_total else 0)
    )
    quality_score = max(
        0,
        100
        - min(35, round((missing_total / max(1, row_count * column_count)) * 100))
        - min(20, round((duplicate_rows / max(1, row_count)) * 100))
        - min(30, issue_count * 3),
    )

    return {
        "quality_score": int(quality_score),
        "row_count": row_count,
        "column_count": column_count,
        "profiled_row_count": profile_row_count,
        "is_profiled_sample": is_profiled_sample,
        "missing": {
            "total_cells": missing_total,
            "columns": [
                {
                    "column": str(column),
                    "missing_count": int(count),
                    "missing_ratio": round(int(count) / max(1, row_count), 4),
                }
                for column, count in missing_counts.items()
                if int(count) > 0
            ],
        },
        "duplicate_rows": {
            "count": duplicate_rows,
            "ratio": round(duplicate_rows / max(1, row_count), 4),
        },
        "constant_columns": constant_columns,
        "high_cardinality_columns": high_cardinality_columns,
        "id_like_columns": id_like_columns,
        "outliers": outliers,
        "class_imbalance": class_imbalance,
        "date_frequency": date_frequency,
        "leakage_candidates": leakage_candidates,
        "issues": _quality_issues(
            duplicate_rows=duplicate_rows,
            missing_total=missing_total,
            constant_columns=constant_columns,
            high_cardinality_columns=high_cardinality_columns,
            outliers=outliers,
            class_imbalance=class_imbalance,
            leakage_candidates=leakage_candidates,
            is_profiled_sample=is_profiled_sample,
        ),
    }


def _detect_numeric_outliers(df: pd.DataFrame) -> list[dict[str, Any]]:
    outliers: list[dict[str, Any]] = []
    numeric_df = df.select_dtypes(include=[np.number])
    for column in numeric_df.columns:
        series = numeric_df[column].dropna()
        if len(series) < 4:
            continue
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        count = int(((series < lower) | (series > upper)).sum())
        if count:
            outliers.append(
                {
                    "column": str(column),
                    "count": count,
                    "ratio": round(count / max(1, len(series)), 4),
                    "lower_bound": round(lower, 6),
                    "upper_bound": round(upper, 6),
                }
            )
    return outliers


def _detect_date_frequency(df: pd.DataFrame) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for column in df.columns:
        column_name = str(column)
        normalized = column_name.lower()
        series = df[column].dropna()
        if series.empty:
            continue
        if not (
            "date" in normalized
            or "time" in normalized
            or pd.api.types.is_datetime64_any_dtype(series)
        ):
            continue
        parsed = pd.to_datetime(series, errors="coerce")
        valid = parsed.dropna().sort_values()
        if len(valid) < 3:
            continue
        diffs = valid.diff().dropna()
        median_seconds = float(diffs.dt.total_seconds().median())
        candidates.append(
            {
                "column": column_name,
                "valid_ratio": round(len(valid) / max(1, len(series)), 4),
                "median_interval_seconds": round(median_seconds, 2),
                "start": valid.iloc[0].isoformat(),
                "end": valid.iloc[-1].isoformat(),
            }
        )
    return candidates


def _detect_leakage_candidates(df: pd.DataFrame) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    keywords = ("target", "label", "result", "outcome", "答案", "結果")
    for column in df.columns:
        normalized = str(column).strip().lower()
        if any(keyword in normalized for keyword in keywords):
            candidates.append(
                {
                    "column": str(column),
                    "reason": "欄位名稱像目標或結果欄位，建模前需確認是否造成 target leakage。",
                }
            )
    return candidates


def _quality_issues(
    *,
    duplicate_rows: int,
    missing_total: int,
    constant_columns: list[str],
    high_cardinality_columns: list[dict[str, Any]],
    outliers: list[dict[str, Any]],
    class_imbalance: list[dict[str, Any]],
    leakage_candidates: list[dict[str, Any]],
    is_profiled_sample: bool = False,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if is_profiled_sample:
        issues.append(
            {
                "severity": "info",
                "code": "profile_sample",
                "message": f"資料列數較多，品質檢查已使用前 {PROFILE_ROW_LIMIT:,} 列建立輪廓，避免讀取過久。",
            }
        )
    if missing_total:
        issues.append(
            {
                "severity": "warning",
                "code": "missing_values",
                "message": "資料包含缺失值，模型前會自動補值，但建議先確認缺失原因。",
            }
        )
    if duplicate_rows:
        issues.append(
            {
                "severity": "warning",
                "code": "duplicate_rows",
                "message": "偵測到重複列，可能影響統計摘要與模型評估。",
            }
        )
    if constant_columns:
        issues.append(
            {
                "severity": "info",
                "code": "constant_columns",
                "message": "部分欄位只有單一值，通常不適合作為模型特徵。",
            }
        )
    if high_cardinality_columns:
        issues.append(
            {
                "severity": "info",
                "code": "high_cardinality",
                "message": "部分欄位唯一值比例很高，可能是 ID 或需要特殊編碼。",
            }
        )
    if outliers:
        issues.append(
            {
                "severity": "warning",
                "code": "outliers",
                "message": "數值欄位存在 IQR 異常值，建議分析前確認是否為有效極端值。",
            }
        )
    if class_imbalance:
        issues.append(
            {
                "severity": "warning",
                "code": "class_imbalance",
                "message": "部分類別欄位分布不均，分類任務應使用分層切分與 F1 等指標。",
            }
        )
    if leakage_candidates:
        issues.append(
            {
                "severity": "danger",
                "code": "target_leakage",
                "message": "偵測到疑似結果欄位，建模前需避免把答案欄位當作特徵。",
            }
        )
    return issues


def _schema_fingerprint(summary: dict[str, Any]) -> str:
    payload = {
        "columns": summary.get("columns", []),
        "data_types": summary.get("data_types", {}),
        "row_count": summary.get("row_count"),
        "column_count": summary.get("column_count"),
    }
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _detect_schema_conflicts(
    datasets: list[tuple[str, pd.DataFrame]],
    common_columns: list[str],
) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    for column in common_columns:
        observed = {
            file_name: str(df[column].dtype)
            for file_name, df in datasets
            if column in df.columns
        }
        if len(set(observed.values())) > 1:
            conflicts.append({"column": column, "types_by_file": observed})
    return conflicts


def _detect_join_key_candidates(
    datasets: list[tuple[str, pd.DataFrame]],
    common_columns: list[str],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for column in common_columns:
        scores: list[float] = []
        for _, df in datasets:
            series = df[column].dropna()
            if series.empty:
                scores.append(0)
                continue
            scores.append(float(series.nunique(dropna=True)) / max(1, len(series)))
        normalized = column.lower()
        name_bonus = 0.25 if normalized == "id" or normalized.endswith("_id") else 0
        name_bonus += 0.15 if "date" in normalized or "time" in normalized else 0
        score = min(1.0, (sum(scores) / max(1, len(scores))) + name_bonus)
        if score >= 0.65:
            candidates.append(
                {
                    "column": column,
                    "confidence": round(score, 4),
                    "reason": "共同欄位且唯一值比例高，可能可作為 Join key。",
                }
            )
    candidates.sort(key=lambda item: (-float(item["confidence"]), item["column"]))
    return candidates[:5]
