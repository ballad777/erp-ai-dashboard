import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import (
    AgentWorkflowResponse,
    DatasetAnalysisResponse,
    ErrorResponse,
    FinancialAnalysisResponse,
    GeneratedCodeResponse,
    ModelAnalysisResponse,
    MultipleDatasetAnalysisResponse,
    ReportResponse,
)
from app.services.agent_orchestrator import (
    run_uploaded_agent_workflow,
    run_uploaded_merged_agent_workflow,
)
from app.services.code_generator import (
    generate_uploaded_code_artifacts,
    generate_uploaded_merged_code_artifacts,
)
from app.services.dataset_analyzer import (
    analyze_multiple_uploaded_datasets,
    analyze_uploaded_dataset,
)
from app.services.financial_analyzer import (
    analyze_uploaded_financial_dataset,
    analyze_uploaded_merged_financial_dataset,
)
from app.services.model_runner import (
    get_model_options,
    run_uploaded_merged_model_analysis,
    run_uploaded_model_analysis,
)
from app.services.report_generator import (
    generate_uploaded_merged_report,
    generate_uploaded_report,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATED_OUTPUTS_DIR = REPO_ROOT / "generated_outputs"


def get_cors_origins() -> list[str]:
    configured_origins = os.getenv("FRONTEND_ORIGINS", "").strip()
    if configured_origins:
        return [
            origin.strip().rstrip("/")
            for origin in configured_origins.split(",")
            if origin.strip()
        ]

    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app = FastAPI(
    title="智能金融資料分析 API",
    description="智能金融資料分析的資料分析與模型訓練服務。",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: object, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: object, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": f"伺服器發生未預期錯誤：{exc}"},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "智能金融資料分析 API"}


@app.post(
    "/api/datasets/analyze",
    response_model=DatasetAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_dataset(
    file: UploadFile = File(...),
) -> DatasetAnalysisResponse:
    result = await analyze_uploaded_dataset(file)
    return DatasetAnalysisResponse(**result)


@app.post(
    "/api/datasets/analyze-multiple",
    response_model=MultipleDatasetAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_multiple_datasets(
    files: list[UploadFile] = File(...),
) -> MultipleDatasetAnalysisResponse:
    result = await analyze_multiple_uploaded_datasets(files)
    return MultipleDatasetAnalysisResponse(**result)


@app.post(
    "/api/models/analyze",
    response_model=ModelAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_models(
    target_column: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    model_selection_mode: str = Form("auto"),
    selected_models: str = Form("auto"),
    automl_mode: str = Form("off"),
    file: UploadFile = File(...),
) -> ModelAnalysisResponse:
    result = await run_uploaded_model_analysis(
        file=file,
        target_column=target_column,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        model_selection_mode=model_selection_mode,
        selected_models=selected_models,
        automl_mode=automl_mode,
    )
    return ModelAnalysisResponse(**result)


@app.post(
    "/api/models/analyze-merged",
    response_model=ModelAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_merged_models(
    target_column: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    model_selection_mode: str = Form("auto"),
    selected_models: str = Form("auto"),
    automl_mode: str = Form("off"),
    files: list[UploadFile] = File(...),
) -> ModelAnalysisResponse:
    result = await run_uploaded_merged_model_analysis(
        files=files,
        target_column=target_column,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
        model_selection_mode=model_selection_mode,
        selected_models=selected_models,
        automl_mode=automl_mode,
    )
    return ModelAnalysisResponse(**result)


@app.get("/api/models/options")
async def model_options(problem_type: str | None = None) -> dict[str, object]:
    return {"models": get_model_options(problem_type)}


@app.post(
    "/api/code/generate",
    response_model=GeneratedCodeResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_code(
    target_column: str = Form(...),
    model_name: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    file: UploadFile = File(...),
) -> GeneratedCodeResponse:
    result = await generate_uploaded_code_artifacts(
        file=file,
        target_column=target_column,
        model_name=model_name,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
    )
    return GeneratedCodeResponse(**result)


@app.post(
    "/api/code/generate-merged",
    response_model=GeneratedCodeResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_merged_code(
    target_column: str = Form(...),
    model_name: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    files: list[UploadFile] = File(...),
) -> GeneratedCodeResponse:
    result = await generate_uploaded_merged_code_artifacts(
        files=files,
        target_column=target_column,
        model_name=model_name,
        analysis_mode=analysis_mode,
        chart_types=chart_types,
    )
    return GeneratedCodeResponse(**result)


@app.post(
    "/api/finance/analyze",
    response_model=FinancialAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_finance(
    date_column: str | None = Form(None),
    price_column: str | None = Form(None),
    file: UploadFile = File(...),
) -> FinancialAnalysisResponse:
    result = await analyze_uploaded_financial_dataset(
        file=file,
        date_column=date_column,
        price_column=price_column,
    )
    return FinancialAnalysisResponse(**result)


@app.post(
    "/api/finance/analyze-merged",
    response_model=FinancialAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_merged_finance(
    date_column: str | None = Form(None),
    price_column: str | None = Form(None),
    files: list[UploadFile] = File(...),
) -> FinancialAnalysisResponse:
    result = await analyze_uploaded_merged_financial_dataset(
        files=files,
        date_column=date_column,
        price_column=price_column,
    )
    return FinancialAnalysisResponse(**result)


@app.post(
    "/api/agents/analyze",
    response_model=AgentWorkflowResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_with_agents(
    target_column: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    model_selection_mode: str = Form("auto"),
    selected_models: str = Form("auto"),
    automl_mode: str = Form("quick"),
    date_column: str | None = Form(None),
    price_column: str | None = Form(None),
    file: UploadFile = File(...),
) -> AgentWorkflowResponse:
    result = await run_uploaded_agent_workflow(
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
    return AgentWorkflowResponse(**result)


@app.post(
    "/api/agents/analyze-merged",
    response_model=AgentWorkflowResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_merged_with_agents(
    target_column: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    model_selection_mode: str = Form("auto"),
    selected_models: str = Form("auto"),
    automl_mode: str = Form("quick"),
    date_column: str | None = Form(None),
    price_column: str | None = Form(None),
    files: list[UploadFile] = File(...),
) -> AgentWorkflowResponse:
    result = await run_uploaded_merged_agent_workflow(
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
    return AgentWorkflowResponse(**result)


@app.post(
    "/api/reports/generate",
    response_model=ReportResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_report(
    target_column: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    model_selection_mode: str = Form("auto"),
    selected_models: str = Form("auto"),
    automl_mode: str = Form("quick"),
    date_column: str | None = Form(None),
    price_column: str | None = Form(None),
    file: UploadFile = File(...),
) -> ReportResponse:
    result = await generate_uploaded_report(
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
    return ReportResponse(**result)


@app.post(
    "/api/reports/generate-merged",
    response_model=ReportResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_merged_report(
    target_column: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    model_selection_mode: str = Form("auto"),
    selected_models: str = Form("auto"),
    automl_mode: str = Form("quick"),
    date_column: str | None = Form(None),
    price_column: str | None = Form(None),
    files: list[UploadFile] = File(...),
) -> ReportResponse:
    result = await generate_uploaded_merged_report(
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
    return ReportResponse(**result)


app.mount(
    "/generated_outputs",
    StaticFiles(directory=GENERATED_OUTPUTS_DIR),
    name="generated_outputs",
)
