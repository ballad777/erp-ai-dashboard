from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import re
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

WEATHER_DOMAIN = DomainDefinition(
    key="weather",
    label="天氣資料集",
    clues=(
        "weather",
        "precipitation",
        "rain",
        "rainfall",
        "snow",
        "temp",
        "temperature",
        "temp_max",
        "temp_min",
        "wind",
        "humidity",
        "pressure",
        "station",
        "氣溫",
        "降雨",
        "雨量",
        "濕度",
        "風速",
    ),
    strong_clues=("weather", "precipitation", "temp_max", "temp_min", "temperature", "humidity"),
)

BIOLOGY_DOMAIN = DomainDefinition(
    key="biology",
    label="生物觀測資料集",
    clues=(
        "species",
        "genus",
        "family",
        "organism",
        "island",
        "bill",
        "flipper",
        "body_mass",
        "body",
        "mass",
        "sepal",
        "petal",
        "sex",
        "品種",
        "物種",
        "生物",
    ),
    strong_clues=("species", "body_mass", "flipper", "bill_length", "sepal", "petal", "品種", "物種"),
)

MEDICAL_DOMAIN = DomainDefinition(
    key="medical_health",
    label="醫療或健康資料集",
    clues=(
        "patient",
        "diagnosis",
        "diagnostic",
        "disease",
        "cancer",
        "tumor",
        "malignant",
        "benign",
        "blood",
        "pressure",
        "glucose",
        "insulin",
        "bmi",
        "risk",
        "health",
        "medical",
        "病患",
        "診斷",
        "疾病",
        "腫瘤",
        "血壓",
        "血糖",
    ),
    strong_clues=("diagnosis", "patient", "cancer", "tumor", "glucose", "病患", "診斷"),
)

AUTOMOTIVE_DOMAIN = DomainDefinition(
    key="automotive",
    label="汽車或車輛資料集",
    clues=(
        "car",
        "cars",
        "vehicle",
        "auto",
        "automobile",
        "mpg",
        "mileage",
        "horsepower",
        "cylinders",
        "acceleration",
        "model_year",
        "origin",
        "fuel",
        "transmission",
        "engine",
        "汽車",
        "車輛",
        "里程",
        "油耗",
        "馬力",
    ),
    strong_clues=("mpg", "horsepower", "cylinders", "vehicle", "mileage", "油耗"),
)

TRANSPORT_DOMAIN = DomainDefinition(
    key="transport",
    label="交通運輸資料集",
    clues=(
        "taxi",
        "trip",
        "passenger",
        "passengers",
        "pickup",
        "dropoff",
        "fare",
        "airport",
        "flight",
        "airline",
        "carrier",
        "origin",
        "destination",
        "distance",
        "delay",
        "交通",
        "航班",
        "機場",
        "乘客",
        "車程",
    ),
    strong_clues=("pickup", "dropoff", "fare", "airport", "flight", "passengers"),
)

AGRICULTURE_DOMAIN = DomainDefinition(
    key="agriculture",
    label="農業或產量資料集",
    clues=(
        "yield",
        "crop",
        "barley",
        "corn",
        "wheat",
        "cotton",
        "farm",
        "agriculture",
        "variety",
        "site",
        "harvest",
        "農業",
        "作物",
        "產量",
    ),
    strong_clues=("yield", "crop", "barley", "agriculture", "variety", "產量"),
)

DEMOGRAPHICS_DOMAIN = DomainDefinition(
    key="demographics",
    label="人口與社會統計資料集",
    clues=(
        "population",
        "people",
        "age",
        "sex",
        "gender",
        "country",
        "continent",
        "life_expectancy",
        "gdp",
        "pop",
        "demographic",
        "人口",
        "年齡",
        "性別",
    ),
    strong_clues=("population", "life_expectancy", "gdp", "country", "人口"),
)

EDUCATION_DOMAIN = DomainDefinition(
    key="education",
    label="教育或學校資料集",
    clues=(
        "school",
        "college",
        "university",
        "student",
        "major",
        "earnings",
        "education",
        "score",
        "grade",
        "學校",
        "學生",
        "教育",
        "科系",
    ),
    strong_clues=("school", "student", "major", "education", "學校", "學生"),
)

POLITICS_DOMAIN = DomainDefinition(
    key="politics",
    label="選舉或政治資料集",
    clues=(
        "election",
        "candidate",
        "party",
        "votes",
        "winner",
        "result",
        "district",
        "precinct",
        "選舉",
        "候選人",
        "政黨",
        "投票",
    ),
    strong_clues=("election", "candidate", "votes", "winner", "選舉"),
)

FOOD_QUALITY_DOMAIN = DomainDefinition(
    key="food_quality",
    label="食品品質資料集",
    clues=(
        "quality",
        "alcohol",
        "acidity",
        "sugar",
        "chlorides",
        "density",
        "ph",
        "sulphates",
        "wine",
        "food",
        "食品",
        "品質",
    ),
    strong_clues=("quality", "alcohol", "acidity", "chlorides", "wine", "品質"),
)

CLIMATE_DOMAIN = DomainDefinition(
    key="climate_environment",
    label="氣候或環境資料集",
    clues=(
        "co2",
        "carbon",
        "emission",
        "emissions",
        "concentration",
        "climate",
        "temperature",
        "anomaly",
        "ppm",
        "氣候",
        "碳",
        "排放",
    ),
    strong_clues=("co2", "carbon", "concentration", "emissions", "ppm"),
)

GENERIC_DOMAIN = DomainDefinition(
    key="unclassified_dataset",
    label="待確認資料集",
    clues=(),
)

DOMAIN_DEFINITIONS = (
    AI_LLM_DOMAIN,
    FINANCIAL_DOMAIN,
    WEATHER_DOMAIN,
    BIOLOGY_DOMAIN,
    MEDICAL_DOMAIN,
    AUTOMOTIVE_DOMAIN,
    TRANSPORT_DOMAIN,
    HOUSING_DOMAIN,
    CUSTOMER_DOMAIN,
    SALES_DOMAIN,
    AGRICULTURE_DOMAIN,
    DEMOGRAPHICS_DOMAIN,
    EDUCATION_DOMAIN,
    POLITICS_DOMAIN,
    FOOD_QUALITY_DOMAIN,
    CLIMATE_DOMAIN,
    SPORTS_DOMAIN,
)

DATE_NAME_HINTS = ("date", "time", "timestamp", "year_month", "release_date", "created_at", "updated_at")
ID_NAME_HINTS = ("id", "uuid", "guid", "index", "row_number")
TEXT_NAME_HINTS = ("description", "summary", "notes", "text", "content", "url")
TARGET_NAME_HINTS = (
    "target",
    "label",
    "class",
    "category",
    "species",
    "price",
    "sales",
    "revenue",
    "profit",
    "amount",
    "value",
    "score",
    "result",
    "outcome",
    "status",
    "churn",
    "risk",
)
SUBMISSION_NAME_HINTS = ("submission", "submit", "prediction", "predicted", "answer")
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


class DataDiagnostics:
    def analyze(self, df: pd.DataFrame) -> dict[str, Any]:
        row_count = int(len(df))
        column_count = int(df.shape[1])
        columns = [str(column) for column in df.columns]
        missing_ratio_by_column = {
            str(column): round(float(df[column].isna().mean()), 6)
            for column in df.columns
        }
        unique_ratio_by_column: dict[str, float] = {}
        constant_columns: list[str] = []
        high_cardinality_columns: list[str] = []
        class_balance: dict[str, Any] = {}

        for column in df.columns:
            column_name = str(column)
            non_null = df[column].dropna()
            unique_count = int(non_null.nunique(dropna=True))
            unique_ratio = unique_count / max(1, int(len(non_null)))
            unique_ratio_by_column[column_name] = round(unique_ratio, 6)
            if unique_count <= 1:
                constant_columns.append(column_name)
            if unique_count >= HIGH_CARDINALITY_MIN_UNIQUE_FOR_DIAGNOSTICS or unique_ratio >= 0.85:
                high_cardinality_columns.append(column_name)
            if 2 <= unique_count <= 30 and not pd.api.types.is_numeric_dtype(non_null):
                counts = non_null.astype(str).value_counts(dropna=True)
                class_balance[column_name] = {
                    "classes": int(len(counts)),
                    "min_count": int(counts.min()) if not counts.empty else 0,
                    "max_count": int(counts.max()) if not counts.empty else 0,
                    "minority_ratio": round(float(counts.min() / max(1, counts.sum())), 6) if not counts.empty else 0,
                }

        id_like_columns = [
            str(column) for column in df.columns
            if _is_id_like_column_name(str(column), df[column])
        ]
        datetime_columns = _detect_date_columns(df)
        numeric_columns = [str(column) for column in df.select_dtypes(include="number").columns]
        text_columns = _detect_text_columns(df)
        categorical_columns = _detect_categorical_columns(df, text_columns=text_columns)
        possible_leakage_columns = [
            str(column) for column in df.columns
            if _looks_like_leakage_or_prediction_column(str(column))
        ]
        outlier_columns = _detect_outlier_columns(df)
        header_issue = _detect_header_issue(columns)
        candidate_target_columns = TargetAdvisor().recommend(df, diagnostics=None)
        usable_feature_count = len(
            [
                column for column in df.columns
                if str(column) not in id_like_columns
                and str(column) not in constant_columns
                and str(column) not in text_columns
                and not _looks_like_leakage_or_prediction_column(str(column))
            ]
        )

        return {
            "row_count": row_count,
            "column_count": column_count,
            "column_names": columns,
            "dtypes": {str(column): str(dtype) for column, dtype in df.dtypes.items()},
            "missing_ratio": round(float(df.isna().sum().sum() / max(1, row_count * column_count)), 6),
            "missing_ratio_by_column": missing_ratio_by_column,
            "duplicate_ratio": round(float(df.duplicated().sum() / max(1, row_count)), 6),
            "unique_ratio": unique_ratio_by_column,
            "constant_columns": constant_columns,
            "id_like_columns": id_like_columns,
            "datetime_columns": datetime_columns,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "text_columns": text_columns,
            "high_cardinality_columns": high_cardinality_columns,
            "candidate_target_columns": candidate_target_columns,
            "possible_leakage_columns": possible_leakage_columns,
            "outlier_columns": outlier_columns,
            "suspected_header_issue": header_issue["suspected"],
            "header_issue_reasons": header_issue["reasons"],
            "class_balance": class_balance,
            "usable_feature_count": int(usable_feature_count),
        }


HIGH_CARDINALITY_MIN_UNIQUE_FOR_DIAGNOSTICS = 500


class DataUnderstandingEngine:
    """Rule-based semantic profiler for uploaded tabular datasets.

    The engine intentionally uses transparent scoring instead of opaque labels.
    Every returned classification carries evidence columns, confidence, and
    limits so the UI can explain why the system made the call.
    """

    def analyze(self, df: pd.DataFrame, file_name: str) -> dict[str, Any]:
        diagnostics = DataDiagnostics().analyze(df)
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
        domain_scores = _score_domains(df, columns, file_name=file_name, date_columns=date_columns)
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
        task_router = TaskRouter()
        executable_tasks = task_router.route(df=df, diagnostics=diagnostics, primary_domain=primary_domain)
        target_recommendations = TargetAdvisor().recommend(df, diagnostics=diagnostics)
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
            "data_diagnostics": diagnostics,
            "task_recommendations": executable_tasks,
            "analysis_context": _analysis_context_payload(df=df, file_name=file_name, columns=columns),
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


class TargetAdvisor:
    def recommend(
        self,
        df: pd.DataFrame,
        *,
        diagnostics: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        candidates = self._generic_targets(df, diagnostics=diagnostics or {})
        return _dedupe_target_candidates(candidates)[:5]

    def _generic_targets(self, df: pd.DataFrame, *, diagnostics: dict[str, Any]) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        usable_feature_count = int(diagnostics.get("usable_feature_count") or max(0, df.shape[1] - 1))
        for column in df.columns:
            column_name = str(column)
            normalized = _normalize_name(column_name)
            warnings: list[str] = []
            why_not_higher: list[str] = []
            reasons: list[str] = []
            series = df[column].dropna()
            if series.empty:
                continue
            missing_ratio = 1 - (len(series) / max(1, len(df)))
            unique_count = int(series.nunique(dropna=True))
            unique_ratio = unique_count / max(1, int(len(series)))

            score = 35
            if _is_unsafe_target_name(normalized) or _is_id_like_column_name(column_name, df[column]):
                score -= 55
                warnings.append("疑似 ID 或索引欄位，不適合作為目標。")
            if _looks_like_leakage_or_prediction_column(column_name):
                score -= 35
                warnings.append("欄位名稱像答案、提交或預測欄位，需要人工確認。")
            if any(keyword in normalized for keyword in TARGET_NAME_HINTS):
                score += 18
                reasons.append("欄位名稱具有結果或目標語意。")
            if missing_ratio >= 0.4:
                score -= 25
                warnings.append("缺失比例過高。")
            elif missing_ratio > 0:
                score -= 5
                why_not_higher.append("仍存在缺失值。")
            if unique_count <= 1:
                score -= 60
                warnings.append("常數欄位無法作為建模目標。")
            if unique_ratio >= 0.95 and len(series) >= 20:
                score -= 35
                warnings.append("唯一值比例過高，較像識別碼或自由文字。")

            task_type = self._infer_task_type(series)
            if task_type == "classification":
                if 2 <= unique_count <= min(30, max(3, int(len(series) * 0.25))):
                    score += 18
                    reasons.append("類別數量合理，適合分類任務。")
                counts = series.astype(str).value_counts()
                if not counts.empty and int(counts.min()) < 2:
                    score -= 18
                    warnings.append("至少一個類別樣本少於 2 筆，無法穩定切分訓練/測試。")
            elif task_type == "regression":
                if pd.api.types.is_numeric_dtype(series) and unique_count >= max(8, min(30, int(len(series) * 0.1))):
                    score += 15
                    reasons.append("連續數值欄位，具備回歸目標條件。")
                else:
                    why_not_higher.append("數值變異不足或唯一值偏少。")

            if usable_feature_count < 2:
                score -= 30
                warnings.append("可用特徵少於 2 個，建模支撐不足。")

            score = int(max(0, min(100, score)))
            if score >= 45:
                candidates.append(
                    _target_payload(
                        column=column_name,
                        task_type=task_type,
                        confidence_score=score,
                        purpose="自訂目標欄位",
                        reasons=reasons or ["欄位型態可用於分析，但仍需使用者確認問題定義。"],
                        warnings=warnings,
                        why_not_higher=why_not_higher,
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


class TargetRecommendationEngine(TargetAdvisor):
    """Backward-compatible alias for existing imports/tests."""

    def recommend(
        self,
        df: pd.DataFrame,
        *,
        primary_domain_key: str | None = None,
        diagnostics: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        _ = primary_domain_key
        return super().recommend(df, diagnostics=diagnostics)


class TaskRouter:
    def route(
        self,
        *,
        df: pd.DataFrame,
        diagnostics: dict[str, Any],
        primary_domain: dict[str, Any],
    ) -> list[dict[str, Any]]:
        numeric_columns = [str(column) for column in diagnostics.get("numeric_columns") or []]
        categorical_columns = [str(column) for column in diagnostics.get("categorical_columns") or []]
        datetime_columns = [str(column) for column in diagnostics.get("datetime_columns") or []]
        target_candidates = [dict(item) for item in diagnostics.get("candidate_target_columns") or []]
        usable_feature_count = int(diagnostics.get("usable_feature_count") or 0)
        row_count = int(diagnostics.get("row_count") or len(df))
        financial_eligible = bool(_financial_eligibility(df=df, primary_domain_key=str(primary_domain.get("key") or ""), date_columns=datetime_columns).get("eligible"))
        top_classification = next((item for item in target_candidates if item.get("task_type") == "classification" and int(item.get("score") or 0) >= 60), None)
        top_regression = next((item for item in target_candidates if item.get("task_type") == "regression" and int(item.get("score") or 0) >= 60), None)

        return [
            _task_payload(
                task="EDA",
                can_run=row_count > 0 and len(df.columns) > 0,
                confidence=95 if row_count > 0 else 0,
                required_columns=[],
                missing_requirements=[] if row_count > 0 else ["至少一列資料"],
                reason="資料探索只需要可讀取的表格資料。",
                warning="",
            ),
            _task_payload(
                task="classification",
                can_run=bool(top_classification) and usable_feature_count >= 2 and row_count >= 10,
                confidence=int(top_classification.get("score") if top_classification else 0),
                required_columns=[str(top_classification.get("column"))] if top_classification else ["可靠分類目標欄位"],
                missing_requirements=_task_missing_requirements(
                    [
                        (bool(top_classification), "可靠分類目標欄位"),
                        (usable_feature_count >= 2, "至少 2 個可用特徵"),
                        (row_count >= 10, "至少 10 筆資料"),
                    ]
                ),
                reason="分類任務需要低到中基數的目標欄位與足夠特徵。",
                warning="若類別樣本太少，系統會阻止或降低可信度。",
            ),
            _task_payload(
                task="regression",
                can_run=bool(top_regression) and usable_feature_count >= 2 and row_count >= 10,
                confidence=int(top_regression.get("score") if top_regression else 0),
                required_columns=[str(top_regression.get("column"))] if top_regression else ["可靠數值目標欄位"],
                missing_requirements=_task_missing_requirements(
                    [
                        (bool(top_regression), "可靠數值目標欄位"),
                        (usable_feature_count >= 2, "至少 2 個可用特徵"),
                        (row_count >= 10, "至少 10 筆資料"),
                    ]
                ),
                reason="回歸任務需要連續數值目標與足夠變異。",
                warning="若目標像 ID、日期或答案欄位，應先人工確認。",
            ),
            _task_payload(
                task="time_series",
                can_run=bool(datetime_columns) and bool(numeric_columns) and row_count >= 24,
                confidence=75 if bool(datetime_columns) and bool(numeric_columns) else 25,
                required_columns=[*(datetime_columns[:1] or ["日期欄位"]), *(numeric_columns[:1] or ["數值欄位"])],
                missing_requirements=_task_missing_requirements(
                    [
                        (bool(datetime_columns), "日期欄位"),
                        (bool(numeric_columns), "數值欄位"),
                        (row_count >= 24, "至少 24 個時間點"),
                    ]
                ),
                reason="時間序列至少需要可排序日期與足夠時間點。",
                warning="有日期不代表可預測；資料需具備穩定時間粒度。",
            ),
            _task_payload(
                task="financial_analysis",
                can_run=financial_eligible,
                confidence=90 if financial_eligible else 0,
                required_columns=["日期欄位", "close/price/open/high/low/adjusted_close"],
                missing_requirements=[] if financial_eligible else ["金融日期欄位與價格欄位"],
                reason="金融分析只在同時具備日期與金融價格欄位時啟用。",
                warning="" if financial_eligible else "不可對非金融資料產生 RSI、MACD、VaR。",
            ),
            _task_payload(
                task="clustering",
                can_run=len(numeric_columns) >= 2 and row_count >= 10,
                confidence=70 if len(numeric_columns) >= 2 and row_count >= 10 else 20,
                required_columns=numeric_columns[:4] or ["至少 2 個數值欄位"],
                missing_requirements=_task_missing_requirements(
                    [
                        (len(numeric_columns) >= 2, "至少 2 個數值欄位"),
                        (row_count >= 10, "至少 10 筆資料"),
                    ]
                ),
                reason="分群不需要目標欄位，但需要足夠數值特徵。",
                warning="分群結果是探索，不等於真實族群或因果結論。",
            ),
            _task_payload(
                task="anomaly_detection",
                can_run=len(numeric_columns) >= 1 and row_count >= 20,
                confidence=65 if len(numeric_columns) >= 1 and row_count >= 20 else 20,
                required_columns=numeric_columns[:4] or ["至少 1 個數值欄位"],
                missing_requirements=_task_missing_requirements(
                    [
                        (len(numeric_columns) >= 1, "至少 1 個數值欄位"),
                        (row_count >= 20, "至少 20 筆資料"),
                    ]
                ),
                reason="異常偵測可用於探索極端值，但不能直接判定資料錯誤。",
                warning="低樣本異常偵測容易誤判。",
            ),
        ]


class AnalysisIntegrityValidator:
    def validate_columns_exist(
        self,
        *,
        schema_columns: list[str],
        referenced_columns: list[str],
        context: str,
    ) -> None:
        schema = set(schema_columns)
        missing = sorted({column for column in referenced_columns if column and column not in schema})
        if missing:
            raise ValueError(f"{context} 引用了不存在於目前 schema 的欄位：{', '.join(missing)}")


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
        if key == AI_LLM_DOMAIN.key:
            return {
                "one_sentence": "這份資料具備 AI/LLM 模型評估語意欄位；這是資料類型推薦，不是不可變結論。",
                "what_is_this": "目前資料中可驗證欄位包含模型、benchmark、參數量、公司、發布日期、成本或 API 價格等線索。",
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
            HOUSING_DOMAIN.key: ("房價預測資料", ["哪些數值或類別欄位與價格目標一起變動？", "是否具備足夠欄位支撐價格預測？"], ["只有 price 不足以證明這是房價資料。"]),
            CUSTOMER_DOMAIN.key: ("客戶行為資料", ["哪些客戶欄位與分群、流失或消費目標相關？", "是否可做分類、分群或留存探索？"], ["不能在沒有同意與合規審查下做敏感個資決策。"]),
            SALES_DOMAIN.key: ("銷售績效資料", ["哪些產品、地區或期間欄位與銷售/營收一起變動？", "是否能預測銷售或利潤？"], ["不能單靠內部表格推論市場總需求。"]),
            SPORTS_DOMAIN.key: ("體育表現資料", ["哪些球員或球隊欄位與表現指標相關？", "是否能建立排名或分群？"], ["不能只因為有 score 就判斷為體育資料。"]),
            WEATHER_DOMAIN.key: ("天氣資料", ["降雨、氣溫或風速是否有季節變化？", "是否能用日期與氣象欄位預測天氣類別？"], ["不能只靠單一城市資料推論其他地區天氣。"]),
            BIOLOGY_DOMAIN.key: ("生物觀測資料", ["哪些測量欄位最能區分物種或群體？", "是否能用外觀特徵預測分類標籤？"], ["不能把相關性直接解讀成生物因果。"]),
            MEDICAL_DOMAIN.key: ("醫療或健康資料", ["哪些特徵與診斷、風險或健康結果一起變動？", "是否能建立初步分類或風險排序？"], ["不能直接作為醫療診斷；需專業驗證與合規審查。"]),
            AUTOMOTIVE_DOMAIN.key: ("汽車或車輛資料", ["哪些車輛特徵與油耗、馬力或價格一起變動？", "是否能比較不同車款或年份的差異？"], ["不能只靠表格推論維修、安全或市場全貌。"]),
            TRANSPORT_DOMAIN.key: ("交通運輸資料", ["路線、距離、時間或乘客數如何影響旅程結果？", "是否能找出延誤、費用或流量異常？"], ["不能在沒有外部事件資料時直接判定原因。"]),
            AGRICULTURE_DOMAIN.key: ("農業或產量資料", ["不同作物、品種、地區或年份的產量差異？", "哪些欄位與產量或出口表現一起變動？"], ["不能只靠觀測資料推論氣候或政策造成的因果。"]),
            DEMOGRAPHICS_DOMAIN.key: ("人口與社會統計資料", ["人口、年齡、性別或國家指標如何變化？", "是否能比較不同地區或年份的差異？"], ["不能忽略資料定義、抽樣方式與時間背景。"]),
            EDUCATION_DOMAIN.key: ("教育或學校資料", ["不同學校、科系或群體的結果差異？", "哪些欄位與成績、收入或表現一起變動？"], ["不能只靠表格資料判定教育品質或個人能力。"]),
            POLITICS_DOMAIN.key: ("選舉或政治資料", ["候選人、政黨或地區結果如何分布？", "是否能比較勝負、票數或支持度差異？"], ["不能把歷史選舉資料直接當成未來預測。"]),
            FOOD_QUALITY_DOMAIN.key: ("食品品質資料", ["哪些化學或感官欄位與品質評分一起變動？", "是否能建立品質分類或評分模型？"], ["不能取代實驗室檢驗或食品安全判定。"]),
            CLIMATE_DOMAIN.key: ("氣候或環境資料", ["濃度、排放或環境指標是否有長期趨勢？", "哪些時間點變化最明顯？"], ["不能只靠單一表格完成完整氣候歸因。"]),
        }
        subject, can_answer, cannot_answer = labels.get(
            key,
            ("待確認資料", ["資料有哪些欄位與缺失值？", "哪些欄位可能適合作為分析目標？"], ["尚未確認業務語意前，不適合直接做決策。"]),
        )
        return {
            "one_sentence": f"這份資料較像「{primary_domain.get('label', subject)}」，共有 {row_count:,} 筆與 {column_count:,} 欄；建議先確認欄位定義，再選擇分析目的。",
            "what_is_this": f"系統只根據目前資料欄位與型態判斷；檔名「{file_name}」僅作低權重輔助訊號。",
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
    warnings: list[str] | None = None,
    why_not_higher: list[str] | None = None,
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
        "score": score,
        "confidence": "high" if score >= 80 else "medium" if score >= 65 else "low",
        "reasons": reasons,
        "reason": "；".join(reasons),
        "warnings": warnings or [],
        "why_not_higher": why_not_higher or [],
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


def _task_payload(
    *,
    task: str,
    can_run: bool,
    confidence: int,
    required_columns: list[str],
    missing_requirements: list[str],
    reason: str,
    warning: str,
) -> dict[str, Any]:
    return {
        "task": task,
        "can_run": bool(can_run),
        "confidence": int(max(0, min(100, confidence))),
        "required_columns": required_columns,
        "missing_requirements": missing_requirements,
        "reason": reason,
        "warning": warning,
    }


def _task_missing_requirements(checks: list[tuple[bool, str]]) -> list[str]:
    return [label for passed, label in checks if not passed]


def _analysis_context_payload(*, df: pd.DataFrame, file_name: str, columns: list[str]) -> dict[str, Any]:
    schema_parts = [
        {"name": str(column), "dtype": str(df[column].dtype)}
        for column in df.columns
    ]
    schema_json = json.dumps(schema_parts, ensure_ascii=False, sort_keys=True)
    column_signature = "|".join(f"{item['name']}:{item['dtype']}" for item in schema_parts)
    schema_fingerprint = hashlib.sha256(schema_json.encode("utf-8")).hexdigest()
    file_payload = json.dumps(
        {
            "file_name": file_name,
            "row_count": int(len(df)),
            "column_signature": column_signature,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    file_fingerprint = hashlib.sha256(file_payload.encode("utf-8")).hexdigest()
    dataset_id = hashlib.sha256(f"{file_fingerprint}:{schema_fingerprint}".encode("utf-8")).hexdigest()[:24]
    run_id = hashlib.sha256(f"{dataset_id}:{len(df)}:{len(columns)}".encode("utf-8")).hexdigest()[:24]
    return {
        "dataset_id": dataset_id,
        "run_id": run_id,
        "schema_fingerprint": schema_fingerprint,
        "file_fingerprint": file_fingerprint,
        "column_signature": column_signature,
        "column_count": len(columns),
        "row_count": int(len(df)),
    }


def _is_id_like_column_name(column_name: str, series: pd.Series) -> bool:
    normalized = _normalize_name(column_name)
    non_null = series.dropna()
    unique_ratio = float(non_null.nunique(dropna=True) / max(1, len(non_null))) if len(non_null) else 0
    return (
        normalized in {"id", "uuid", "guid", "index", "row_id", "source_row_number"}
        or normalized.endswith("_id")
        or normalized.endswith("_uuid")
        or normalized.endswith("_guid")
        or (unique_ratio >= 0.98 and any(hint in normalized for hint in ID_NAME_HINTS))
    )


def _looks_like_leakage_or_prediction_column(column_name: str) -> bool:
    normalized = _normalize_name(column_name)
    return any(hint in normalized for hint in SUBMISSION_NAME_HINTS) or normalized in {
        "pred",
        "prediction",
        "predicted",
        "answer",
        "output",
    }


def _detect_outlier_columns(df: pd.DataFrame) -> list[dict[str, Any]]:
    outliers: list[dict[str, Any]] = []
    numeric = df.select_dtypes(include="number")
    for column in numeric.columns:
        values = pd.to_numeric(numeric[column], errors="coerce").dropna()
        if len(values) < 12:
            continue
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        mask = (values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)
        count = int(mask.sum())
        if count:
            outliers.append(
                {
                    "column": str(column),
                    "count": count,
                    "ratio": round(float(count / max(1, len(values))), 6),
                    "method": "IQR 1.5x",
                }
            )
    return outliers


def _detect_header_issue(columns: list[str]) -> dict[str, Any]:
    if not columns:
        return {"suspected": False, "reasons": []}
    numeric_like = 0
    short_code_like = 0
    value_like = 0
    for column in columns:
        name = str(column).strip()
        normalized = _normalize_name(name)
        if re.fullmatch(r"-?\d+(\.\d+)?", name):
            numeric_like += 1
            value_like += 1
            continue
        if re.fullmatch(r"-?\d+(\.\d+)?[eE][+-]?\d+", name):
            numeric_like += 1
            value_like += 1
            continue
        if len(normalized) <= 2 and normalized not in {"id", "ph"}:
            short_code_like += 1
        if re.fullmatch(r"[a-z]?\d+(\.\d+)?", normalized):
            value_like += 1
    total = max(1, len(columns))
    reasons: list[str] = []
    if numeric_like / total >= 0.35:
        reasons.append("超過三分之一欄位名稱像數值資料。")
    if (numeric_like + short_code_like) / total >= 0.5 and total >= 5:
        reasons.append("多數欄位名稱過短或像資料值，可能缺少正式表頭。")
    if value_like >= 3 and total >= 5:
        reasons.append("多個欄位名稱像第一列資料值。")
    return {"suspected": bool(reasons), "reasons": reasons}


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
    role_keys = {role["role_key"] for role in table_roles}

    if {"training_dataset", "unlabeled_prediction_dataset"}.issubset(role_keys) or "submission_format" in role_keys:
        strategy = "train_predict_workflow"
        label = "訓練 / 預測工作流"
        reason = "多檔案結構像 train/test/submission 流程；不可把未標籤 test 或 submission format 當訓練資料合併。"
        warnings = ["需要使用者確認目標欄位與哪個檔案是訓練資料後，才可執行模型。"]
    elif _is_union_candidate(column_sets, understandings):
        strategy = "union"
        label = "垂直合併"
        reason = "欄位結構高度相似，較像同一種資料的不同批次或不同時間片段。"
        warnings = []
    elif join_key_candidates:
        strategy = "relational_analysis"
        label = "多表關聯分析"
        reason = "檔案之間存在共同鍵候選，適合先確認鍵值定義後做關聯分析。"
        warnings = [
            "不建議直接垂直合併；需先確認共同鍵與每張表代表的資料角色。",
            "Join 前需確認鍵值唯一性，避免多對多合併放大資料列。低信心時不會自動合併。",
        ]
    else:
        strategy = "keep_separate"
        label = "保持分表分析"
        reason = "欄位與主題差異較大，目前不建議自動合併。"
        warnings = ["若要合併，請先手動指定共同鍵或確認每張表代表同一種資料。"]

    return {
        "recommended_strategy": strategy,
        "label": label,
        "confidence_score": 88 if strategy == "union" else 72 if strategy in {"relational_analysis", "train_predict_workflow"} else 55,
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


def _score_domains(df: pd.DataFrame, columns: list[str], *, file_name: str, date_columns: list[str]) -> list[dict[str, Any]]:
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
            if definition.key == FINANCIAL_DOMAIN.key and _is_financial_price_column(original, df[original]):
                evidence.append(original)
                score += 7
        if definition.key == FINANCIAL_DOMAIN.key and date_columns:
            score += 5
            evidence.extend(column for column in date_columns if column not in evidence)
            for price_column in _financial_price_columns(df, date_columns):
                if price_column not in evidence:
                    evidence.append(price_column)
                    score += 7
        if any(clue in file_hint for clue in definition.clues) and score >= 4:
            score += 1
        if score > 0 and len(set(evidence)) >= 2:
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
    counter_evidence: list[str] = []
    if definition.key == FINANCIAL_DOMAIN.key and not any(_is_financial_price_column(column) or _ticker_prefix(column) for column in evidence):
        counter_evidence.append("尚未同時確認日期欄位與標準金融價格欄位。")
    if len(evidence) < 3 and definition.key != GENERIC_DOMAIN.key:
        counter_evidence.append("可用證據欄位偏少，資料類型仍需人工確認。")
    uncertainty_reason = "證據不足，需使用者確認資料語意。" if confidence_score < 70 or counter_evidence else ""
    return {
        "key": definition.key,
        "label": definition.label,
        "predicted_dataset_type": definition.label,
        "confidence_score": int(confidence_score),
        "confidence": int(confidence_score),
        "evidence_columns": evidence,
        "evidence": evidence,
        "counter_evidence": counter_evidence,
        "uncertainty_reason": uncertainty_reason,
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
    price_columns = _financial_price_columns(df, date_columns)
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


def _financial_price_columns(df: pd.DataFrame, date_columns: list[str]) -> list[str]:
    columns: list[str] = []
    for column in df.columns:
        column_name = str(column)
        if _is_financial_price_column(column_name, df[column]):
            columns.append(column_name)
    if columns or not date_columns:
        return columns

    date_prefixes = {
        prefix for column in date_columns
        if (prefix := _ticker_prefix(str(column)))
    }
    if not date_prefixes:
        return columns
    for column in df.columns:
        column_name = str(column)
        if column_name in date_columns:
            continue
        if _ticker_prefix(column_name) not in date_prefixes:
            continue
        numeric_values = pd.to_numeric(df[column], errors="coerce").dropna()
        if len(numeric_values) < 6:
            continue
        if float(numeric_values.nunique(dropna=True) / max(1, len(numeric_values))) < 0.2:
            continue
        columns.append(column_name)
    return columns


def _ticker_prefix(column_name: str) -> str | None:
    match = re.fullmatch(r"([A-Z]{1,5})(?:[\._ -][A-Za-z]{1,12})?", column_name.strip())
    return match.group(1) if match else None


def _is_financial_price_column(column_name: str, series: pd.Series | None = None) -> bool:
    normalized = _normalize_name(column_name)
    if normalized in {"source_row_number", "row_number", "benchmark_score", "score", "score_pct", "max_score"}:
        return False
    if any(context in normalized for context in NON_FINANCIAL_PRICE_CONTEXT):
        return False
    if normalized in FINANCIAL_PRICE_NAMES or normalized.endswith("_close") or normalized.endswith("_price"):
        return True
    original = column_name.strip()
    ticker_like = bool(re.fullmatch(r"[A-Z]{1,5}", original)) or bool(
        re.fullmatch(r"[A-Z]{1,5}[\._ -]?(close|price|open|high|low|adjclose|adjustedclose)", original, flags=re.IGNORECASE)
    )
    if not ticker_like:
        return False
    if series is None:
        return True
    numeric_values = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric_values) < 6:
        return False
    if float(numeric_values.nunique(dropna=True) / max(1, len(numeric_values))) < 0.2:
        return False
    return True


def _not_suitable_reasons(
    *,
    df: pd.DataFrame,
    primary_domain_key: str,
    financial_eligibility: dict[str, Any],
    target_recommendations: list[dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    header_issue = _detect_header_issue([str(column) for column in df.columns])
    if header_issue["suspected"]:
        reasons.append("欄位名稱疑似不是正式表頭，可能是資料第一列被誤讀為欄位名稱；請先確認或補上表頭。")
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
    target_candidates = TargetAdvisor().recommend(df)
    id_like = [column for column in df.columns if _is_id_like_column_name(str(column), df[column])]
    if "submission" in normalized_file or (
        len(df.columns) <= 3
        and bool(id_like)
        and any(_looks_like_leakage_or_prediction_column(str(column)) for column in df.columns)
    ):
        role_key = "submission_format"
        role = "提交格式表"
    elif any(token in normalized_file for token in ("test", "predict", "unlabeled")) and not target_candidates:
        role_key = "unlabeled_prediction_dataset"
        role = "未標籤預測資料"
    elif any(token in normalized_file for token in ("train", "training")) and target_candidates:
        role_key = "training_dataset"
        role = "訓練資料"
    elif len(df.columns) <= 4 and bool(id_like):
        role_key = "lookup_table"
        role = "對照表或查找表"
    elif any(token in text for token in ("transaction", "order", "invoice", "event", "交易", "訂單")):
        role_key = "transaction_table"
        role = "交易或事件表"
    elif bool(id_like) and df.shape[1] >= 4:
        role_key = "dimension_table"
        role = "維度或主檔資料表"
    elif target_candidates:
        role_key = "standalone_dataset"
        role = "可獨立分析資料"
    else:
        role_key = "unknown"
        role = "待確認資料表"
    return {"file_name": file_name, "role": role, "role_key": role_key}


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
            "key": "relational_analysis",
            "label": "多表關聯分析",
            "description": "適合主題不同但共享模型、公司或日期等實體的資料。",
            "enabled": True,
        },
        {
            "key": "keep_separate",
            "label": "保持分表分析",
            "description": "適合關聯不明或需要先分別理解每張表的資料。",
            "enabled": True,
        },
        {
            "key": "ask_user_to_confirm",
            "label": "要求使用者確認",
            "description": "低信心或角色不明時，不自動合併或建模。",
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
