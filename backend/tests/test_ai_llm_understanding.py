import pandas as pd
from fastapi import HTTPException

from app.services.data_understanding import build_dataset_understanding, plan_multi_table_strategy
from app.services.financial_analyzer import run_financial_analysis


def _ai_llm_tables() -> list[tuple[str, pd.DataFrame]]:
    return [
        (
            "benchmark_scores.csv",
            pd.DataFrame(
                {
                    "model_id": ["M001", "M002", "M003"],
                    "model_name": ["GPT-3", "T5-XXL", "Claude"],
                    "organization": ["OpenAI", "Google", "Anthropic"],
                    "release_date": ["2020-06-11", "2020-02-24", "2023-03-14"],
                    "benchmark": ["MMLU", "HumanEval", "GSM8K"],
                    "score": [32.8, 45.1, 76.4],
                    "score_pct": [32.8, 45.1, 76.4],
                }
            ),
        ),
        (
            "capability_milestones.csv",
            pd.DataFrame(
                {
                    "event_id": ["E001", "E002"],
                    "date": ["2020-05-28", "2023-11-06"],
                    "milestone_name": ["GPT-3 paper", "GPT-4 Turbo"],
                    "organization": ["OpenAI", "OpenAI"],
                    "significance_score": [9, 8],
                    "description": ["Few-shot learning emerges", "Larger context window"],
                }
            ),
        ),
        (
            "compute_estimates.csv",
            pd.DataFrame(
                {
                    "model_id": ["M001", "M002"],
                    "model_name": ["GPT-3", "T5-XXL"],
                    "organization": ["OpenAI", "Google"],
                    "release_date": ["2020-06-11", "2020-02-24"],
                    "params_billions": [175.0, 11.0],
                    "training_flops": [3.68e23, 1.45e21],
                    "gpu_hours_h100_equiv": [4593, 18],
                    "training_cost_usd_est": [18375, 72],
                }
            ),
        ),
        (
            "models_catalog.csv",
            pd.DataFrame(
                {
                    "model_id": ["M001", "M002"],
                    "model_name": ["GPT-3", "T5-XXL"],
                    "organization": ["OpenAI", "Google"],
                    "release_date": ["2020-06-11", "2020-02-24"],
                    "params_billions": [175.0, 11.0],
                    "access_type": ["closed_api", "open_weights"],
                    "context_window_k_tokens": [4, 2],
                }
            ),
        ),
        (
            "pricing_history.csv",
            pd.DataFrame(
                {
                    "year_month": ["2020-06", "2020-07", "2023-03"],
                    "model_name": ["GPT-3", "GPT-3", "Claude"],
                    "input_usd_per_1m_tokens": [60.0, 60.0, 8.0],
                    "output_usd_per_1m_tokens": [60.0, 60.0, 24.0],
                    "blended_usd_per_1m_tokens": [60.0, 60.0, 16.0],
                }
            ),
        ),
    ]


def test_ai_llm_tables_are_not_sports_or_financial() -> None:
    for file_name, df in _ai_llm_tables():
        understanding = build_dataset_understanding(df, file_name=file_name)

        assert understanding["primary_domain"]["key"] == "ai_llm"
        assert understanding["primary_domain"]["label"] == "AI/LLM模型評估資料集"
        assert understanding["financial_eligibility"]["eligible"] is False
        assert "sports" not in [topic["key"] for topic in understanding["possible_data_topics"][:1]]


def test_ai_llm_multi_table_strategy_is_relationship_not_union() -> None:
    plan = plan_multi_table_strategy(_ai_llm_tables())

    assert plan["recommended_strategy"] == "multi_table_relationship"
    assert plan["label"] == "多表關聯分析"
    assert plan["common_column_ratio"] < 0.75
    keys = {candidate["key"] for candidate in plan["join_key_candidates"]}
    assert {"model_name", "organization"}.issubset(keys)
    assert any("不建議直接垂直合併" in warning for warning in plan["warnings"])


def test_ai_llm_dataset_does_not_enable_rsi_macd_or_var() -> None:
    benchmark_df = _ai_llm_tables()[0][1]

    try:
        run_financial_analysis(benchmark_df, file_name="benchmark_scores.csv")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "不適合金融技術分析" in str(exc.detail)
        assert "benchmark 分數趨勢" in str(exc.detail)
    else:
        raise AssertionError("AI/LLM benchmark data must not run RSI/MACD/VaR")
