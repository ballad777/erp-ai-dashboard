from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any
import warnings

import pandas as pd


@dataclass(frozen=True)
class DomainDefinition:
    key: str
    label: str
    clues: tuple[str, ...]
    strong_clues: tuple[str, ...] = ()


AI_LLM_DOMAIN = DomainDefinition(
    key="ai_llm",
    label="AI / LLM 模型發展資料",
    clues=(
        "model",
        "model_name",
        "model_id",
        "benchmark",
        "benchmark_type",
        "score",
        "score_pct",
        "max_score",
        "parameters",
        "params",
        "params_billions",
        "context_window",
        "context_window_k_tokens",
        "company",
        "organization",
        "provider",
        "release_date",
        "release_year",
        "training_cost",
        "training_cost_usd",
        "flops",
        "training_flops",
        "gpu_hours",
        "gpu_hours_h100",
        "input_price",
        "output_price",
        "input_usd",
        "output_usd",
        "blended_usd",
        "token",
        "tokens",
        "milestone",
        "milestone_name",
        "capability",
        "modality",
        "access_type",
        "open_source",
    ),
    strong_clues=(
        "model_name",
        "benchmark",
        "params_billions",
        "training_flops",
        "gpu_hours",
        "context_window",
        "input_usd_per_1m_tokens",
        "output_usd_per_1m_tokens",
        "milestone_name",
    ),
)

FINANCIAL_DOMAIN = DomainDefinition(
    key="financial_timeseries",
    label="金融時間序列資料",
    clues=(
        "date",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "adj_close",
        "price",
        "volume",
        "ticker",
        "symbol",
    ),
    strong_clues=("open", "high", "low", "close", "adjusted_close", "ticker", "symbol"),
)

SPORTS_DOMAIN = DomainDefinition(
    key="sports",
    label="體育表現資料",
    clues=(
        "player",
        "team",
        "season",
        "game",
        "match",
        "points",
        "assists",
        "rebounds",
        "steals",
        "blocks",
    ),
    strong_clues=("player", "team", "season", "game", "match"),
)

GENERIC_DOMAIN = DomainDefinition(
    key="general_table",
    label="一般表格資料",
    clues=(),
)

DOMAIN_DEFINITIONS = (AI_LLM_DOMAIN, FINANCIAL_DOMAIN, SPORTS_DOMAIN)

DATE_NAME_HINTS = ("date", "time", "timestamp", "year_month", "release_date", "created_at", "updated_at")
ID_NAME_HINTS = ("id", "uuid", "guid", "index", "row_number")
TEXT_NAME_HINTS = ("description", "summary", "notes", "text", "content", "url")
FINANCIAL_PRICE_NAMES = {
    "close",
    "price",
    "open",
    "high",
    "low",
    "adjusted_close",
    "adj_close",
}
NON_FINANCIAL_PRICE_CONTEXT = (
    "input",
    "output",
    "token",
    "training",
    "cost",
    "benchmark",
    "score",
    "source",
    "row",
)


def build_dataset_understanding(df: pd.DataFrame, file_name: str) -> dict[str, Any]:
    columns = [str(column) for column in df.columns]
    row_count = int(len(df))
    column_count = int(len(columns))
    date_columns = _detect_date_columns(df)
    numeric_columns = [str(column) for column in df.select_dtypes(include="number").columns]
    text_columns = _detect_text_columns(df)
    categorical_columns = _detect_categorical_columns(df, text_columns=text_columns)
    primary_key_candidates = _detect_primary_key_candidates(df)
    missing_ratio = float(df.isna().sum().sum() / max(1, row_count * column_count))
    duplicate_ratio = float(df.duplicated().sum() / max(1, row_count))
    domain_scores = _score_domains(columns, file_name=file_name)
    possible_topics = _possible_topics(domain_scores)
    primary_domain = possible_topics[0] if possible_topics else _topic_payload(GENERIC_DOMAIN, 35, [])
    financial_eligibility = _financial_eligibility(
        df=df,
        primary_domain_key=str(primary_domain["key"]),
        date_columns=date_columns,
    )
    target_recommendations = recommend_target_columns_for_purpose(df, primary_domain_key=str(primary_domain["key"]))
    not_suitable_reasons = _not_suitable_reasons(
        df=df,
        primary_domain_key=str(primary_domain["key"]),
        financial_eligibility=financial_eligibility,
        target_recommendations=target_recommendations,
    )

    return {
        "file_name": file_name,
        "row_count": row_count,
        "column_count": column_count,
        "columns": columns,
        "primary_key_candidates": primary_key_candidates,
        "date_columns": date_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "text_columns": text_columns,
        "missing_value_ratio": round(missing_ratio, 6),
        "duplicate_value_ratio": round(duplicate_ratio, 6),
        "possible_data_topics": possible_topics,
        "primary_domain": primary_domain,
        "confidence_score": int(primary_domain.get("confidence_score") or 35),
        "not_suitable_reasons": not_suitable_reasons,
        "recommended_analysis_goals": _recommended_analysis_goals(str(primary_domain["key"])),
        "target_recommendations": target_recommendations,
        "financial_eligibility": financial_eligibility,
    }


def recommend_target_columns_for_purpose(
    df: pd.DataFrame,
    *,
    primary_domain_key: str | None = None,
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    columns = [str(column) for column in df.columns]

    if primary_domain_key == AI_LLM_DOMAIN.key:
        purpose_map = (
            (
                "預測模型能力",
                ("score", "score_pct", "benchmark_score"),
                "適合在確認 benchmark 定義後，用來比較模型能力或建立能力預測。",
            ),
            (
                "預測訓練成本",
                ("training_cost", "training_cost_usd", "gpu_hours", "flops", "energy", "co2"),
                "適合分析訓練成本、算力與環境成本的變化。",
            ),
            (
                "API 價格分析",
                ("input_usd", "output_usd", "blended_usd", "price_per_million", "tokens"),
                "適合分析 API 價格與 token 成本變化。",
            ),
            (
                "時間趨勢分析",
                ("release_date", "date", "year_month", "timestamp", "release_year"),
                "適合建立模型發布、能力突破或價格變化時間軸。",
            ),
        )
        for purpose, hints, reason in purpose_map:
            matched = [
                column for column in columns
                if any(hint in _normalize_name(column) for hint in hints)
            ]
            if matched:
                recommendations.append(
                    {
                        "purpose": purpose,
                        "columns": matched[:5],
                        "confidence": "medium" if purpose == "預測模型能力" else "high",
                        "reason": reason,
                    }
                )
        return recommendations

    generic_candidates: list[tuple[int, str, str]] = []
    for column in df.columns:
        column_name = str(column)
        normalized = _normalize_name(column_name)
        if _is_unsafe_target_name(normalized):
            continue
        series = df[column].dropna()
        if series.empty:
            continue
        score = 0
        if pd.api.types.is_numeric_dtype(series):
            score += 30
            if series.nunique() > min(10, max(3, int(len(series) * 0.3))):
                score += 10
        elif 2 <= series.nunique() <= 20:
            score += 20
        if any(keyword in normalized for keyword in ("target", "label", "price", "sales", "revenue", "profit", "risk", "amount", "value")):
            score += 20
        if score >= 25:
            generic_candidates.append((score, column_name, "欄位型態與名稱看起來可作為分析目標，但仍需使用者確認。"))

    generic_candidates.sort(key=lambda item: (-item[0], item[1]))
    if not generic_candidates:
        return []

    return [
        {
            "purpose": "自訂目標欄位",
            "columns": [column for _, column, _ in generic_candidates[:5]],
            "confidence": "low",
            "reason": "目前無法自動判斷可靠目標欄位，建議先做資料探索或手動選擇目標。",
        }
    ]


def recommended_target_column_names(understanding: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for item in understanding.get("target_recommendations") or []:
        for column in item.get("columns") or []:
            if isinstance(column, str) and column not in names:
                names.append(column)
    return names[:5]


def plan_multi_table_strategy(datasets: list[tuple[str, pd.DataFrame]]) -> dict[str, Any]:
    if len(datasets) < 2:
        return {
            "recommended_strategy": "single_file",
            "label": "單檔分析",
            "confidence_score": 100,
            "reason": "目前只有一個成功讀取的檔案，不需要合併策略。",
            "join_key_candidates": [],
            "common_column_ratio": 1,
            "available_strategies": [],
            "table_roles": [],
            "warnings": [],
        }

    understandings = [build_dataset_understanding(df, file_name) for file_name, df in datasets]
    domain_counter = Counter(str(item["primary_domain"]["key"]) for item in understandings)
    dominant_domain, dominant_count = domain_counter.most_common(1)[0]
    column_sets = [set(str(column) for column in df.columns) for _, df in datasets]
    common_columns = sorted(set.intersection(*column_sets)) if column_sets else []
    union_columns = sorted(set.union(*column_sets)) if column_sets else []
    common_ratio = len(common_columns) / max(1, len(union_columns))
    join_key_candidates = _multi_table_join_candidates(datasets)
    table_roles = [_infer_table_role(name, df) for name, df in datasets]

    if dominant_domain == AI_LLM_DOMAIN.key and dominant_count >= max(2, len(datasets) // 2):
        strategy = "multi_table_relationship"
        label = "多表關聯分析"
        reason = (
            "這批檔案共同描述 AI/LLM 模型、benchmark、算力成本、API 價格與里程碑；"
            "每張表主題不同，不建議直接垂直合併。"
        )
        warnings = [
            "不建議直接垂直合併，否則會製造大量缺失值，並讓 source_row_number、score 等欄位被誤用。",
            "建議先用 model_name / model_id / organization / release_date / date 作為關聯線索。",
        ]
    elif _is_union_candidate(column_sets, understandings):
        strategy = "union"
        label = "垂直合併"
        reason = "欄位結構高度相似，較像同一種資料的不同批次或不同時間片段。"
        warnings = []
    elif join_key_candidates:
        strategy = "join"
        label = "依鍵值 Join"
        reason = "檔案之間存在可疑共同鍵，適合先確認鍵值定義後再橫向合併。"
        warnings = ["Join 前需確認鍵值唯一性，避免多對多合併放大資料列。"]
    else:
        strategy = "separate_analysis"
        label = "保持分表分析"
        reason = "欄位與主題差異較大，目前不建議自動合併。"
        warnings = ["若要合併，請先手動指定共同鍵或確認每張表代表同一種資料。"]

    return {
        "recommended_strategy": strategy,
        "label": label,
        "confidence_score": 88 if dominant_domain == AI_LLM_DOMAIN.key else 72,
        "reason": reason,
        "dominant_domain": next(
            (item["primary_domain"] for item in understandings if item["primary_domain"]["key"] == dominant_domain),
            _topic_payload(GENERIC_DOMAIN, 35, []),
        ),
        "common_column_ratio": round(common_ratio, 4),
        "common_columns": common_columns,
        "union_column_count": len(union_columns),
        "join_key_candidates": join_key_candidates,
        "available_strategies": _available_merge_strategies(common_ratio, join_key_candidates),
        "table_roles": table_roles,
        "warnings": warnings,
        "understandings": understandings,
    }


def is_financial_timeseries_dataset(df: pd.DataFrame, file_name: str = "dataset.csv") -> tuple[bool, dict[str, Any]]:
    understanding = build_dataset_understanding(df, file_name=file_name)
    eligibility = understanding["financial_eligibility"]
    return bool(eligibility.get("eligible")), understanding


def _score_domains(columns: list[str], *, file_name: str) -> list[dict[str, Any]]:
    normalized_columns = [_normalize_name(column) for column in columns]
    file_hint = _normalize_name(file_name)
    scored: list[dict[str, Any]] = []

    for definition in DOMAIN_DEFINITIONS:
        evidence: list[str] = []
        score = 0
        for original, normalized in zip(columns, normalized_columns):
            matched_clues = [clue for clue in definition.clues if clue in normalized]
            if matched_clues:
                evidence.append(original)
                score += 2 + min(3, len(matched_clues))
            if any(strong in normalized for strong in definition.strong_clues):
                score += 5
        if any(clue in file_hint for clue in definition.clues):
            score += 2
        if score > 0:
            confidence = min(97, 35 + score * 5)
            scored.append(_topic_payload(definition, confidence, evidence[:8]))

    if not scored:
        return [_topic_payload(GENERIC_DOMAIN, 35, [])]

    scored.sort(key=lambda item: (-int(item["confidence_score"]), str(item["label"])))
    return scored


def _possible_topics(domain_scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not domain_scores:
        return [_topic_payload(GENERIC_DOMAIN, 35, [])]
    best = int(domain_scores[0]["confidence_score"])
    if best < 45:
        return [*_dedupe_topics(domain_scores), _topic_payload(GENERIC_DOMAIN, 35, [])]
    return _dedupe_topics(domain_scores)


def _dedupe_topics(topics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for topic in topics:
        key = str(topic["key"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(topic)
    return deduped


def _topic_payload(definition: DomainDefinition, confidence_score: int, evidence: list[str]) -> dict[str, Any]:
    return {
        "key": definition.key,
        "label": definition.label,
        "confidence_score": int(confidence_score),
        "evidence_columns": evidence,
    }


def _detect_date_columns(df: pd.DataFrame) -> list[str]:
    date_columns: list[str] = []
    for column in df.columns:
        column_name = str(column)
        normalized = _normalize_name(column_name)
        has_hint = any(hint in normalized for hint in DATE_NAME_HINTS)
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            date_columns.append(column_name)
            continue
        if not has_hint and pd.api.types.is_numeric_dtype(df[column]):
            continue
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Could not infer format.*", category=UserWarning)
            parsed = pd.to_datetime(df[column], errors="coerce")
        if float(parsed.notna().mean()) >= (0.5 if has_hint else 0.75):
            date_columns.append(column_name)
    return date_columns


def _detect_text_columns(df: pd.DataFrame) -> list[str]:
    text_columns: list[str] = []
    for column in df.columns:
        column_name = str(column)
        series = df[column].dropna()
        if series.empty:
            continue
        normalized = _normalize_name(column_name)
        if any(hint in normalized for hint in TEXT_NAME_HINTS):
            text_columns.append(column_name)
            continue
        if not pd.api.types.is_numeric_dtype(series):
            as_text = series.astype(str)
            average_length = float(as_text.str.len().mean() or 0)
            unique_ratio = float(as_text.nunique(dropna=True) / max(1, len(as_text)))
            if average_length >= 40 or unique_ratio >= 0.8:
                text_columns.append(column_name)
    return text_columns


def _detect_categorical_columns(df: pd.DataFrame, *, text_columns: list[str]) -> list[str]:
    text_set = set(text_columns)
    categorical: list[str] = []
    for column in df.columns:
        column_name = str(column)
        if column_name in text_set or pd.api.types.is_numeric_dtype(df[column]):
            continue
        non_null = df[column].dropna()
        if non_null.empty:
            continue
        unique_count = int(non_null.nunique(dropna=True))
        unique_ratio = unique_count / max(1, len(non_null))
        if unique_count <= 50 or unique_ratio <= 0.4:
            categorical.append(column_name)
    return categorical


def _detect_primary_key_candidates(df: pd.DataFrame) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    row_count = max(1, len(df))
    for column in df.columns:
        column_name = str(column)
        normalized = _normalize_name(column_name)
        non_null = df[column].dropna()
        if non_null.empty:
            continue
        unique_ratio = float(non_null.nunique(dropna=True) / max(1, len(non_null)))
        missing_ratio = 1 - float(len(non_null) / row_count)
        has_key_hint = any(hint == normalized or normalized.endswith(f"_{hint}") for hint in ID_NAME_HINTS)
        if unique_ratio >= 0.95 and missing_ratio <= 0.05:
            candidates.append(
                {
                    "column": column_name,
                    "unique_ratio": round(unique_ratio, 4),
                    "missing_ratio": round(missing_ratio, 4),
                    "reason": "唯一值比例高且缺失少" + ("，欄位名稱也像識別碼" if has_key_hint else ""),
                }
            )
    return candidates[:8]


def _financial_eligibility(
    *,
    df: pd.DataFrame,
    primary_domain_key: str,
    date_columns: list[str],
) -> dict[str, Any]:
    price_columns = [
        str(column) for column in df.columns
        if _is_financial_price_column(str(column)) and pd.to_numeric(df[column], errors="coerce").notna().sum() >= 6
    ]
    reasons: list[str] = []
    if primary_domain_key != FINANCIAL_DOMAIN.key:
        reasons.append("資料主題不是金融時間序列。")
    if not date_columns:
        reasons.append("缺少可用日期欄位。")
    if not price_columns:
        reasons.append("缺少 close、price、open、high、low 或 adjusted_close 等價格欄位。")
    eligible = primary_domain_key == FINANCIAL_DOMAIN.key and bool(date_columns) and bool(price_columns)
    return {
        "eligible": eligible,
        "date_columns": date_columns,
        "price_columns": price_columns,
        "reasons": reasons,
    }


def _is_financial_price_column(column_name: str) -> bool:
    normalized = _normalize_name(column_name)
    if normalized in {"source_row_number", "row_number", "benchmark_score", "score", "score_pct", "max_score"}:
        return False
    if any(context in normalized for context in NON_FINANCIAL_PRICE_CONTEXT):
        return False
    return normalized in FINANCIAL_PRICE_NAMES or normalized.endswith("_close") or normalized.endswith("_price")


def _not_suitable_reasons(
    *,
    df: pd.DataFrame,
    primary_domain_key: str,
    financial_eligibility: dict[str, Any],
    target_recommendations: list[dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    if primary_domain_key == AI_LLM_DOMAIN.key:
        reasons.append("不適合直接套用 RSI、MACD、VaR 或回測，因為 benchmark score 與 API 價格不是股價。")
        reasons.append("若同時上傳多張表，不建議直接垂直合併，應先確認 model_name、model_id、organization 或日期關聯。")
    if not financial_eligibility.get("eligible"):
        reasons.append("此資料未同時具備金融日期與價格欄位，因此不應啟用金融技術分析。")
    if not target_recommendations:
        reasons.append("目前無法自動判斷可靠目標欄位，建議先做資料探索或手動選擇目標。")
    if df.shape[0] < 30:
        reasons.append("資料列數偏少，建模結果可能不穩定，應避免過度解讀分數。")
    return reasons


def _recommended_analysis_goals(primary_domain_key: str) -> list[dict[str, str]]:
    if primary_domain_key == AI_LLM_DOMAIN.key:
        return [
            {"key": "ai_model_overview", "label": "模型基本概況"},
            {"key": "benchmark_analysis", "label": "Benchmark 分數排行榜"},
            {"key": "cost_compute_analysis", "label": "訓練成本與算力分析"},
            {"key": "api_pricing_analysis", "label": "API 價格分析"},
            {"key": "timeline_analysis", "label": "模型發布與能力里程碑時間軸"},
            {"key": "multi_table_relationship", "label": "多表關聯洞察"},
        ]
    if primary_domain_key == FINANCIAL_DOMAIN.key:
        return [
            {"key": "financial_technical_analysis", "label": "金融技術分析"},
            {"key": "trend_analysis", "label": "時間趨勢分析"},
        ]
    return [
        {"key": "eda", "label": "資料探索"},
        {"key": "custom_target", "label": "自訂目標欄位"},
    ]


def _is_union_candidate(column_sets: list[set[str]], understandings: list[dict[str, Any]]) -> bool:
    if not column_sets:
        return False
    common_columns = set.intersection(*column_sets)
    union_columns = set.union(*column_sets)
    common_ratio = len(common_columns) / max(1, len(union_columns))
    domains = {str(item["primary_domain"]["key"]) for item in understandings}
    return common_ratio >= 0.75 and len(domains) == 1


def _multi_table_join_candidates(datasets: list[tuple[str, pd.DataFrame]]) -> list[dict[str, Any]]:
    normalized_to_originals: dict[str, list[tuple[str, str]]] = {}
    key_hints = {
        "model_name",
        "model",
        "model_id",
        "company",
        "organization",
        "provider",
        "date",
        "release_date",
        "year_month",
        "ticker",
        "symbol",
    }
    for file_name, df in datasets:
        for column in df.columns:
            normalized = _normalize_name(str(column))
            if normalized in key_hints or normalized.endswith("_id") or normalized.endswith("_date"):
                normalized_to_originals.setdefault(normalized, []).append((file_name, str(column)))

    candidates = []
    for normalized, occurrences in normalized_to_originals.items():
        files = sorted({file_name for file_name, _ in occurrences})
        if len(files) < 2:
            continue
        candidates.append(
            {
                "key": normalized,
                "files": files,
                "columns": sorted({column for _, column in occurrences}),
                "reason": "多張表共享此欄位，可作為關聯線索。",
            }
        )
    return sorted(candidates, key=lambda item: (-len(item["files"]), item["key"]))[:10]


def _infer_table_role(file_name: str, df: pd.DataFrame) -> dict[str, str]:
    normalized_file = _normalize_name(file_name)
    normalized_columns = " ".join(_normalize_name(str(column)) for column in df.columns)
    text = f"{normalized_file} {normalized_columns}"
    if "benchmark" in text:
        role = "Benchmark 成績表"
    elif "pricing" in text or "input_usd" in text or "output_usd" in text:
        role = "API 價格歷史表"
    elif "compute" in text or "flops" in text or "gpu_hours" in text or "training_cost" in text:
        role = "訓練成本與算力估計表"
    elif "milestone" in text or "capability" in text:
        role = "能力里程碑表"
    elif "catalog" in text or "params_billions" in text or "context_window" in text:
        role = "模型基本資料表"
    else:
        role = "待確認資料表"
    return {"file_name": file_name, "role": role}


def _available_merge_strategies(common_ratio: float, join_key_candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "key": "union",
            "label": "垂直合併",
            "description": "只適合欄位高度相似、代表同一種資料的不同批次。",
            "enabled": common_ratio >= 0.75,
        },
        {
            "key": "join",
            "label": "依鍵值 Join",
            "description": "適合有共同 key 且需要橫向補充欄位的資料。",
            "enabled": bool(join_key_candidates),
        },
        {
            "key": "multi_table_relationship",
            "label": "多表關聯分析",
            "description": "適合主題不同但共享模型、公司或日期等實體的資料。",
            "enabled": True,
        },
        {
            "key": "separate_analysis",
            "label": "保持分表分析",
            "description": "適合關聯不明或需要先分別理解每張表的資料。",
            "enabled": True,
        },
    ]


def _is_unsafe_target_name(normalized: str) -> bool:
    return (
        normalized in {"id", "uuid", "guid", "index", "source_row_number", "source_file", "file_name"}
        or normalized.endswith("_id")
        or normalized.endswith("_uuid")
        or normalized.endswith("_guid")
    )


def _normalize_name(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
        .replace(".", "_")
        .replace("/", "_")
    )
