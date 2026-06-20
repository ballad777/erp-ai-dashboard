from __future__ import annotations

from typing import Any

from app.services.metric_glossary import (
    build_metric_interpretation as _glossary_metric_interpretation,
    get_metric_terms,
)


def build_dataset_brief(dataset_summary: dict[str, Any]) -> dict[str, Any]:
    """Build the shared readable layer for dataset pages and downstream tools."""

    quality_report = _as_dict(dataset_summary.get("quality_report"))
    quality_score = int(quality_report.get("quality_score") or 0)
    quality_issues = _as_list(quality_report.get("issues"))
    row_count = int(dataset_summary.get("row_count") or 0)
    column_count = int(dataset_summary.get("column_count") or 0)
    columns = [str(column) for column in _as_list(dataset_summary.get("columns"))]
    numeric_columns = list(_as_dict(dataset_summary.get("numeric_summary")).keys())
    date_candidates = _as_list(quality_report.get("date_frequency"))
    target_recommendations = [_as_dict(item) for item in _as_list(dataset_summary.get("target_recommendations"))]
    recommended_targets = [
        str(item.get("column"))
        for item in target_recommendations
        if item.get("column")
    ] or [str(column) for column in _as_list(dataset_summary.get("recommended_target_columns"))]
    dataset_type = _as_dict(dataset_summary.get("dataset_type"))
    dataset_story = _as_dict(dataset_summary.get("dataset_story"))
    dataset_kind = str(dataset_type.get("label") or _infer_dataset_kind(columns, numeric_columns, date_candidates))
    missing = _as_dict(quality_report.get("missing"))
    missing_columns = _as_list(missing.get("columns"))
    completeness = _dataset_completeness(row_count, column_count, int(missing.get("total_cells") or 0))

    if recommended_targets:
        target_sentence = f"系統初步建議可從「{recommended_targets[0]}」開始作為目標欄位。"
    else:
        target_sentence = "系統尚未偵測到明確目標欄位，仍可在模型頁手動選擇。"

    headline = str(dataset_story.get("one_sentence") or "") or (
        f"這份資料看起來偏向「{dataset_kind}」，共有 {row_count:,} 筆與 {column_count:,} 欄；"
        f"{target_sentence}"
    )

    suitable_tasks = _dataset_suitable_tasks(
        numeric_count=len(numeric_columns),
        has_date=bool(date_candidates),
        recommended_targets=recommended_targets,
        dataset_kind=dataset_kind,
    )
    risk = _dataset_primary_risk(quality_score, quality_issues, missing_columns)

    return {
        "plain_summary": {
            "headline": headline,
            "what_happened": str(dataset_story.get("what_is_this") or f"系統已完成欄位型態、缺失值、數值摘要與資料品質檢查，並偵測到 {len(numeric_columns)} 個數值欄位。"),
            "why_it_matters": _story_list_sentence(dataset_story.get("can_answer"), fallback=f"這份資料可優先用來做：{'、'.join(suitable_tasks)}。"),
            "risk": _story_list_sentence(dataset_story.get("cannot_answer"), prefix="目前不適合直接回答：", fallback=risk),
            "next_action": _dataset_next_action(recommended_targets, dataset_kind),
        },
        "confidence": {
            "level": _confidence_level_from_quality(quality_score, len(quality_issues)),
            "reason": _quality_summary(quality_score, quality_issues),
            "blocking_issues": [str(_as_dict(issue).get("message") or issue) for issue in quality_issues[:5]],
        },
        "evidence": [
            {
                "label": "資料規模",
                "value": f"{row_count:,} 筆 × {column_count:,} 欄",
                "source": "資料摘要",
            },
            {
                "label": "資料完整度",
                "value": f"{completeness * 100:.1f}%",
                "source": "缺失值統計",
            },
            {
                "label": "可用分析",
                "value": "、".join(suitable_tasks),
                "source": "欄位型態與日期欄位偵測",
            },
            {
                "label": "資料類型",
                "value": dataset_kind,
                "source": "DataUnderstandingEngine",
            },
        ],
        "terms": get_metric_terms(["data_completeness", "missing_values", "mean", "median", "std"]),
        "research_details": {
            "method": "pandas profile + rule-based schema detection",
            "assumptions": [
                "欄位名稱與資料型態可用於初步推測欄位角色。",
                "缺失值、重複列與 IQR 極端值可作為資料品質風險的第一層檢查。",
            ],
            "parameters": {
                "supported_formats": ["csv", "xlsx", "xls", "json"],
                "outlier_method": "IQR 1.5x",
                "target_candidate_limit": 5,
            },
            "limitations": [
                "欄位角色仍需使用者依業務定義確認。",
                "資料摘要不代表因果分析或正式模型驗證。",
            ],
            "artifacts": [
                "dataset_hash",
                "schema_fingerprint",
                "quality_report",
            ],
        },
    }


class ModelNarrator:
    def summarize(
        self,
        *,
        dataset_summary: dict[str, Any],
        model_analysis: dict[str, Any],
        best_model: dict[str, Any],
        baseline_model: dict[str, Any] | None,
        confidence: dict[str, Any],
        performance: str,
        next_action: str,
    ) -> dict[str, str]:
        dataset_key = str(_as_dict(dataset_summary.get("dataset_type")).get("key") or "")
        problem_type = str(model_analysis.get("problem_type") or "regression")
        target_column = str(model_analysis.get("target_column") or "")
        best_name = str(best_model.get("model_name") or "尚未產生")
        return {
            "headline": f"系統判定這是「{_problem_type_label(problem_type)}」任務，目前最佳模型是「{best_name}」。",
            "what_happened": performance,
            "why_it_matters": "模型比較只能說明目前資料與目標欄位之間是否存在可學習訊號；若證據不足，結果只能作為探索參考。",
            "risk": str(confidence.get("reason") or "仍需確認資料品質與目標欄位定義。"),
            "next_action": next_action,
        }


def build_model_brief(
    *,
    dataset_summary: dict[str, Any],
    model_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Build readable and research layers for model results."""

    ranked_models = _rank_model_results(model_analysis)
    best_model = ranked_models[0] if ranked_models else {}
    baseline_model = _find_baseline_model(model_analysis)
    problem_type = str(model_analysis.get("problem_type") or "regression")
    target_column = str(model_analysis.get("target_column") or "")
    quality_report = _as_dict(dataset_summary.get("quality_report"))
    quality_score = int(quality_report.get("quality_score") or 0)
    quality_issues = _as_list(quality_report.get("issues"))
    confidence = _model_confidence(problem_type, best_model, baseline_model, quality_score, quality_issues)
    performance = _performance_summary(problem_type, best_model, baseline_model)
    next_action = _next_action(
        quality_score=quality_score,
        issue_count=len(quality_issues),
        problem_type=problem_type,
        best_model=best_model,
        financial_analysis=None,
    )
    chart_stories = [
        build_chart_story(
            chart,
            {
                "dataset_summary": dataset_summary,
                "model_analysis": model_analysis,
                "best_model": best_model,
                "baseline_model": baseline_model,
                "financial_analysis": None,
            },
        )
        for chart in _as_list(model_analysis.get("charts"))
    ]

    metric_terms = ["rmse", "mae", "r2", "feature_importance", "residual"]
    if problem_type == "classification":
        metric_terms = ["accuracy", "f1_score", "rmse", "mae", "feature_importance"]
    plain_summary = ModelNarrator().summarize(
        dataset_summary=dataset_summary,
        model_analysis=model_analysis,
        best_model=best_model,
        baseline_model=baseline_model,
        confidence=confidence,
        performance=performance,
        next_action=next_action,
    )

    return {
        "plain_summary": plain_summary,
        "confidence": confidence,
        "evidence": [
            {
                "label": "最佳模型",
                "value": str(best_model.get("model_name") or "尚未產生"),
                "source": "模型比較",
            },
            {
                "label": "最佳模型指標",
                "value": _metric_evidence(problem_type, best_model),
                "source": "測試資料評估",
            },
            {
                "label": "Baseline 對照",
                "value": _model_evaluation_summary(problem_type, baseline_model),
                "source": "Dummy baseline",
            },
        ],
        "terms": get_metric_terms(metric_terms),
        "chart_stories": chart_stories,
        "model_guidance": _build_model_guidance(
            dataset_summary=dataset_summary,
            model_analysis=model_analysis,
            ranked_models=ranked_models,
            baseline_model=baseline_model,
        ),
        "research_details": {
            "method": "scikit-learn Pipeline + train/test split + baseline comparison",
            "assumptions": [
                "目前以一次固定 random seed 的 train/test split 作為初步驗證。",
                "模型比較排名依任務類型選擇 RMSE 或分類分數。",
            ],
            "parameters": {
                "target_column": target_column,
                "problem_type": problem_type,
                "train_test_split": "75/25",
                "random_seed": 42,
                "automl_mode": model_analysis.get("automl_mode"),
                "selected_model_keys": _as_list(model_analysis.get("selected_model_keys")),
                "selected_chart_types": _as_list(model_analysis.get("selected_chart_types")),
            },
            "limitations": _risk_limitations(
                dataset_summary=dataset_summary,
                model_analysis=model_analysis,
                quality_issues=quality_issues,
                financial_analysis=None,
            ),
            "artifacts": [
                model_analysis.get("model_results_path"),
                model_analysis.get("cleaned_dataset_path"),
                *[chart.get("chart_path") for chart in _as_list(model_analysis.get("charts")) if isinstance(chart, dict)],
            ],
        },
    }


def build_financial_brief(
    *,
    financial_analysis: dict[str, Any],
    dataset_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build readable and research layers for financial/time-series results."""

    reliability = build_forecast_reliability(financial_analysis)
    trend_label = str(financial_analysis.get("trend_label") or "尚未判斷")
    latest_return = _safe_float(financial_analysis.get("latest_return"))
    volatility = _safe_float(financial_analysis.get("latest_volatility"))
    rsi = _safe_float(financial_analysis.get("latest_rsi"))
    var_95 = _safe_float(financial_analysis.get("var_95"))
    risk_parts = [
        build_metric_interpretation("volatility", volatility)["this_result_means"],
        build_metric_interpretation("rsi", rsi)["this_result_means"],
        build_metric_interpretation("var", var_95)["this_result_means"],
    ]
    chart_stories = [
        build_chart_story(
            chart,
            {
                "dataset_summary": dataset_summary or {},
                "model_analysis": {},
                "best_model": {},
                "baseline_model": None,
                "financial_analysis": financial_analysis,
            },
        )
        for chart in _as_list(financial_analysis.get("charts"))
    ]

    return {
        "plain_summary": {
            "headline": f"目前時間序列訊號為「{trend_label}」，預測可信度為「{_confidence_label(reliability['level'])}」。",
            "what_happened": f"系統已使用「{financial_analysis.get('date_column')}」與「{financial_analysis.get('price_column')}」完成趨勢、報酬率、波動率、RSI、MACD 與 VaR 分析。",
            "why_it_matters": "這些指標可協助判斷目前趨勢、短期風險與是否需要更保守地解讀預測。",
            "risk": "；".join(risk_parts),
            "next_action": reliability["recommended_action"],
        },
        "confidence": {
            "level": reliability["level"],
            "reason": reliability["reason"],
            "blocking_issues": [reliability["reason"]] if reliability["should_show_warning"] else [],
        },
        "forecast_reliability": reliability,
        "evidence": [
            {
                "label": "最新報酬率",
                "value": _format_optional_number(latest_return),
                "source": "金融指標",
            },
            {
                "label": "RSI",
                "value": _format_optional_number(rsi),
                "source": "技術指標",
            },
            {
                "label": "VaR 95%",
                "value": _format_optional_number(var_95),
                "source": "歷史風險估計",
            },
            {
                "label": "預測可信度",
                "value": _confidence_label(reliability["level"]),
                "source": "預測防護檢查",
            },
        ],
        "terms": [
            build_metric_interpretation("return", latest_return),
            build_metric_interpretation("volatility", volatility),
            *get_metric_terms(["moving_average"]),
            build_metric_interpretation("rsi", rsi),
            build_metric_interpretation("macd", financial_analysis.get("latest_macd")),
            build_metric_interpretation("var", var_95),
            build_metric_interpretation("forecast", reliability.get("forecast_label")),
        ],
        "chart_stories": chart_stories,
        "research_details": {
            "method": "rolling indicators + historical VaR + linear baseline forecast",
            "assumptions": [
                "目前預測使用簡化線性趨勢模型，只能作為基準情境估計。",
                "VaR 使用歷史報酬分位數估計，不包含外部事件。",
            ],
            "parameters": {
                "date_column": financial_analysis.get("date_column"),
                "value_column": financial_analysis.get("price_column"),
                "row_count_used": financial_analysis.get("row_count_used"),
                "forecast_periods": len(_as_list(financial_analysis.get("forecast_points"))),
            },
            "limitations": [
                "金融與時間序列結果不構成投資建議。",
                "沒有回測前，不應把預測點當成確定結果。",
                "短期技術指標需搭配外部市場或業務背景解讀。",
            ],
            "artifacts": [
                financial_analysis.get("indicator_path"),
                *[chart.get("chart_path") for chart in _as_list(financial_analysis.get("charts")) if isinstance(chart, dict)],
            ],
        },
    }


class ChartStoryEngine:
    def build(self, chart: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, str]:
        context = context or {}
        model_analysis = _as_dict(context.get("model_analysis"))
        financial_analysis = _as_dict(context.get("financial_analysis")) or None
        best_model = _as_dict(context.get("best_model"))
        baseline_model = _as_dict(context.get("baseline_model")) or None
        dataset_summary = _as_dict(context.get("dataset_summary"))
        outliers = _as_list(_as_dict(dataset_summary.get("quality_report")).get("outliers"))
        chart_type = str(chart.get("chart_type") or "chart")
        title = str(chart.get("title") or _chart_title(chart_type))
        return {
            "chart_type": chart_type,
            "title": title,
            "chart_path": str(chart.get("chart_path") or ""),
            "chart_url": str(chart.get("chart_url") or ""),
            "explanation": _chart_explanation(chart_type, title),
            "key_findings": _chart_key_findings(
                chart_type=chart_type,
                model_analysis=model_analysis,
                best_model=best_model,
                baseline_model=baseline_model,
                financial_analysis=financial_analysis,
            ),
            "meaning": _chart_meaning(chart_type, model_analysis, financial_analysis),
            "what_it_cannot_prove": _chart_cannot_prove(chart_type),
            "trend_interpretation": _chart_trend_interpretation(chart_type, model_analysis, financial_analysis),
            "anomaly_note": _chart_anomaly_note(chart_type, outliers),
            "business_insight": _chart_business_insight(chart_type, model_analysis, financial_analysis),
            "recommended_action": _chart_recommended_action(chart_type),
        }


def build_chart_story(chart: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, str]:
    return ChartStoryEngine().build(chart, context)


def build_metric_interpretation(
    metric: str,
    value: Any,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _glossary_metric_interpretation(metric, value, context=context)


def build_forecast_reliability(financial_analysis: dict[str, Any]) -> dict[str, Any]:
    latest = _safe_float(financial_analysis.get("latest_price"))
    points = _as_list(financial_analysis.get("forecast_points"))
    predicted_values = [
        _safe_float(_as_dict(point).get("predicted_price"))
        for point in points
        if _safe_float(_as_dict(point).get("predicted_price")) is not None
    ]
    row_count = int(financial_analysis.get("row_count_used") or 0)

    if latest is None or latest == 0 or not predicted_values:
        return {
            "level": "low",
            "reason": "缺少可比較的最新值或預測點，因此不能可靠解讀預測。",
            "recommended_action": "先確認日期與價格/指數/數值欄位是否正確，再重新執行分析。",
            "should_show_warning": True,
            "max_deviation_ratio": None,
            "forecast_label": "基準情境估計",
        }

    max_deviation = max(abs(value - latest) / abs(latest) for value in predicted_values if value is not None)
    if max_deviation > 0.2:
        level = "low"
        reason = "預測值與最新值落差超過 20%，且目前使用簡化線性趨勢模型。"
    elif max_deviation > 0.08 or row_count < 30:
        level = "medium"
        reason = "預測值與最新值有明顯落差，或資料期間偏短；目前只能作為情境參考。"
    else:
        level = "medium"
        reason = "預測與最新值落差不大，但目前仍是線性基準模型，未完成回測前不能視為高可信預測。"

    if row_count > 365 * 10 and level != "low":
        level = "medium"
        reason += " 資料跨越較長期間，若趨勢非線性，建議改用近年視窗並加入回測。"

    return {
        "level": level,
        "reason": reason,
        "recommended_action": "把預測視為基準情境估計；若要用於決策，請改用近 1 年或近 5 年資料視窗並加入回測誤差。",
        "should_show_warning": True,
        "max_deviation_ratio": round(max_deviation, 6),
        "forecast_label": "基準情境估計",
    }


def build_decision_brief(
    *,
    dataset_summary: dict[str, Any],
    model_analysis: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
) -> dict[str, Any]:
    """Translate technical analysis outputs into decision-ready language."""

    ranked_models = _rank_model_results(model_analysis)
    best_model = ranked_models[0] if ranked_models else {}
    baseline_model = _find_baseline_model(model_analysis)
    quality_report = _as_dict(dataset_summary.get("quality_report"))
    quality_score = int(quality_report.get("quality_score") or 0)
    quality_issues = _as_list(quality_report.get("issues"))
    problem_type = str(model_analysis.get("problem_type") or "regression")
    target_column = str(model_analysis.get("target_column") or "")
    row_count = int(dataset_summary.get("row_count") or model_analysis.get("row_count_used") or 0)
    column_count = int(dataset_summary.get("column_count") or 0)
    performance_summary = _performance_summary(problem_type, best_model, baseline_model)
    next_action = _next_action(
        quality_score=quality_score,
        issue_count=len(quality_issues),
        problem_type=problem_type,
        best_model=best_model,
        financial_analysis=financial_analysis,
    )

    executive_summary = [
        f"本次分析共讀取 {row_count:,} 筆資料與 {column_count:,} 個欄位，系統判定主要任務是「{_problem_type_label(problem_type)}」，目標欄位為「{target_column}」。",
        performance_summary,
        _quality_summary(quality_score, quality_issues),
        _financial_summary(financial_analysis),
        f"建議下一步：{next_action}",
    ]

    priority_findings = _build_priority_findings(
        dataset_summary=dataset_summary,
        model_analysis=model_analysis,
        financial_analysis=financial_analysis,
        best_model=best_model,
        baseline_model=baseline_model,
        quality_score=quality_score,
        quality_issues=quality_issues,
        next_action=next_action,
    )

    chart_interpretations = _build_chart_interpretations(
        dataset_summary=dataset_summary,
        model_analysis=model_analysis,
        financial_analysis=financial_analysis,
        best_model=best_model,
        baseline_model=baseline_model,
    )

    model_guidance = _build_model_guidance(
        dataset_summary=dataset_summary,
        model_analysis=model_analysis,
        ranked_models=ranked_models,
        baseline_model=baseline_model,
    )

    report_sections = _build_report_sections(
        dataset_summary=dataset_summary,
        model_analysis=model_analysis,
        financial_analysis=financial_analysis,
        best_model=best_model,
        quality_score=quality_score,
        quality_issues=quality_issues,
        chart_interpretations=chart_interpretations,
        next_action=next_action,
    )

    return {
        "summary_title": "把分析結果翻譯成下一步",
        "plain_language_summary": {
            "what_happened": executive_summary[0],
            "why_it_matters": executive_summary[1],
            "risks": _risk_sentence(quality_score, quality_issues, financial_analysis),
            "opportunities": _opportunity_sentence(model_analysis, financial_analysis),
            "next_step": next_action,
        },
        "executive_summary": executive_summary,
        "priority_findings": priority_findings,
        "model_guidance": model_guidance,
        "chart_interpretations": chart_interpretations,
        "report_sections": report_sections,
        "risk_and_limitations": _risk_limitations(
            dataset_summary=dataset_summary,
            model_analysis=model_analysis,
            quality_issues=quality_issues,
            financial_analysis=financial_analysis,
        ),
        "ai_conclusion": _ai_conclusion(best_model, quality_score, next_action),
    }


def enrich_model_option(option: dict[str, Any]) -> dict[str, Any]:
    key = str(option.get("key") or "")
    family = str(option.get("family") or "")
    problem_type = str(option.get("problem_type") or "")
    complexity = str(option.get("complexity") or "medium")
    guide = _model_static_guide(key=key, family=family, problem_type=problem_type)
    return {
        **option,
        "purpose": guide["purpose"],
        "suitable_data_types": guide["suitable_data_types"],
        "difficulty_label": _difficulty_label(complexity),
        "use_cases": guide["use_cases"],
    }


def _build_priority_findings(
    *,
    dataset_summary: dict[str, Any],
    model_analysis: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
    best_model: dict[str, Any],
    baseline_model: dict[str, Any] | None,
    quality_score: int,
    quality_issues: list[Any],
    next_action: str,
) -> list[dict[str, str]]:
    problem_type = str(model_analysis.get("problem_type") or "regression")
    findings = [
        {
            "level": "most_important",
            "label": "最重要發現",
            "title": f"最佳模型目前是「{best_model.get('model_name', '尚未產生')}」",
            "summary": _performance_summary(problem_type, best_model, baseline_model),
            "evidence": _metric_evidence(problem_type, best_model),
            "recommended_action": "先用這個模型作為目前分析基準，再檢查資料品質與關鍵欄位是否合理。",
        },
        {
            "level": "attention",
            "label": "需要注意",
            "title": f"資料品質分數為 {quality_score}/100",
            "summary": _quality_summary(quality_score, quality_issues),
            "evidence": _quality_evidence(dataset_summary),
            "recommended_action": "在正式決策前，優先處理缺失值、重複資料、極端值與可能造成洩漏的欄位。",
        },
        {
            "level": "action",
            "label": "建議行動",
            "title": "下一步不是看更多圖，而是驗證最關鍵的假設",
            "summary": next_action,
            "evidence": "此建議由資料品質、模型表現、金融訊號與已產出圖表共同推導。",
            "recommended_action": next_action,
        },
    ]

    if financial_analysis:
        findings.insert(
            2,
            {
                "level": "risk" if "下行" in str(financial_analysis.get("trend_label")) else "opportunity",
                "label": "金融訊號",
                "title": f"價格或時間序列訊號：{financial_analysis.get('trend_label')}",
                "summary": _financial_summary(financial_analysis),
                "evidence": f"VaR 95%：{_format_optional_number(financial_analysis.get('var_95'))}；最新波動率：{_format_optional_number(financial_analysis.get('latest_volatility'))}",
                "recommended_action": "若這是金融或時間序列資料，請搭配外部市場事件與更長期間資料再確認趨勢。",
            },
        )
    else:
        findings.insert(
            2,
            {
                "level": "opportunity",
                "label": "成長機會",
                "title": "目前重點可放在模型解釋與欄位驗證",
                "summary": "資料未啟用金融時間序列分析，因此應先理解哪些欄位最能解釋目標欄位。",
                "evidence": f"系統已產生 {len(_as_list(model_analysis.get('charts')))} 張模型圖表。",
                "recommended_action": "優先查看特徵重要性與預測誤差，找出最值得追蹤或改善的欄位。",
            },
        )

    return findings


def _build_chart_interpretations(
    *,
    dataset_summary: dict[str, Any],
    model_analysis: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
    best_model: dict[str, Any],
    baseline_model: dict[str, Any] | None,
) -> list[dict[str, str]]:
    charts: list[dict[str, Any]] = []
    charts.extend(_as_list(model_analysis.get("charts")))
    if financial_analysis:
        charts.extend(_as_list(financial_analysis.get("charts")))

    interpretations: list[dict[str, str]] = []
    for chart in charts:
        interpretations.append(
            build_chart_story(
                chart,
                {
                    "dataset_summary": dataset_summary,
                    "model_analysis": model_analysis,
                    "best_model": best_model,
                    "baseline_model": baseline_model,
                    "financial_analysis": financial_analysis,
                },
            )
        )
    return interpretations


def _build_model_guidance(
    *,
    dataset_summary: dict[str, Any],
    model_analysis: dict[str, Any],
    ranked_models: list[dict[str, Any]],
    baseline_model: dict[str, Any] | None,
) -> dict[str, Any]:
    problem_type = str(model_analysis.get("problem_type") or "regression")
    recommended_models = [_as_dict(model) for model in _as_list(model_analysis.get("recommended_models"))]
    trained_by_key = {str(model.get("model_key")): model for model in ranked_models}
    rows = int(model_analysis.get("row_count_used") or dataset_summary.get("row_count") or 0)
    features = int(model_analysis.get("feature_count_used") or 0)
    quality_report = _as_dict(dataset_summary.get("quality_report"))
    missing_columns = _as_list(_as_dict(quality_report.get("missing")).get("columns"))

    cards: list[dict[str, Any]] = []
    for option in recommended_models[:6]:
        enriched = enrich_model_option(option)
        trained = trained_by_key.get(str(enriched.get("key")))
        cards.append(
            {
                "model_key": enriched.get("key"),
                "model_name": enriched.get("label"),
                "purpose": enriched.get("purpose"),
                "suitable_data_types": enriched.get("suitable_data_types"),
                "difficulty": enriched.get("difficulty_label"),
                "use_cases": enriched.get("use_cases"),
                "why_recommended": _recommendation_reason(
                    model=enriched,
                    rows=rows,
                    features=features,
                    missing_column_count=len(missing_columns),
                    problem_type=problem_type,
                ),
                "expected_output": _expected_output(problem_type, str(model_analysis.get("target_column") or "")),
                "recommendation_score": _recommendation_score(enriched, rows, features, len(missing_columns)),
                "evaluation_summary": _model_evaluation_summary(problem_type, trained),
            }
        )

    return {
        "problem_type": problem_type,
        "problem_type_label": _problem_type_label(problem_type),
        "target_column": str(model_analysis.get("target_column") or ""),
        "selection_logic": "系統依資料量、欄位數、缺失比例、欄位型態與目標欄位型態推薦模型，而不是固定每次套用同一組模型。",
        "baseline_summary": _model_evaluation_summary(problem_type, baseline_model),
        "recommended_models": cards,
        "best_model_summary": _model_evaluation_summary(problem_type, ranked_models[0] if ranked_models else None),
    }


def _build_report_sections(
    *,
    dataset_summary: dict[str, Any],
    model_analysis: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
    best_model: dict[str, Any],
    quality_score: int,
    quality_issues: list[Any],
    chart_interpretations: list[dict[str, str]],
    next_action: str,
) -> list[dict[str, str]]:
    problem_type = str(model_analysis.get("problem_type") or "regression")
    target_column = str(model_analysis.get("target_column") or "")
    dataset_type = str(_as_dict(dataset_summary.get("dataset_type")).get("label") or "資料集")
    dataset_story = _as_dict(dataset_summary.get("dataset_story"))
    best_model_name = str(best_model.get("model_name") or "最佳模型")
    performance = _performance_summary(problem_type, best_model, _find_baseline_model(model_analysis))
    story_can_answer = _story_list_sentence(dataset_story.get("can_answer"), fallback="這份資料可用於資料探索、模型比較與圖表解讀。")
    story_cannot_answer = _story_list_sentence(dataset_story.get("cannot_answer"), prefix="不建議直接用來判斷：", fallback=_risk_sentence(quality_score, quality_issues, financial_analysis))
    return [
        {
            "title": "執行摘要",
            "analysis_purpose": "讓決策者先在 10 秒內理解本次分析的核心結論。",
            "analysis_method": "整合資料理解、品質檢查、模型比較與圖表故事，濃縮成可行動摘要。",
            "analysis_result": f"本次資料為「{dataset_type}」，目標欄位為「{target_column or '尚未指定'}」；{performance}",
            "interpretation": dataset_story.get("one_sentence") or "這份資料已被轉換成可閱讀的分析摘要。",
            "business_meaning": "先知道重點，才能決定要補資料、換模型、產出報告或採取行動。",
            "recommended_action": next_action,
            "risks_and_limits": _risk_sentence(quality_score, quality_issues, financial_analysis),
            "ai_conclusion": _ai_conclusion(best_model, quality_score, next_action),
        },
        {
            "title": "資料介紹",
            "analysis_purpose": "說明這份資料代表什麼，避免把資料誤解成錯誤情境。",
            "analysis_method": "DataUnderstandingEngine 依欄位名稱、資料型態、日期欄位、數值欄位與檔名語意判斷資料主題。",
            "analysis_result": dataset_story.get("what_is_this") or f"資料共有 {int(dataset_summary.get('row_count') or 0):,} 筆、{int(dataset_summary.get('column_count') or 0):,} 欄。",
            "interpretation": story_can_answer,
            "business_meaning": "資料主題判斷會影響模型、圖表與報告語氣；主題錯誤會導致整份報告失真。",
            "recommended_action": "先確認資料類型與業務理解一致，再進入模型訓練。",
            "risks_and_limits": story_cannot_answer,
            "ai_conclusion": f"目前系統將資料定位為「{dataset_type}」。",
        },
        {
            "title": "資料品質",
            "analysis_purpose": "判斷目前資料是否足以支撐模型與決策。",
            "analysis_method": "檢查缺失值、重複列、極端值、疑似洩漏欄位與整體品質分數。",
            "analysis_result": _quality_summary(quality_score, quality_issues),
            "interpretation": "品質分數不是裝飾數字，而是提醒哪些結果可以相信、哪些需要先補資料。",
            "business_meaning": "品質風險越高，模型分數越容易看起來漂亮但沒有決策價值。",
            "recommended_action": "先修正資料品質問題，再使用模型結果做正式判斷。",
            "risks_and_limits": "資料品質檢查只能指出可疑點，仍需人工確認欄位定義與資料來源。",
            "ai_conclusion": f"目前資料品質分數為 {quality_score}/100。",
        },
        {
            "title": "分析目標",
            "analysis_purpose": f"確認本次是否要解釋或預測「{target_column}」。",
            "analysis_method": "TargetRecommendationEngine 依欄位語意、型態、唯一值比例與資料主題推薦候選目標。",
            "analysis_result": f"目前任務為「{_problem_type_label(problem_type)}」，目標欄位為「{target_column or '尚未指定'}」。",
            "interpretation": "目標欄位代表使用者真正想回答的問題；若目標選錯，模型分數再高也沒有意義。",
            "business_meaning": "好的目標欄位會讓圖表、模型與報告都指向同一個決策問題。",
            "recommended_action": next_action,
            "risks_and_limits": "自動推薦不是替使用者決定；正式分析前仍需確認欄位是否符合業務問題。",
            "ai_conclusion": f"建議先以「{target_column or '系統推薦目標'}」作為本次分析主軸。",
        },
        {
            "title": "分析方法",
            "analysis_purpose": "說明系統如何從原始資料走到模型結果。",
            "analysis_method": "建立前處理流程、缺失值填補、類別編碼、train/test split、baseline 對照與候選模型比較。",
            "analysis_result": f"本次使用 {_problem_type_label(problem_type)} 流程，並以測試資料評估候選模型。",
            "interpretation": "有 baseline 對照才能確認模型是否真的學到訊號，而不是只產生一個看起來專業的分數。",
            "business_meaning": "方法透明會讓結果可追溯，也方便使用者修正目標欄位或模型設定。",
            "recommended_action": "若結果用於高風險決策，請再加入交叉驗證或獨立驗證集。",
            "risks_and_limits": "目前仍是表格機器學習流程，不等同因果推論或正式審計。",
            "ai_conclusion": "本次方法可用於探索與初步決策，不應被當成最終真相。",
        },
        {
            "title": "最佳模型",
            "analysis_purpose": f"找出目前最適合處理「{target_column}」的模型。",
            "analysis_method": "依任務型態排序候選模型，並與 baseline 比較。",
            "analysis_result": performance,
            "interpretation": _model_result_interpretation(problem_type, best_model),
            "business_meaning": "最佳模型提供目前最可靠的預測基準，但仍需要檢查是否發生資料洩漏。",
            "recommended_action": f"先以「{best_model_name}」作為基準，再檢查錯誤樣本與重要特徵。",
            "risks_and_limits": "單次切分可能高估或低估表現；資料量小時尤其需要保守解讀。",
            "ai_conclusion": f"目前最佳模型為「{best_model_name}」。",
        },
        {
            "title": "模型解讀",
            "analysis_purpose": "把模型分數翻譯成一般人能理解的訊號。",
            "analysis_method": "結合指標、baseline 差距、特徵重要性與資料品質風險。",
            "analysis_result": _metric_evidence(problem_type, best_model),
            "interpretation": "分數越高或誤差越低，代表模型越能重現目前資料中的模式；但不代表未來一定相同。",
            "business_meaning": "模型可以協助排序、預測與找重點，但不能取代業務判斷。",
            "recommended_action": "確認模型依賴的前幾個欄位是否合理，若有 ID 或答案欄位需排除後重跑。",
            "risks_and_limits": "若指標異常接近 1，需優先檢查資料洩漏。",
            "ai_conclusion": "模型解讀的核心是確認分數背後是否有合理原因。",
        },
        {
            "title": "圖表解讀",
            "analysis_purpose": "用圖表支撐文字結論，而不是堆疊更多資料。",
            "analysis_method": "ChartStoryEngine 為每張圖建立說明、發現、意義、不能證明的事與下一步。",
            "analysis_result": f"本次共產生 {len(chart_interpretations)} 張可追溯圖表。",
            "interpretation": chart_interpretations[0].get("key_findings") if chart_interpretations else "目前尚未產生圖表。",
            "business_meaning": "圖表應該幫助使用者知道先看哪裡，而不是讓使用者自行解讀所有數據。",
            "recommended_action": "先查看模型比較與特徵重要性，再決定是否需要補資料或換模型。",
            "risks_and_limits": "圖表呈現的是目前資料內的模式，不能單獨證明因果或未來結果。",
            "ai_conclusion": "圖表的價值在於支撐下一步決策。",
        },
        {
            "title": "商業意義",
            "analysis_purpose": "把技術結果轉換成決策語言。",
            "analysis_method": "根據資料主題、模型表現與圖表故事推導可能的營運或研究含義。",
            "analysis_result": story_can_answer,
            "interpretation": "若資料主題與目標欄位明確，分析結果可直接對應到分類、預測、排序或風險確認。",
            "business_meaning": "使用者不需要懂模型細節，也應該能知道結果代表哪些機會、風險與下一步。",
            "recommended_action": next_action,
            "risks_and_limits": "商業意義需要結合真實脈絡；系統只能依目前資料提出可驗證方向。",
            "ai_conclusion": "本次分析提供的是可行動線索，不是取代決策者的結論。",
        },
        {
            "title": "風險分析",
            "analysis_purpose": "明確列出哪些結果不能過度解讀。",
            "analysis_method": "彙整資料品質、樣本量、模型分數、圖表限制與金融/非金融適用性。",
            "analysis_result": _risk_sentence(quality_score, quality_issues, financial_analysis),
            "interpretation": "風險不代表資料不能用，而是代表需要知道哪些假設會影響結論。",
            "business_meaning": "把風險說清楚，可以避免使用者因漂亮分數做出錯誤決策。",
            "recommended_action": "先處理最嚴重的資料品質與目標欄位風險。",
            "risks_and_limits": story_cannot_answer,
            "ai_conclusion": "目前結果應搭配風險提示一起閱讀。",
        },
        {
            "title": "建議行動",
            "analysis_purpose": "把分析轉成下一個可執行動作。",
            "analysis_method": "依資料品質、模型結果與圖表故事排序最值得先做的事。",
            "analysis_result": next_action,
            "interpretation": "下一步不一定是跑更多模型；更常見的是確認目標、修資料或檢查重要特徵。",
            "business_meaning": "清楚的下一步能降低分析門檻，讓非資料背景使用者也能行動。",
            "recommended_action": next_action,
            "risks_and_limits": "若業務目標改變，下一步也應重新產生。",
            "ai_conclusion": "目前最值得先做的是依建議行動驗證核心假設。",
        },
        {
            "title": "結論",
            "analysis_purpose": "收斂本次分析的主要訊息。",
            "analysis_method": "綜合資料理解、品質、模型、圖表與風險。",
            "analysis_result": _ai_conclusion(best_model, quality_score, next_action),
            "interpretation": "這份結論應作為下一輪分析或決策討論的起點。",
            "business_meaning": "好的分析不是提供更多數字，而是讓使用者知道接下來要做什麼。",
            "recommended_action": next_action,
            "risks_and_limits": "結論僅根據目前上傳資料，不包含外部資料與人工審核後的業務知識。",
            "ai_conclusion": _ai_conclusion(best_model, quality_score, next_action),
        },
    ]


def _rank_model_results(model_analysis: dict[str, Any]) -> list[dict[str, Any]]:
    results = [_as_dict(result) for result in _as_list(model_analysis.get("model_results"))]
    problem_type = str(model_analysis.get("problem_type") or "regression")
    if problem_type == "classification":
        return sorted(
            results,
            key=lambda result: (
                -float(result.get("accuracy") or 0),
                float(result.get("rmse") or 0),
            ),
        )
    return sorted(results, key=lambda result: float(result.get("rmse") or 0))


def _find_baseline_model(model_analysis: dict[str, Any]) -> dict[str, Any] | None:
    for result in _as_list(model_analysis.get("model_results")):
        item = _as_dict(result)
        if str(item.get("model_key", "")).startswith("baseline_"):
            return item
    return None


def _performance_summary(
    problem_type: str,
    best_model: dict[str, Any],
    baseline_model: dict[str, Any] | None,
) -> str:
    model_name = str(best_model.get("model_name") or "最佳模型")
    if problem_type == "classification":
        accuracy = best_model.get("accuracy")
        f1 = best_model.get("f1_score")
        base_accuracy = baseline_model.get("accuracy") if baseline_model else None
        lift = _relative_lift(accuracy, base_accuracy, higher_is_better=True)
        suffix = f"，相較 baseline 提升約 {lift:.1f}%" if lift is not None else ""
        return f"目前表現最佳的是「{model_name}」，Accuracy 為 {_format_optional_number(accuracy)}、F1-score 為 {_format_optional_number(f1)}{suffix}。"

    rmse = best_model.get("rmse")
    mae = best_model.get("mae")
    base_rmse = baseline_model.get("rmse") if baseline_model else None
    lift = _relative_lift(rmse, base_rmse, higher_is_better=False)
    suffix = f"，誤差相較 baseline 降低約 {lift:.1f}%" if lift is not None else ""
    return f"目前表現最佳的是「{model_name}」，RMSE 為 {_format_optional_number(rmse)}、MAE 為 {_format_optional_number(mae)}{suffix}。"


def _quality_summary(quality_score: int, quality_issues: list[Any]) -> str:
    issue_count = len(quality_issues)
    if quality_score >= 85 and issue_count == 0:
        return f"資料品質分數為 {quality_score}/100，目前沒有明顯資料品質警訊，可優先進入模型解讀。"
    if quality_score >= 70:
        return f"資料品質分數為 {quality_score}/100，已偵測到 {issue_count} 類需要確認的資料品質問題，建議在正式決策前逐一檢查。"
    return f"資料品質分數為 {quality_score}/100，資料風險偏高；建議先完成資料清理，再使用模型結果做決策。"


def _financial_summary(financial_analysis: dict[str, Any] | None) -> str:
    if not financial_analysis:
        return "本資料未啟用金融時間序列分析；目前重點應放在資料品質、模型表現與欄位解釋。"
    trend = financial_analysis.get("trend_label")
    var_95 = _format_optional_number(financial_analysis.get("var_95"))
    latest_return = _format_optional_number(financial_analysis.get("latest_return"))
    return f"金融分析訊號為「{trend}」，最新報酬率為 {latest_return}，VaR 95% 為 {var_95}；建議搭配外部市場脈絡解讀。"


def _next_action(
    *,
    quality_score: int,
    issue_count: int,
    problem_type: str,
    best_model: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
) -> str:
    if quality_score < 70 or issue_count >= 4:
        return "先修正資料品質問題，尤其是缺失值、重複列、極端值與可能造成目標洩漏的欄位。"
    if financial_analysis and financial_analysis.get("trend_label"):
        return "先確認金融訊號是否符合業務或市場脈絡，再用最佳模型做敏感度分析。"
    if problem_type == "classification":
        return f"以「{best_model.get('model_name', '最佳模型')}」建立初步分類規則，並檢查錯分樣本集中在哪些族群。"
    return f"以「{best_model.get('model_name', '最佳模型')}」作為預測基準，優先檢查特徵重要性與預測誤差最大的資料區段。"


def _quality_evidence(dataset_summary: dict[str, Any]) -> str:
    report = _as_dict(dataset_summary.get("quality_report"))
    missing = _as_dict(report.get("missing"))
    missing_total = int(missing.get("total_cells") or 0)
    duplicates = int(_as_dict(report.get("duplicate_rows")).get("count") or 0)
    outlier_count = len(_as_list(report.get("outliers")))
    leakage_count = len(_as_list(report.get("leakage_candidates")))
    return f"缺失儲存格 {missing_total:,} 個、重複列 {duplicates:,} 筆、極端值欄位 {outlier_count} 個、可能洩漏欄位 {leakage_count} 個。"


def _metric_evidence(problem_type: str, model: dict[str, Any]) -> str:
    if problem_type == "classification":
        return f"Accuracy：{_format_optional_number(model.get('accuracy'))}；F1-score：{_format_optional_number(model.get('f1_score'))}；訓練時間：{_format_optional_number(model.get('training_time_seconds'))} 秒。"
    return f"R2：{_format_optional_number(model.get('r2'))}；RMSE：{_format_optional_number(model.get('rmse'))}；MAE：{_format_optional_number(model.get('mae'))}；訓練時間：{_format_optional_number(model.get('training_time_seconds'))} 秒。"


def _chart_explanation(chart_type: str, title: str) -> str:
    explanations = {
        "model_comparison": "用測試資料誤差把候選模型排出順序，重點是看最佳模型是否真正勝過 baseline，而不是只看模型名稱。",
        "feature_importance": "把模型最依賴的欄位排出優先級，協助你判斷結果是由合理訊號支撐，還是被 ID、來源欄位或資料洩漏帶偏。",
        "predicted_vs_actual": "把預測值放回真實結果旁邊檢查，越接近理想線代表模型越能重現資料裡的規律。",
        "residual_plot": "把每筆資料的預測誤差攤開檢查，用來找出模型是否在特定區段或族群持續偏差。",
        "financial_indicators": "這張圖彙整價格、移動平均與技術指標，用來觀察趨勢與短期風險。",
        "financial_forecast": "這張圖呈現時間序列預測，用來快速理解接下來可能的價格方向。",
        "price_moving_average": "這張圖把價格/指數/數值與移動平均放在一起，用來看短期與中期趨勢是否一致。",
        "return_volatility": "這張圖同時呈現單期變化與波動率，用來判斷近期變動幅度是否需要注意。",
        "rsi_macd": "這張圖用 RSI 與 MACD 觀察短期強弱與動能變化。",
        "time_series_forecast": "這張圖呈現基準情境估計，用來看模型外推方向，但不是確定預測。",
    }
    return explanations.get(chart_type, f"這張「{title}」用來輔助理解目前分析結果。")


def _chart_key_findings(
    *,
    chart_type: str,
    model_analysis: dict[str, Any],
    best_model: dict[str, Any],
    baseline_model: dict[str, Any] | None,
    financial_analysis: dict[str, Any] | None,
) -> str:
    problem_type = str(model_analysis.get("problem_type") or "regression")
    if chart_type == "model_comparison":
        return _performance_summary(problem_type, best_model, baseline_model)
    if chart_type == "feature_importance":
        target = str(model_analysis.get("target_column") or "目標欄位")
        return f"系統已用「{best_model.get('model_name', '最佳模型')}」檢查哪些欄位最能解釋「{target}」；排名前段欄位應優先被人工驗證。"
    if chart_type == "predicted_vs_actual":
        return _model_result_interpretation(problem_type, best_model)
    if chart_type == "residual_plot":
        return "若殘差集中在特定區域，代表模型可能對某些資料族群預測不穩；應搭配極端值與分群檢查。"
    if chart_type in {"price_moving_average", "return_volatility", "rsi_macd", "time_series_forecast"} and financial_analysis:
        return _financial_summary(financial_analysis)
    return "圖表已由後端根據本次分析結果產生，沒有使用示範資料替代。"


def _chart_meaning(
    chart_type: str,
    model_analysis: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
) -> str:
    target = str(model_analysis.get("target_column") or "目標欄位")
    meanings = {
        "model_comparison": f"模型差距越明顯，越能判斷目前資料適合用哪種方法預測「{target}」。",
        "feature_importance": "如果少數欄位影響力很高，代表決策可以優先聚焦在這些因素；如果分散，代表問題可能需要更完整的資料解釋。",
        "predicted_vs_actual": "預測與實際越接近，代表模型越能支援預測或排序；差距大的區段則是下一步調查重點。",
        "residual_plot": "殘差若呈現規律，通常表示資料中仍有模型未捕捉的結構。",
    }
    if chart_type.startswith("financial") and financial_analysis:
        return "金融圖表反映的是目前資料期間內的趨勢與波動，不應單獨作為投資或營運決策依據。"
    if chart_type in {"price_moving_average", "return_volatility", "rsi_macd", "time_series_forecast"} and financial_analysis:
        return "時間序列圖表反映的是目前資料期間內的趨勢、波動與基準情境估計，不應單獨作為投資或營運決策依據。"
    return meanings.get(chart_type, "這張圖的重點是把分析結果轉成可檢查的證據。")


def _chart_trend_interpretation(
    chart_type: str,
    model_analysis: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
) -> str:
    if (chart_type.startswith("financial") or chart_type in {"price_moving_average", "return_volatility", "rsi_macd", "time_series_forecast"}) and financial_analysis:
        return f"目前趨勢標籤為「{financial_analysis.get('trend_label')}」，需觀察該趨勢是否持續出現在更多期間。"
    if chart_type == "model_comparison":
        return "模型排序可視為目前資料對不同方法的適配程度；若最佳模型明顯勝過 baseline，代表資料裡有可學習訊號。"
    if chart_type == "predicted_vs_actual":
        return "若大多數點集中在理想線附近，代表預測趨勢較穩；離散程度越大，代表不確定性越高。"
    return "此圖表主要用於解釋目前資料結構，不直接代表長期趨勢。"


def _chart_anomaly_note(chart_type: str, outliers: list[Any]) -> str:
    if outliers:
        return f"資料品質檢查已偵測到 {len(outliers)} 個數值欄位存在極端值；解讀此圖時應確認極端值是否為真實事件或資料錯誤。"
    if chart_type == "residual_plot":
        return "目前資料品質檢查未標示明顯極端值，但仍應查看殘差圖是否有成群偏差。"
    return "目前未從資料品質摘要中發現需要立即標示的極端值警訊。"


def _chart_business_insight(
    chart_type: str,
    model_analysis: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
) -> str:
    target = str(model_analysis.get("target_column") or "目標欄位")
    if chart_type == "feature_importance":
        return f"若前幾個欄位具有明確業務意義，它們很可能是影響「{target}」的主要槓桿。"
    if chart_type == "model_comparison":
        return "最佳模型若明顯優於 baseline，表示資料內確實有可被模型學習的訊號；若差距很小，應先改善資料而非追求更複雜模型。"
    if chart_type == "predicted_vs_actual":
        return "預測誤差較大的資料點通常代表特殊客群、特殊期間或資料紀錄問題。"
    if chart_type == "residual_plot":
        return "殘差規律可用來找出模型尚未理解的業務規則或資料分段。"
    if financial_analysis:
        return "金融指標可協助判斷短期壓力與趨勢，但需要搭配外部事件與基本面確認。"
    return "此圖可作為與團隊討論資料現象的共同依據。"


def _chart_recommended_action(chart_type: str) -> str:
    actions = {
        "model_comparison": "先採用排名第一的模型作為基準，並用 baseline 確認模型是否真的帶來改善。",
        "feature_importance": "檢查前 5 個重要欄位是否合理，若出現 ID、結果欄位或人工標記欄位，需排除後重跑分析。",
        "predicted_vs_actual": "找出誤差最大的資料列，確認是否代表特殊案例、資料錯誤或需要新增特徵。",
        "residual_plot": "若殘差呈現群聚或曲線，請改用非線性模型、加入分群欄位或重新切分資料。",
        "financial_indicators": "搭配較長時間區間與外部市場資料，確認目前訊號是否只是短期波動。",
        "financial_forecast": "把預測結果視為情境參考，不要單獨作為正式決策依據。",
        "price_moving_average": "先確認短期線與長期線方向是否一致，再搭配報酬率與波動率判斷。",
        "return_volatility": "若報酬率波動變大，請先檢查資料期間是否有特殊事件或資料異常。",
        "rsi_macd": "RSI 或 MACD 出現極端訊號時，請搭配趨勢圖與外部脈絡確認，不要單獨解讀。",
        "time_series_forecast": "把這張圖視為基準情境估計；若要用於決策，請加入近年視窗與回測誤差。",
    }
    return actions.get(chart_type, "用這張圖確認分析結論是否符合業務常識。")


def _chart_cannot_prove(chart_type: str) -> str:
    if chart_type == "feature_importance":
        return "這張圖不能證明因果關係，也不能保證重要欄位改變後結果一定改變。"
    if chart_type == "model_comparison":
        return "這張圖不能證明最佳模型在未來資料仍然最佳，需要交叉驗證或 holdout 檢查。"
    if chart_type == "predicted_vs_actual":
        return "這張圖不能指出誤差原因，只能提示哪些區段需要進一步檢查。"
    if chart_type == "residual_plot":
        return "這張圖不能直接修正模型，只能揭露模型可能未捕捉的規律。"
    if chart_type in {"price_moving_average", "return_volatility", "rsi_macd", "time_series_forecast"}:
        return "這張圖不能保證未來走勢，也不構成投資建議。"
    return "這張圖只能提供目前資料內的證據，不能單獨證明原因或未來結果。"


def _model_result_interpretation(problem_type: str, best_model: dict[str, Any]) -> str:
    if problem_type == "classification":
        accuracy = _safe_float(best_model.get("accuracy"))
        if accuracy is not None and accuracy >= 0.8:
            return "分類表現目前偏穩定，可用來建立初步分類或風險排序。"
        return "分類表現仍需進一步驗證，建議檢查類別不平衡與錯分樣本。"
    r2 = _safe_float(best_model.get("r2"))
    if r2 is not None and r2 >= 0.7:
        return "模型已解釋相當比例的目標變化，可作為初步預測與欄位解釋基準。"
    if r2 is not None and r2 >= 0.35:
        return "模型具備一定解釋力，但仍可能缺少重要欄位或需要更細緻特徵工程。"
    return "模型解釋力偏弱，建議先檢查資料品質、目標欄位設定與是否需要更多特徵。"


def _risk_sentence(
    quality_score: int,
    quality_issues: list[Any],
    financial_analysis: dict[str, Any] | None,
) -> str:
    risks = []
    if quality_score < 80 or quality_issues:
        risks.append(f"資料品質仍有 {len(quality_issues)} 類問題需要確認")
    if financial_analysis and financial_analysis.get("var_95") is not None:
        risks.append(f"金融風險指標 VaR 95% 為 {_format_optional_number(financial_analysis.get('var_95'))}")
    if not risks:
        return "目前沒有立即阻擋分析的高風險訊號，但仍需人工確認欄位定義與商業脈絡。"
    return "；".join(risks) + "。"


def _opportunity_sentence(
    model_analysis: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
) -> str:
    if financial_analysis:
        return f"若「{financial_analysis.get('trend_label')}」訊號持續，可進一步做情境分析與風險控管。"
    return f"可先使用模型比較與特徵重要性，找出影響「{model_analysis.get('target_column')}」的主要因素。"


def _risk_limitations(
    *,
    dataset_summary: dict[str, Any],
    model_analysis: dict[str, Any],
    quality_issues: list[Any],
    financial_analysis: dict[str, Any] | None,
) -> list[str]:
    limitations = [
        "本報告只根據目前上傳資料產生，不包含外部市場、企業策略或人工訪談資訊。",
        "模型表現來自目前資料切分，正式上線前應補交叉驗證、時間序列切分或獨立 holdout。",
        "若資料含有敏感或結果欄位，必須先確認是否造成 target leakage。",
    ]
    if quality_issues:
        limitations.append(f"資料品質檢查已列出 {len(quality_issues)} 類問題，這些問題可能影響結論可信度。")
    if financial_analysis:
        limitations.append("金融指標與預測僅供分析參考，不構成投資建議。")
    if model_analysis.get("automl_mode") == "off":
        limitations.append("本次未啟用 AutoML 調參，模型仍可能透過參數搜尋獲得更好表現。")
    return limitations


def _ai_conclusion(best_model: dict[str, Any], quality_score: int, next_action: str) -> str:
    return (
        f"目前資料可以產生可用的初步分析，最佳模型為「{best_model.get('model_name', '最佳模型')}」。"
        f"資料品質分數為 {quality_score}/100；最重要的下一步是：{next_action}"
    )


def _recommendation_reason(
    *,
    model: dict[str, Any],
    rows: int,
    features: int,
    missing_column_count: int,
    problem_type: str,
) -> str:
    family = str(model.get("family") or "")
    reasons = [f"目前資料有 {rows:,} 筆與 {features:,} 個可用特徵，任務類型是{_problem_type_label(problem_type)}"]
    if missing_column_count:
        reasons.append(f"且有 {missing_column_count} 個欄位含缺失值，系統會先做前處理")
    if family == "linear":
        reasons.append("線性模型可作為容易解釋的基準")
    elif family in {"ensemble", "boosting"}:
        reasons.append("集成模型較能處理非線性與混合欄位")
    elif family == "distance":
        reasons.append("距離型模型適合檢查相似樣本是否有一致模式")
    elif family == "kernel":
        reasons.append("核心方法可補足非線性邊界探索")
    return "；".join(reasons) + "。"


def _expected_output(problem_type: str, target_column: str) -> str:
    if problem_type == "classification":
        return f"預期可得到「{target_column}」的類別判斷、錯分風險與重要欄位。"
    return f"預期可得到「{target_column}」的數值預測、預測誤差與重要欄位。"


def _recommendation_score(
    model: dict[str, Any],
    rows: int,
    features: int,
    missing_column_count: int,
) -> str:
    score = 3
    family = str(model.get("family") or "")
    if family in {"ensemble", "boosting"} and (features >= 5 or missing_column_count):
        score += 1
    if family == "linear" and rows < 120:
        score += 1
    if str(model.get("complexity")) == "high" and rows < 50:
        score -= 1
    return f"{max(1, min(5, score))}/5"


def _model_evaluation_summary(problem_type: str, model: dict[str, Any] | None) -> str:
    if not model:
        return "尚未完成此模型的實際訓練結果。"
    if problem_type == "classification":
        return f"{model.get('model_name')}：Accuracy {_format_optional_number(model.get('accuracy'))}，F1-score {_format_optional_number(model.get('f1_score'))}。"
    return f"{model.get('model_name')}：RMSE {_format_optional_number(model.get('rmse'))}，MAE {_format_optional_number(model.get('mae'))}，R2 {_format_optional_number(model.get('r2'))}。"


def _model_static_guide(key: str, family: str, problem_type: str) -> dict[str, Any]:
    problem_label = _problem_type_label(problem_type)
    family_guides = {
        "linear": {
            "purpose": f"建立容易解釋的{problem_label}基準，快速判斷欄位與目標的整體關係。",
            "suitable_data_types": ["中小型表格資料", "欄位關係較線性的資料", "需要解釋性的分析"],
            "use_cases": ["銷售預測", "房價估算", "信用或風險基準", "趨勢解釋"],
        },
        "tree": {
            "purpose": f"用分支規則找出影響{problem_label}結果的條件。",
            "suitable_data_types": ["混合數值與類別欄位", "需要規則解釋的資料", "中小型資料"],
            "use_cases": ["客戶分層", "風險規則探索", "產品表現分段", "醫療風險初篩"],
        },
        "ensemble": {
            "purpose": f"整合多棵樹提升穩定度，處理非線性與欄位交互作用。",
            "suitable_data_types": ["已確認目標欄位的表格資料", "欄位較多的資料", "含類別與數值混合欄位"],
            "use_cases": ["房價預測", "客戶流失預測", "信用評分", "銷售預測"],
        },
        "boosting": {
            "purpose": f"逐步修正錯誤，追求更高的{problem_label}表現。",
            "suitable_data_types": ["訊號明確的表格資料", "中小型到中大型資料", "需要高精度的資料"],
            "use_cases": ["營收預測", "風險評分", "需求預測", "交易或異常風險排序"],
        },
        "distance": {
            "purpose": "用相似樣本推估結果，檢查資料是否存在局部相似模式。",
            "suitable_data_types": ["低維度資料", "樣本分布平滑的資料", "尺度已標準化的資料"],
            "use_cases": ["相似客戶推薦", "低維分類", "鄰近房價估算", "體育表現分群"],
        },
        "kernel": {
            "purpose": "建立非線性邊界，探索較複雜但資料量不大的模式。",
            "suitable_data_types": ["中小型資料", "非線性關係", "低到中維度欄位"],
            "use_cases": ["風險分類", "醫療初篩", "品質檢測", "特殊群體辨識"],
        },
    }
    guide = family_guides.get(family, family_guides["ensemble"])
    if key.startswith("xgboost") or key.startswith("lightgbm"):
        guide = {
            **guide,
            "use_cases": ["高精度銷售預測", "信用風險評分", "需求預測", "表格資料競賽型建模"],
        }
    return guide


def _infer_dataset_kind(
    columns: list[str],
    numeric_columns: list[str],
    date_candidates: list[Any],
) -> str:
    lowered = " ".join(columns).lower()
    vehicle_score = _keyword_score(
        lowered,
        (
            "car",
            "vehicle",
            "auto",
            "automobile",
            "make",
            "model",
            "mileage",
            "kms_driven",
            "km_driven",
            "fuel",
            "transmission",
            "engine",
            "owner",
            "seller_type",
            "汽車",
            "車款",
            "車型",
            "里程",
            "燃料",
            "排氣",
            "變速",
        ),
    )
    real_estate_score = _keyword_score(
        lowered,
        (
            "house",
            "housing",
            "home",
            "property",
            "real_estate",
            "real estate",
            "apartment",
            "bedroom",
            "bathroom",
            "sqft",
            "sq_feet",
            "area_sqft",
            "lot",
            "floor",
            "房價",
            "不動產",
            "房屋",
            "坪",
            "屋齡",
            "建坪",
            "地坪",
            "樓層",
        ),
    )
    commerce_score = _keyword_score(
        lowered,
        ("sales", "revenue", "customer", "product", "order", "sold", "營收", "銷售", "客戶", "商品"),
    )

    if date_candidates and any(
        keyword in lowered
        for keyword in ("close", "price", "nav", "return", "volume", "收盤", "價格", "股價", "淨值", "報酬")
    ):
        return "金融或時間序列資料"
    if vehicle_score >= 2:
        return "汽車銷售資料"
    if real_estate_score >= 2:
        return "房價或不動產資料"
    if any(keyword in lowered for keyword in ("patient", "diagnosis", "blood", "risk", "病患", "診斷", "醫療")):
        return "醫療或風險資料"
    if any(keyword in lowered for keyword in ("team", "player", "score", "match", "球員", "球隊", "比賽")):
        return "體育表現資料"
    if commerce_score:
        return "商業營運資料"
    if any(keyword in lowered for keyword in ("price", "amount", "value", "價格", "金額")):
        return "價格或交易表格資料"
    if date_candidates and numeric_columns:
        return "一般時間序列資料"
    if numeric_columns:
        return "待確認數值表格資料"
    return "類別或文字表格資料"


def _keyword_score(text: str, keywords: tuple[str, ...]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def _dataset_suitable_tasks(
    *,
    numeric_count: int,
    has_date: bool,
    recommended_targets: list[str],
    dataset_kind: str,
) -> list[str]:
    tasks: list[str] = []
    if recommended_targets:
        tasks.append("預測或分類目標欄位")
    if numeric_count >= 2:
        tasks.append("相關性與數值分布檢查")
    if numeric_count >= 3:
        tasks.append("特徵重要性與異常值檢查")
    if has_date:
        tasks.append("時間序列趨勢分析")
    if "金融" in dataset_kind or "時間序列" in dataset_kind:
        tasks.append("風險與波動分析")
    if not tasks:
        tasks.append("欄位品質與類別分布檢查")
    return list(dict.fromkeys(tasks))[:4]


def _story_list_sentence(value: Any, *, fallback: str, prefix: str = "可回答：") -> str:
    items = [str(item) for item in _as_list(value) if str(item).strip()]
    if not items:
        return fallback
    return f"{prefix}{'；'.join(items[:4])}。"


def _dataset_next_action(recommended_targets: list[str], dataset_kind: str) -> str:
    if recommended_targets:
        return f"先確認「{recommended_targets[0]}」是否就是你的問題目標，再進入模型或圖表分析。"
    return "先選擇分析目的與目標欄位；若不確定，從資料探索和欄位分布開始。"


def _dataset_primary_risk(
    quality_score: int,
    quality_issues: list[Any],
    missing_columns: list[Any],
) -> str:
    if quality_score < 70:
        return "資料品質偏低，建議先處理缺失、重複、極端值或疑似結果欄位，再進行正式分析。"
    if missing_columns:
        first = _as_dict(missing_columns[0])
        column = first.get("column") or "部分欄位"
        return f"最大風險是「{column}」等欄位存在缺失，可能影響模型可信度。"
    if quality_issues:
        first_issue = _as_dict(quality_issues[0]).get("message") or quality_issues[0]
        return f"需要注意：{first_issue}"
    return "目前沒有立即阻擋分析的資料品質警訊，但仍需確認欄位定義是否符合業務理解。"


def _dataset_completeness(row_count: int, column_count: int, missing_total: int) -> float:
    total_cells = max(1, row_count * max(1, column_count))
    return max(0.0, min(1.0, 1 - missing_total / total_cells))


def _confidence_level_from_quality(quality_score: int, issue_count: int) -> str:
    if quality_score >= 85 and issue_count <= 1:
        return "high"
    if quality_score >= 70 and issue_count <= 4:
        return "medium"
    return "low"


def _model_confidence(
    problem_type: str,
    best_model: dict[str, Any],
    baseline_model: dict[str, Any] | None,
    quality_score: int,
    quality_issues: list[Any],
) -> dict[str, Any]:
    blocking_issues = [str(_as_dict(issue).get("message") or issue) for issue in quality_issues[:5]]
    if quality_score < 70:
        return {
            "level": "low",
            "reason": "資料品質偏低，模型結果目前只能作為探索參考。",
            "blocking_issues": blocking_issues,
        }

    if problem_type == "classification":
        score = _safe_float(best_model.get("f1_score") or best_model.get("accuracy"))
        baseline = _safe_float((baseline_model or {}).get("f1_score") or (baseline_model or {}).get("accuracy"))
        if score is not None and score >= 0.8 and (baseline is None or score > baseline):
            level = "high" if quality_score >= 85 else "medium"
            reason = "分類分數高於 baseline，且資料品質可接受。"
        elif score is not None and score >= 0.6:
            level = "medium"
            reason = "分類模型已有一定訊號，但仍需檢查錯分樣本與類別不平衡。"
        else:
            level = "low"
            reason = "分類表現不足或缺少可靠評估，暫不適合直接決策。"
    else:
        r2 = _safe_float(best_model.get("r2"))
        lift = _relative_lift(best_model.get("rmse"), (baseline_model or {}).get("rmse"), higher_is_better=False)
        if r2 is not None and r2 >= 0.7 and (lift is None or lift > 10):
            level = "high" if quality_score >= 85 else "medium"
            reason = "模型解釋力較高，且相較 baseline 有明顯改善。"
        elif r2 is not None and r2 >= 0.35:
            level = "medium"
            reason = "模型已有一定解釋力，但仍可能缺少重要欄位或需要交叉驗證。"
        else:
            level = "low"
            reason = "模型解釋力偏弱，建議先檢查目標欄位、資料品質與特徵設定。"

    if blocking_issues and level == "high":
        level = "medium"
        reason += " 但資料仍有品質警訊，因此可信度下修。"
    return {
        "level": level,
        "reason": reason,
        "blocking_issues": blocking_issues,
    }


def _confidence_label(level: str) -> str:
    return {
        "high": "高",
        "medium": "中",
        "low": "低",
    }.get(level, "中")


def _problem_type_label(problem_type: str) -> str:
    return "分類" if problem_type == "classification" else "回歸"


def _difficulty_label(complexity: str) -> str:
    return {
        "low": "初學者",
        "medium": "中級",
        "high": "進階",
    }.get(complexity, "中級")


def _chart_title(chart_type: str) -> str:
    return {
        "model_comparison": "模型比較圖",
        "feature_importance": "特徵重要性",
        "predicted_vs_actual": "預測值與實際值",
        "residual_plot": "殘差圖",
    }.get(chart_type, chart_type)


def _relative_lift(
    value: Any,
    baseline: Any,
    *,
    higher_is_better: bool,
) -> float | None:
    current = _safe_float(value)
    base = _safe_float(baseline)
    if current is None or base is None or base == 0:
        return None
    if higher_is_better:
        return max(0.0, ((current - base) / abs(base)) * 100)
    return max(0.0, ((base - current) / abs(base)) * 100)


def _format_optional_number(value: Any) -> str:
    number = _safe_float(value)
    if number is None:
        return "未提供"
    if abs(number) >= 100:
        return f"{number:,.2f}"
    if abs(number) >= 1:
        return f"{number:.3f}"
    return f"{number:.4f}"


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
