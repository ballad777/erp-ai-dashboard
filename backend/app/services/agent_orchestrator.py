from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

import pandas as pd
from fastapi import HTTPException, UploadFile

from app.services.dataset_analyzer import analyze_dataframe, merge_dataframes, read_uploaded_dataframe
from app.services.financial_analyzer import run_financial_analysis
from app.services.model_runner import run_model_analysis


@dataclass(frozen=True)
class AgentStep:
    agent_name: str
    status: str
    summary: str
    outputs: dict[str, Any]


async def run_uploaded_agent_workflow(
    file: UploadFile,
    target_column: str,
    analysis_mode: str = "auto",
    chart_types: str = "auto",
    model_selection_mode: str = "auto",
    selected_models: str = "auto",
    automl_mode: str = "quick",
    date_column: str | None = None,
    price_column: str | None = None,
) -> dict[str, Any]:
    df, file_name = await read_uploaded_dataframe(file)
    return run_agent_workflow(
        df=df,
        file_name=file_name,
        target_column=target_column,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        model_selection_mode=model_selection_mode,
        selected_models=selected_models,
        automl_mode=automl_mode,
        date_column=date_column,
        price_column=price_column,
    )


async def run_uploaded_merged_agent_workflow(
    files: list[UploadFile],
    target_column: str,
    analysis_mode: str = "auto",
    chart_types: str = "auto",
    model_selection_mode: str = "auto",
    selected_models: str = "auto",
    automl_mode: str = "quick",
    date_column: str | None = None,
    price_column: str | None = None,
) -> dict[str, Any]:
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="AI 協作合併分析至少需要 2 個檔案。")

    loaded_datasets: list[tuple[str, pd.DataFrame]] = []
    for file in files:
        df, file_name = await read_uploaded_dataframe(file)
        loaded_datasets.append((file_name, df))

    merged_df, metadata = merge_dataframes(loaded_datasets)
    result = run_agent_workflow(
        df=merged_df,
        file_name="merged_dataset.csv",
        target_column=target_column,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        model_selection_mode=model_selection_mode,
        selected_models=selected_models,
        automl_mode=automl_mode,
        date_column=date_column,
        price_column=price_column,
    )
    result["agent_steps"].insert(
        0,
        AgentStep(
            agent_name="資料理解代理",
            status="completed",
            summary=f"已先合併 {metadata['source_file_count']} 個檔案，策略：{metadata['merge_strategy']}。",
            outputs={"merge_notes": metadata["merge_notes"]},
        ).__dict__,
    )
    return result


def run_agent_workflow(
    df: pd.DataFrame,
    file_name: str,
    target_column: str,
    analysis_mode: str = "auto",
    chart_types: str = "auto",
    model_selection_mode: str = "auto",
    selected_models: str = "auto",
    automl_mode: str = "quick",
    date_column: str | None = None,
    price_column: str | None = None,
) -> dict[str, Any]:
    agent_steps: list[AgentStep] = []

    dataset_summary = analyze_dataframe(df, file_name=file_name)
    agent_steps.append(
        AgentStep(
            agent_name="資料理解代理",
            status="completed",
            summary=f"已解析 {dataset_summary['row_count']} 筆資料與 {dataset_summary['column_count']} 個欄位。",
            outputs={
                "row_count": dataset_summary["row_count"],
                "column_count": dataset_summary["column_count"],
                "recommended_target_columns": dataset_summary["recommended_target_columns"],
            },
        )
    )

    model_analysis = run_model_analysis(
        df=df,
        file_name=file_name,
        target_column=target_column,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        model_selection_mode=model_selection_mode,
        selected_models=selected_models,
        automl_mode=automl_mode,
    )
    best_model = _best_model_name(model_analysis)
    agent_steps.append(
        AgentStep(
            agent_name="模型分析代理",
            status="completed",
            summary=f"已完成 {len(model_analysis['model_results'])} 個模型訓練與比較，最佳模型為 {best_model}。",
            outputs={
                "problem_type": model_analysis["problem_type"],
                "best_model": best_model,
                "automl_mode": model_analysis["automl_mode"],
                "model_results_path": model_analysis["model_results_path"],
            },
        )
    )

    financial_analysis: dict[str, Any] | None = None
    try:
        financial_analysis = run_financial_analysis(
            df=df,
            file_name=file_name,
            date_column=date_column,
            price_column=price_column,
        )
        agent_steps.append(
            AgentStep(
                agent_name="金融分析代理",
                status="completed",
                summary=f"已完成金融指標、VaR 與時間序列預測，訊號為 {financial_analysis['trend_label']}。",
                outputs={
                    "trend_label": financial_analysis["trend_label"],
                    "var_95": financial_analysis["var_95"],
                    "var_99": financial_analysis["var_99"],
                    "indicator_path": financial_analysis["indicator_path"],
                },
            )
        )
    except HTTPException as exc:
        agent_steps.append(
            AgentStep(
                agent_name="金融分析代理",
                status="skipped",
                summary=f"資料不符合金融分析條件：{exc.detail}",
                outputs={},
            )
        )

    charts = list(model_analysis["charts"])
    if financial_analysis:
        charts.extend(financial_analysis["charts"])
    agent_steps.append(
        AgentStep(
            agent_name="視覺化代理",
            status="completed",
            summary=f"已整理 {len(charts)} 張系統產生的圖表。",
            outputs={"chart_count": len(charts), "charts": charts},
        )
    )

    deterministic_summary = _build_agent_summary(dataset_summary, model_analysis, financial_analysis)
    llm_summary, llm_provider, llm_notes = _try_llm_summary(deterministic_summary)
    agent_steps.append(
        AgentStep(
            agent_name="報告代理",
            status="completed",
            summary="已生成分析摘要；若環境有 LLM 金鑰，會優先使用 LLM 強化文字。",
            outputs={"llm_provider": llm_provider, "notes": llm_notes},
        )
    )

    return {
        "file_name": file_name,
        "target_column": target_column,
        "agent_steps": [step.__dict__ for step in agent_steps],
        "executive_summary": llm_summary,
        "llm_provider": llm_provider,
        "dataset_summary": dataset_summary,
        "model_analysis": model_analysis,
        "financial_analysis": financial_analysis,
        "notes": llm_notes,
    }


def _best_model_name(model_analysis: dict[str, Any]) -> str:
    if model_analysis["problem_type"] == "classification":
        best = max(
            model_analysis["model_results"],
            key=lambda result: float(result.get("accuracy") or 0),
        )
    else:
        best = min(model_analysis["model_results"], key=lambda result: float(result["rmse"]))
    return str(best["model_name"])


def _build_agent_summary(
    dataset_summary: dict[str, Any],
    model_analysis: dict[str, Any],
    financial_analysis: dict[str, Any] | None,
) -> list[str]:
    best_model = _best_model_name(model_analysis)
    summary = [
        f"資料理解代理判斷資料集共有 {dataset_summary['row_count']} 筆、{dataset_summary['column_count']} 欄，已完成結構化摘要。",
        f"模型分析代理判斷本次為「{model_analysis['problem_type']}」問題，已比較 {len(model_analysis['model_results'])} 個模型，最佳模型為 {best_model}。",
        f"視覺化代理已產出 {len(model_analysis['charts'])} 張模型圖表，所有圖表都已寫入 generated_outputs/charts/。",
    ]
    if financial_analysis:
        summary.append(
            f"金融分析代理已完成金融分析，訊號為「{financial_analysis['trend_label']}」，VaR 95% 為 {financial_analysis['var_95']}。"
        )
    else:
        summary.append("金融分析代理已檢查資料欄位，本資料未達金融分析條件或尚未指定日期與價格欄位。")
    return summary


def _try_llm_summary(summary: list[str]) -> tuple[list[str], str, list[str]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return summary, "local_rule_based", ["未設定 OPENAI_API_KEY，已使用本機規則摘要，不假裝 LLM 執行。"]

    prompt = (
        "請以繁體中文整理以下智能金融資料分析摘要，輸出 3 到 5 點高層管理摘要：\n"
        + "\n".join(f"- {item}" for item in summary)
    )
    payload = json.dumps(
        {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "input": prompt,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = _extract_openai_text(data)
        if not text:
            return summary, "openai_unavailable", ["OpenAI 回應沒有可讀文字，已使用本機規則摘要。"]
        return [line.strip("-• 　") for line in text.splitlines() if line.strip()], "openai", []
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return summary, "openai_failed", [f"OpenAI 摘要呼叫失敗，已使用本機規則摘要：{exc}"]


def _extract_openai_text(data: dict[str, Any]) -> str:
    if "output_text" in data and isinstance(data["output_text"], str):
        return data["output_text"]
    parts: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                parts.append(str(content["text"]))
    return "\n".join(parts)
