from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from docx import Document
from docx.shared import Inches
from fastapi import UploadFile

from app.services.agent_orchestrator import (
    run_uploaded_agent_workflow,
    run_uploaded_merged_agent_workflow,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_DIR = REPO_ROOT / "generated_outputs" / "reports"


async def generate_uploaded_report(
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
    workflow = await run_uploaded_agent_workflow(
        file=file,
        target_column=target_column,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        model_selection_mode=model_selection_mode,
        selected_models=selected_models,
        automl_mode=automl_mode,
        date_column=date_column,
        price_column=price_column,
    )
    return generate_report_from_workflow(workflow)


async def generate_uploaded_merged_report(
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
    workflow = await run_uploaded_merged_agent_workflow(
        files=files,
        target_column=target_column,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        model_selection_mode=model_selection_mode,
        selected_models=selected_models,
        automl_mode=automl_mode,
        date_column=date_column,
        price_column=price_column,
    )
    return generate_report_from_workflow(workflow)


def generate_report_from_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"analysis_report_{uuid4().hex}.docx"

    document = Document()
    document.add_heading("智能金融資料分析報告", 0)
    document.add_paragraph(f"資料檔案：{workflow['file_name']}")
    document.add_paragraph(f"目標欄位：{workflow['target_column']}")
    document.add_paragraph(f"摘要來源：{workflow['llm_provider']}")

    document.add_heading("管理摘要", level=1)
    for item in workflow["executive_summary"]:
        document.add_paragraph(str(item), style="List Bullet")

    document.add_heading("分析代理執行紀錄", level=1)
    agent_table = document.add_table(rows=1, cols=3)
    agent_table.style = "Table Grid"
    hdr_cells = agent_table.rows[0].cells
    hdr_cells[0].text = "分析代理"
    hdr_cells[1].text = "狀態"
    hdr_cells[2].text = "摘要"
    for step in workflow["agent_steps"]:
        row_cells = agent_table.add_row().cells
        row_cells[0].text = str(step["agent_name"])
        row_cells[1].text = str(step["status"])
        row_cells[2].text = str(step["summary"])

    dataset = workflow["dataset_summary"]
    document.add_heading("資料摘要", level=1)
    document.add_paragraph(f"資料列數：{dataset['row_count']}")
    document.add_paragraph(f"欄位數：{dataset['column_count']}")
    document.add_paragraph(f"建議目標欄位：{', '.join(dataset.get('recommended_target_columns') or []) or '無'}")

    model_analysis = workflow["model_analysis"]
    document.add_heading("模型比較", level=1)
    document.add_paragraph(f"問題型態：{model_analysis['problem_type']}")
    document.add_paragraph(f"AutoML 模式：{model_analysis['automl_mode']}")
    model_table = document.add_table(rows=1, cols=6)
    model_table.style = "Table Grid"
    headers = ["模型", "家族", "R2", "RMSE", "MAE", "訓練時間"]
    for index, header in enumerate(headers):
        model_table.rows[0].cells[index].text = header
    for metric in model_analysis["model_results"]:
        row = model_table.add_row().cells
        row[0].text = str(metric["model_name"])
        row[1].text = str(metric["model_family"])
        row[2].text = str(metric["r2"])
        row[3].text = str(metric["rmse"])
        row[4].text = str(metric["mae"])
        row[5].text = f"{metric['training_time_seconds']} 秒"

    financial_analysis = workflow.get("financial_analysis")
    if financial_analysis:
        document.add_heading("金融分析", level=1)
        for item in financial_analysis["summary"]:
            document.add_paragraph(str(item), style="List Bullet")
        document.add_paragraph(f"VaR 95%：{financial_analysis['var_95']}")
        document.add_paragraph(f"VaR 99%：{financial_analysis['var_99']}")

    document.add_heading("圖表輸出", level=1)
    charts = workflow["model_analysis"]["charts"]
    if financial_analysis:
        charts = [*charts, *financial_analysis["charts"]]
    for chart in charts[:8]:
        document.add_paragraph(f"{chart['title']}：{chart['chart_path']}")
        chart_path = REPO_ROOT / chart["chart_path"]
        if chart_path.exists():
            document.add_picture(str(chart_path), width=Inches(5.8))

    if workflow["notes"]:
        document.add_heading("備註", level=1)
        for note in workflow["notes"]:
            document.add_paragraph(str(note), style="List Bullet")

    document.save(report_path)

    return {
        "file_name": workflow["file_name"],
        "target_column": workflow["target_column"],
        "report_path": str(report_path.relative_to(REPO_ROOT)),
        "report_url": f"/generated_outputs/reports/{report_path.name}",
        "workflow": workflow,
        "notes": [
            "已產生 Word 分析報告。",
            "一鍵 ZIP 套件目前未啟用。",
        ],
    }
