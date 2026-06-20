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


IRIS_DOMAIN = DomainDefinition(
    key="iris_classification",
    label="鳶尾花分類資料集",
    clues=(
        "iris",
        "species",
        "class",
        "sepal",
        "sepal_length",
        "sepal_width",
        "petal",
        "petal_length",
        "petal_width",
    ),
    strong_clues=("species", "sepal", "petal", "petallengthcm", "petalwidthcm"),
)

AI_LLM_DOMAIN = DomainDefinition(
    key="ai_llm",
    label="AI/LLM模型評估資料集",
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
    label="金融時間序列資料集",
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
    label="體育表現資料集",
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

HOUSING_DOMAIN = DomainDefinition(
    key="housing_price",
    label="房價預測資料集",
    clues=(
        "house",
        "housing",
        "home",
        "property",
        "real_estate",
        "saleprice",
        "median_house_value",
        "sqft",
        "square_feet",
        "bedroom",
        "bathroom",
        "lot_area",
        "garage",
        "neighborhood",
        "房價",
        "不動產",
        "坪數",
        "屋齡",
        "地區",
    ),
    strong_clues=("saleprice", "median_house_value", "housing", "real_estate", "坪數", "屋齡"),
)

CUSTOMER_DOMAIN = DomainDefinition(
    key="customer_behavior",
    label="客戶行為分析資料集",
    clues=(
        "customer",
        "client",
        "user",
        "churn",
        "retention",
        "segment",
        "loyalty",
        "recency",
        "frequency",
        "monetary",
        "purchase",
        "basket",
        "客戶",
        "會員",
        "留存",
        "流失",
    ),
    strong_clues=("customer_id", "churn", "retention", "segment", "loyalty", "客戶"),
)

SALES_DOMAIN = DomainDefinition(
    key="sales_performance",
    label="銷售績效資料集",
    clues=(
        "sales",
        "sale",
        "revenue",
        "order",
        "orders",
        "quantity",
        "units",
        "profit",
        "discount",
        "product",
        "region",
        "store",
        "invoice",
        "營收",
        "銷售",
        "訂單",
        "商品",
        "利潤",
    ),
    strong_clues=("sales", "revenue", "order_id", "quantity", "profit", "營收", "銷售"),
)

GENERIC_DOMAIN = DomainDefinition(
    key="unclassified_dataset",
    label="待確認資料集",
    clues=(),
)

DOMAIN_DEFINITIONS = (
    IRIS_DOMAIN,
    AI_LLM_DOMAIN,
    FINANCIAL_DOMAIN,
    HOUSING_DOMAIN,
    CUSTOMER_DOMAIN,
    SALES_DOMAIN,
    SPORTS_DOMAIN,
)

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


class DataUnderstandingEngine:
    """Rule-based semantic profiler for uploaded tabular datasets.

    The engine intentionally uses transparent scoring instead of opaque labels.
    Every returned classification carries evidence columns, confidence, and
    limits so the UI can explain why the system made the call.
    """

    def analyze(self, df: pd.DataFrame, file_name: str) -> dict[str, Any]:
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
        confidence_breakdown = ConfidenceScorer().score(
            df=df,
            missing_ratio=missing_ratio,
            duplicate_ratio=duplicate_ratio,
            primary_domain=primary_domain,
        )
        financial_eligibility = _financial_eligibility(
            df=df,
            primary_domain_key=str(primary_domain["key"]),
            date_columns=date_columns,
        )
        target_recommendations = TargetRecommendationEngine().recommend(
            df,
            primary_domain_key=str(primary_domain["key"]),
        )
        dataset_story = DatasetStoryGenerator().generate(
            df=df,
            file_name=file_name,
            primary_domain=primary_domain,
            date_columns=date_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            target_recommendations=target_recommendations,
        )
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
            "domain_confidence_score": int(primary_domain.get("confidence_score") or 35),
            "confidence_score": int(confidence_breakdown["score"]),
            "confidence_breakdown": confidence_breakdown,
            "dataset_story": dataset_story,
            "not_suitable_reasons": not_suitable_reasons,
            "recommended_analysis_goals": _recommended_analysis_goals(str(primary_domain["key"])),
            "target_recommendations": target_recommendations,
            "financial_eligibility": financial_eligibility,
        }


class ConfidenceScorer:
    def score(
        self,
        *,
        df: pd.DataFrame,
        missing_ratio: float,
        duplicate_ratio: float,
        primary_domain: dict[str, Any],
    ) -> dict[str, Any]:
        row_count = int(len(df))
        column_count = int(df.shape[1])
        completeness = 30 if row_count > 0 and column_count > 0 else 0
        missing_quality = round(max(0, 25 * (1 - missing_ratio)))
        sample_size = self._sample_score(row_count)
        column_quality = self._column_score(df)
        outlier_penalty = -self._outlier_penalty(df)
        consistency = self._consistency_score(df, duplicate_ratio, primary_domain)
        components = [
            _confidence_component("data_completeness", "資料完整度", completeness, "資料列與欄位皆存在，可建立基本輪廓。"),
            _confidence_component("missing_quality", "缺失值品質", missing_quality, f"整體缺失比例約 {missing_ratio * 100:.1f}%。"),
            _confidence_component("sample_size", "樣本量", sample_size, f"目前共有 {row_count:,} 筆資料。"),
            _confidence_component("column_quality", "欄位品質", column_quality, "欄位不是全空、全唯一或無法使用的比例較高。"),
            _confidence_component("outlier_penalty", "異常值", outlier_penalty, "依 IQR 初步檢查數值欄位極端值。"),
            _confidence_component("consistency", "一致性", consistency, "主題辨識、重複列與欄位語意一致性。"),
        ]
        total = max(0, min(100, int(round(sum(int(item["value"]) for item in components)))))
        return {
            "score": total,
            "formula": "資料完整度 + 缺失值品質 + 樣本量 + 欄位品質 + 異常值調整 + 一致性",
            "components": components,
        }

    @staticmethod
    def _sample_score(row_count: int) -> int:
        if row_count >= 150:
            return 20
        if row_count >= 100:
            return 18
        if row_count >= 50:
            return 16
        if row_count >= 30:
            return 14
        if row_count >= 10:
            return 9
        return 4

    @staticmethod
    def _column_score(df: pd.DataFrame) -> int:
        if df.empty or df.shape[1] == 0:
            return 0
        usable = 0
        for column in df.columns:
            series = df[column].dropna()
            if series.empty:
                continue
            unique_ratio = float(series.nunique(dropna=True) / max(1, len(series)))
            normalized = _normalize_name(str(column))
            if unique_ratio >= 0.98 and (_is_unsafe_target_name(normalized) or normalized.endswith("_id")):
                continue
            usable += 1
        return min(10, round(10 * usable / max(1, df.shape[1])))

    @staticmethod
    def _outlier_penalty(df: pd.DataFrame) -> int:
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            return 0
        flagged = 0
        for column in numeric.columns:
            values = pd.to_numeric(numeric[column], errors="coerce").dropna()
            if len(values) < 12:
                continue
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            ratio = float(((values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)).mean())
            if ratio >= 0.05:
                flagged += 1
        return min(8, flagged * 2)

    @staticmethod
    def _consistency_score(df: pd.DataFrame, duplicate_ratio: float, primary_domain: dict[str, Any]) -> int:
        score = 8
        if int(primary_domain.get("confidence_score") or 0) >= 75:
            score += 4
        if duplicate_ratio <= 0.02:
            score += 2
        if df.shape[1] >= 4:
            score += 1
        return min(15, score)


class TargetRecommendationEngine:
    def recommend(
        self,
        df: pd.DataFrame,
        *,
        primary_domain_key: str | None = None,
    ) -> list[dict[str, Any]]:
        if primary_domain_key == IRIS_DOMAIN.key:
            return self._iris_targets(df)
        if primary_domain_key == AI_LLM_DOMAIN.key:
            return self._ai_llm_targets(df)

        candidates = self._domain_targets(df, primary_domain_key)
        candidates.extend(self._generic_targets(df))
        return _dedupe_target_candidates(candidates)[:5]

    def _iris_targets(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        lookup = {_normalize_name(str(column)): str(column) for column in df.columns}
        candidates: list[dict[str, Any]] = []
        species = lookup.get("species") or lookup.get("class") or lookup.get("target")
        if species:
            candidates.append(
                _target_payload(
                    column=species,
                    task_type="classification",
                    confidence_score=98,
                    purpose="花朵品種分類",
                    reasons=["類別型欄位", "類別分布合理", "常見分類目標", "唯一值數量合理"],
                )
            )
        ordered_regression = [
            ("petallengthcm", 76),
            ("petal_length", 76),
            ("petalwidthcm", 72),
            ("petal_width", 72),
            ("sepallengthcm", 64),
            ("sepal_length", 64),
            ("sepalwidthcm", 58),
            ("sepal_width", 58),
        ]
        seen: set[str] = set()
        for normalized, score in ordered_regression:
            column = lookup.get(normalized)
            if not column or column in seen:
                continue
            seen.add(column)
            candidates.append(
                _target_payload(
                    column=column,
                    task_type="regression",
                    confidence_score=score,
                    purpose="花朵特徵預測",
                    reasons=["連續數值欄位", "與其他花朵量測欄位可建立關係", "可做回歸示範但不如 Species 直覺"],
                )
            )
        return candidates[:5]

    def _ai_llm_targets(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        purpose_map = (
            ("預測模型能力", "regression", 82, ("score", "score_pct", "benchmark_score")),
            ("預測訓練成本", "regression", 78, ("training_cost", "training_cost_usd", "gpu_hours", "flops", "energy", "co2")),
            ("API 價格分析", "regression", 76, ("input_usd", "output_usd", "blended_usd", "price_per_million", "tokens")),
            ("時間趨勢分析", "time_series", 70, ("release_date", "date", "year_month", "timestamp", "release_year")),
        )
        recommendations: list[dict[str, Any]] = []
        for purpose, task_type, score, hints in purpose_map:
            for column in df.columns:
                column_name = str(column)
                if any(hint in _normalize_name(column_name) for hint in hints):
                    recommendations.append(
                        _target_payload(
                            column=column_name,
                            task_type=task_type,
                            confidence_score=score,
                            purpose=purpose,
                            reasons=[
                                "欄位語意符合 AI/LLM 分析目的",
                                "需先確認 benchmark、價格或時間定義",
                                "不應被誤用為體育分數或金融價格",
                            ],
                        )
                    )
        return _dedupe_target_candidates(recommendations)[:5]

    def _domain_targets(self, df: pd.DataFrame, primary_domain_key: str | None) -> list[dict[str, Any]]:
        domain_hints: dict[str, tuple[str, str, int, tuple[str, ...]]] = {
            HOUSING_DOMAIN.key: ("房價預測", "regression", 88, ("saleprice", "median_house_value", "price", "房價")),
            CUSTOMER_DOMAIN.key: ("客戶行為預測", "classification", 84, ("churn", "retention", "segment", "流失", "留存")),
            FINANCIAL_DOMAIN.key: ("價格或趨勢分析", "time_series", 86, ("close", "adjusted_close", "price")),
            SALES_DOMAIN.key: ("銷售績效預測", "regression", 84, ("sales", "revenue", "profit", "quantity", "營收", "銷售", "利潤")),
            SPORTS_DOMAIN.key: ("體育表現分析", "regression", 74, ("points", "assists", "rebounds", "score")),
        }
        spec = domain_hints.get(str(primary_domain_key))
        if not spec:
            return []
        purpose, task_type, base_score, hints = spec
        recommendations: list[dict[str, Any]] = []
        for column in df.columns:
            column_name = str(column)
            normalized = _normalize_name(column_name)
            if _is_unsafe_target_name(normalized):
                continue
            if any(hint in normalized for hint in hints):
                task = self._infer_task_type(df[column], preferred=task_type)
                recommendations.append(
                    _target_payload(
                        column=column_name,
                        task_type=task,
                        confidence_score=base_score,
                        purpose=purpose,
                        reasons=["欄位名稱符合資料主題", "資料型態可作為目標", "仍需依使用者問題確認"],
                    )
                )
        return recommendations

    def _generic_targets(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        for column in df.columns:
            column_name = str(column)
            normalized = _normalize_name(column_name)
            if _is_unsafe_target_name(normalized):
                continue
            series = df[column].dropna()
            if series.empty:
                continue
            task_type = self._infer_task_type(series)
            score = 42
            reasons = ["欄位型態可用於分析", "需由使用者確認是否符合問題"]
            if pd.api.types.is_numeric_dtype(series):
                score += 16
                reasons.append("連續數值欄位")
            elif 2 <= series.nunique() <= min(30, max(3, int(len(series) * 0.3))):
                score += 18
                reasons.append("類別數量合理")
            if any(keyword in normalized for keyword in ("target", "label", "price", "sales", "revenue", "profit", "amount", "value", "score", "species")):
                score += 12
                reasons.append("欄位名稱帶有目標語意")
            if score >= 58:
                candidates.append(
                    _target_payload(
                        column=column_name,
                        task_type=task_type,
                        confidence_score=min(82, score),
                        purpose="自訂目標欄位",
                        reasons=reasons,
                    )
                )
        return sorted(candidates, key=lambda item: (-int(item["confidence_score"]), str(item["column"])))

    @staticmethod
    def _infer_task_type(series: pd.Series, preferred: str | None = None) -> str:
        if preferred == "time_series":
            return "time_series"
        non_null = series.dropna()
        if non_null.empty:
            return preferred or "regression"
        unique_count = int(non_null.nunique(dropna=True))
        if not pd.api.types.is_numeric_dtype(non_null) or (2 <= unique_count <= min(20, max(3, int(len(non_null) * 0.2)))):
            return "classification" if preferred != "regression" else "regression"
        return "regression"


class DatasetStoryGenerator:
    def generate(
        self,
        *,
        df: pd.DataFrame,
        file_name: str,
        primary_domain: dict[str, Any],
        date_columns: list[str],
        numeric_columns: list[str],
        categorical_columns: list[str],
        target_recommendations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        key = str(primary_domain.get("key") or "")
        top_target = str(target_recommendations[0].get("column")) if target_recommendations else ""
        row_count = int(len(df))
        column_count = int(df.shape[1])
        if key == IRIS_DOMAIN.key:
            return {
                "one_sentence": f"這份資料記錄 {row_count:,} 筆鳶尾花樣本，最適合先用「{top_target or 'Species'}」預測花朵品種。",
                "what_is_this": "這是經典鳶尾花分類資料集，包含花萼與花瓣的長寬量測，以及每筆樣本的花朵品種。",
                "contains": ["花萼長度", "花萼寬度", "花瓣長度", "花瓣寬度", "花朵品種"],
                "can_answer": ["哪些特徵最能區分花朵品種？", "是否能根據花萼與花瓣量測預測 Species？", "花瓣長寬與品種之間有多強的關係？"],
                "cannot_answer": ["金融分析", "時間序列預測", "股票技術分析", "真實野外族群的因果推論"],
            }
        if key == AI_LLM_DOMAIN.key:
            return {
                "one_sentence": "這份資料較像 AI/LLM 模型評估資料，可用來理解模型能力、成本、價格與發布趨勢。",
                "what_is_this": "資料包含模型、benchmark、參數量、公司、發布日期、訓練成本或 API 價格等語意欄位。",
                "contains": _story_column_groups(numeric_columns, categorical_columns, date_columns),
                "can_answer": ["哪些模型或公司在 benchmark 表現較好？", "模型能力是否隨參數量或訓練成本增加？", "API 價格是否隨時間下降？"],
                "cannot_answer": ["體育表現分析", "RSI/MACD/VaR 金融技術分析", "未定義目標欄位時的可靠 AutoML 結論"],
            }
        if key == FINANCIAL_DOMAIN.key:
            return {
                "one_sentence": "這份資料具備金融時間序列特徵，可先檢查價格、成交量與時間趨勢。",
                "what_is_this": "資料包含日期與價格欄位，適合做趨勢、報酬、波動與基礎時間序列分析。",
                "contains": _story_column_groups(numeric_columns, categorical_columns, date_columns),
                "can_answer": ["價格是否呈現趨勢？", "波動是否增加？", "哪些期間變化最明顯？"],
                "cannot_answer": ["沒有外部事件與基本面資料時，不能作為投資建議。"],
            }
        labels = {
            HOUSING_DOMAIN.key: ("房價預測資料", ["哪些因素與房價最相關？", "是否能預測價格區間？"], ["不能直接證明地區或坪數造成價格變化。"]),
            CUSTOMER_DOMAIN.key: ("客戶行為資料", ["哪些客戶特徵與流失、消費或分群相關？", "哪些客群需要優先追蹤？"], ["不能在沒有同意與合規審查下做敏感個資決策。"]),
            SALES_DOMAIN.key: ("銷售績效資料", ["哪些產品、地區或期間帶動營收？", "是否能預測銷售或利潤？"], ["不能單靠內部表格推論市場總需求。"]),
            SPORTS_DOMAIN.key: ("體育表現資料", ["哪些球員或球隊指標與表現相關？", "是否能建立排名或分群？"], ["不能把 score 以外的任意數值當成勝負原因。"]),
        }
        subject, can_answer, cannot_answer = labels.get(
            key,
            ("待確認資料", ["資料有哪些欄位與缺失值？", "哪些欄位可能適合作為分析目標？"], ["尚未確認業務語意前，不適合直接做決策。"]),
        )
        return {
            "one_sentence": f"這份資料看起來像{subject}，共有 {row_count:,} 筆與 {column_count:,} 欄；建議先確認分析目標。",
            "what_is_this": f"系統根據檔名「{file_name}」與欄位語意判斷，這份資料目前最接近{subject}。",
            "contains": _story_column_groups(numeric_columns, categorical_columns, date_columns),
            "can_answer": can_answer,
            "cannot_answer": cannot_answer,
        }


def build_dataset_understanding(df: pd.DataFrame, file_name: str) -> dict[str, Any]:
    return DataUnderstandingEngine().analyze(df, file_name)


def recommend_target_columns_for_purpose(
    df: pd.DataFrame,
    *,
    primary_domain_key: str | None = None,
) -> list[dict[str, Any]]:
    return TargetRecommendationEngine().recommend(df, primary_domain_key=primary_domain_key)


def recommended_target_column_names(understanding: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for item in understanding.get("target_recommendations") or []:
        column = item.get("column")
        if isinstance(column, str) and column not in names:
            names.append(column)
            continue
        for grouped_column in item.get("columns") or []:
            if isinstance(grouped_column, str) and grouped_column not in names:
                names.append(grouped_column)
    return names[:5]


def _confidence_component(key: str, label: str, value: int | float, reason: str) -> dict[str, Any]:
    numeric_value = int(round(value))
    return {
        "key": key,
        "label": label,
        "value": numeric_value,
        "display": f"{'+' if numeric_value >= 0 else ''}{numeric_value}",
        "reason": reason,
    }


def _target_payload(
    *,
    column: str,
    task_type: str,
    confidence_score: int,
    purpose: str,
    reasons: list[str],
) -> dict[str, Any]:
    task_label_map = {
        "classification": "分類",
        "regression": "回歸",
        "time_series": "時間趨勢",
        "clustering": "分群",
    }
    score = int(max(0, min(100, confidence_score)))
    return {
        "column": column,
        "columns": [column],
        "purpose": purpose,
        "task_type": task_type,
        "task_type_label": task_label_map.get(task_type, task_type),
        "confidence_score": score,
        "confidence": "high" if score >= 80 else "medium" if score >= 65 else "low",
        "reasons": reasons,
        "reason": "；".join(reasons),
    }


def _dedupe_target_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_column: dict[str, dict[str, Any]] = {}
    for item in candidates:
        column = str(item.get("column") or "")
        if not column:
            continue
        existing = by_column.get(column)
        if existing is None or int(item.get("confidence_score") or 0) > int(existing.get("confidence_score") or 0):
            by_column[column] = item
    return sorted(by_column.values(), key=lambda item: (-int(item.get("confidence_score") or 0), str(item.get("column"))))


def _story_column_groups(
    numeric_columns: list[str],
    categorical_columns: list[str],
    date_columns: list[str],
) -> list[str]:
    groups: list[str] = []
    if numeric_columns:
        groups.append(f"數值欄位：{', '.join(numeric_columns[:6])}")
    if categorical_columns:
        groups.append(f"類別欄位：{', '.join(categorical_columns[:6])}")
    if date_columns:
        groups.append(f"日期欄位：{', '.join(date_columns[:4])}")
    return groups or ["欄位語意仍需人工確認"]


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
    if primary_domain_key == IRIS_DOMAIN.key:
        return [
            {"key": "species_classification", "label": "花朵品種分類"},
            {"key": "feature_importance", "label": "花萼與花瓣特徵重要性"},
            {"key": "measurement_relationship", "label": "花瓣與花萼量測關係"},
            {"key": "model_comparison", "label": "分類模型比較"},
        ]
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
    if primary_domain_key == HOUSING_DOMAIN.key:
        return [
            {"key": "price_prediction", "label": "房價預測"},
            {"key": "feature_importance", "label": "房價關鍵因素"},
            {"key": "regional_comparison", "label": "地區比較"},
        ]
    if primary_domain_key == CUSTOMER_DOMAIN.key:
        return [
            {"key": "customer_segmentation", "label": "客戶分群"},
            {"key": "churn_prediction", "label": "流失或留存預測"},
            {"key": "behavior_drivers", "label": "客戶行為關鍵因素"},
        ]
    if primary_domain_key == SALES_DOMAIN.key:
        return [
            {"key": "sales_performance", "label": "銷售績效分析"},
            {"key": "revenue_prediction", "label": "營收或銷售預測"},
            {"key": "product_region_drivers", "label": "產品與地區貢獻分析"},
        ]
    if primary_domain_key == SPORTS_DOMAIN.key:
        return [
            {"key": "performance_ranking", "label": "球員或球隊表現排名"},
            {"key": "clustering", "label": "表現分群"},
            {"key": "metric_drivers", "label": "關鍵表現指標"},
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
