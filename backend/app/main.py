import logging
import os
import asyncio
from io import BytesIO
from pathlib import Path
from time import monotonic
from threading import RLock
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.schemas import (
    AgentWorkflowResponse,
    AnalysisJobResponse,
    AnalysisJobStartResponse,
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
from app.services.artifact_access import resolve_artifact_token
from app.services.code_generator import (
    generate_uploaded_code_artifacts,
    generate_uploaded_merged_code_artifacts,
)
from app.services.dataset_analyzer import (
    MAX_BATCH_UPLOAD_BYTES,
    MAX_UPLOAD_BYTES,
    analyze_multiple_uploaded_datasets,
    analyze_uploaded_dataset,
    validate_upload_batch,
)
from app.services.analysis_jobs import (
    cancel_analysis_job,
    create_analysis_job,
    get_analysis_job,
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
from app.database import initialize_database
from app.database import repository
from app.services.run_governance import governed_async_runner, governed_runner

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATED_OUTPUTS_DIR = REPO_ROOT / "generated_outputs"
logger = logging.getLogger(__name__)
_RATE_LIMIT_LOCK = RLock()
_RATE_LIMIT_BUCKETS: dict[str, list[float]] = {}


def get_cors_origins() -> list[str]:
    configured_origins = os.getenv("FRONTEND_ORIGINS", "").strip()
    if configured_origins:
        return [
            origin.strip().rstrip("/")
            for origin in configured_origins.split(",")
            if origin.strip()
        ]

    local_frontend_ports = (3000, 3010, 3011, 3012, 3013, 3014, 3015)
    return [
        origin
        for port in local_frontend_ports
        for origin in (
            f"http://localhost:{port}",
            f"http://127.0.0.1:{port}",
        )
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


@app.on_event("startup")
async def startup() -> None:
    initialize_database()


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=()"
    )
    if request.url.path.startswith("/api/artifacts/"):
        response.headers["Cache-Control"] = "private, no-store"
    elif request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.middleware("http")
async def rate_limit_api_requests(request: Request, call_next):
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
    limit = int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "180"))
    if limit <= 0:
        return await call_next(request)
    client = request.client.host if request.client else "unknown"
    route_key = f"{client}:{request.url.path}"
    current = monotonic()
    cutoff = current - 60
    with _RATE_LIMIT_LOCK:
        bucket = [stamp for stamp in _RATE_LIMIT_BUCKETS.get(route_key, []) if stamp >= cutoff]
        if len(bucket) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "請求過於頻繁，請稍後再試。"},
                headers={"Retry-After": "60"},
            )
        bucket.append(current)
        _RATE_LIMIT_BUCKETS[route_key] = bucket
    return await call_next(request)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: object, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: object, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled API exception",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "伺服器暫時無法完成請求，請稍後再試。"},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "智能金融資料分析 API"}


@app.get("/api/auth/session")
async def demo_session() -> dict[str, object]:
    identity = repository.ensure_demo_identity()
    return {
        "auth_mode": "demo",
        "user": {
            "id": identity.user_id,
            "email": identity.email,
        },
        "project": {
            "id": identity.project_id,
            "name": identity.project_name,
        },
        "notes": [
            "目前為封閉測試 demo identity；正式公開 SaaS 必須接入真正登入、Project ownership 與 artifact 授權檢查。",
        ],
    }


@app.get("/api/artifacts/{token}")
async def get_artifact(token: str) -> FileResponse:
    artifact_path = resolve_artifact_token(
        token,
        root=GENERATED_OUTPUTS_DIR,
    )
    image_media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }
    media_type = image_media_types.get(artifact_path.suffix.lower())
    return FileResponse(
        artifact_path,
        headers={"Cache-Control": "private, no-store"},
        media_type=media_type,
        filename=artifact_path.name,
        content_disposition_type="inline" if media_type else "attachment",
    )


@app.get("/api/jobs/{job_id}", response_model=AnalysisJobResponse)
async def analysis_job_status(job_id: str) -> AnalysisJobResponse:
    return AnalysisJobResponse(**get_analysis_job(job_id))


@app.delete("/api/jobs/{job_id}", response_model=AnalysisJobResponse)
async def stop_analysis_job(job_id: str) -> AnalysisJobResponse:
    return AnalysisJobResponse(**cancel_analysis_job(job_id))


@app.post("/api/jobs/models", response_model=AnalysisJobStartResponse)
async def start_model_analysis_job(
    target_column: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    model_selection_mode: str = Form("auto"),
    selected_models: str = Form("auto"),
    automl_mode: str = Form("off"),
    files: list[UploadFile] = File(...),
) -> AnalysisJobStartResponse:
    snapshots = await _snapshot_uploads(files)
    parameters = {
        "target_column": target_column,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "model_selection_mode": model_selection_mode,
        "selected_models": selected_models,
        "automl_mode": automl_mode,
        "file_count": len(snapshots),
    }

    def runner(progress, should_cancel):
        def execute(uploads: list[UploadFile]) -> dict[str, Any]:
            if len(uploads) == 1:
                return asyncio.run(
                    run_uploaded_model_analysis(
                        file=uploads[0],
                        target_column=target_column,
                        analysis_mode=analysis_mode,
                        chart_types=chart_types,
                        model_selection_mode=model_selection_mode,
                        selected_models=selected_models,
                        automl_mode=automl_mode,
                        progress_callback=progress,
                        should_cancel=should_cancel,
                    )
                )
            return asyncio.run(
                run_uploaded_merged_model_analysis(
                    files=uploads,
                    target_column=target_column,
                    analysis_mode=analysis_mode,
                    chart_types=chart_types,
                    model_selection_mode=model_selection_mode,
                    selected_models=selected_models,
                    automl_mode=automl_mode,
                    progress_callback=progress,
                    should_cancel=should_cancel,
                )
            )
        return governed_runner(
            run_type="model_analysis_job",
            snapshots=snapshots,
            parameters=parameters,
            restore_uploads=_restore_uploads,
            execute=execute,
        )

    job = create_analysis_job("models", runner)
    return AnalysisJobStartResponse(
        job_id=job.job_id,
        status=job.status,
        stage=job.stage,
    )


@app.post("/api/jobs/finance", response_model=AnalysisJobStartResponse)
async def start_financial_analysis_job(
    date_column: str | None = Form(None),
    price_column: str | None = Form(None),
    files: list[UploadFile] = File(...),
) -> AnalysisJobStartResponse:
    snapshots = await _snapshot_uploads(files)
    parameters = {
        "date_column": date_column,
        "price_column": price_column,
        "file_count": len(snapshots),
    }

    def runner(progress, should_cancel):
        def execute(uploads: list[UploadFile]) -> dict[str, Any]:
            if len(uploads) == 1:
                return asyncio.run(
                    analyze_uploaded_financial_dataset(
                        file=uploads[0],
                        date_column=date_column,
                        price_column=price_column,
                        progress_callback=progress,
                        should_cancel=should_cancel,
                    )
                )
            return asyncio.run(
                analyze_uploaded_merged_financial_dataset(
                    files=uploads,
                    date_column=date_column,
                    price_column=price_column,
                    progress_callback=progress,
                    should_cancel=should_cancel,
                )
            )
        return governed_runner(
            run_type="financial_analysis_job",
            snapshots=snapshots,
            parameters=parameters,
            restore_uploads=_restore_uploads,
            execute=execute,
        )

    job = create_analysis_job("finance", runner)
    return AnalysisJobStartResponse(
        job_id=job.job_id,
        status=job.status,
        stage=job.stage,
    )


@app.post("/api/jobs/agents", response_model=AnalysisJobStartResponse)
async def start_agent_analysis_job(
    target_column: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    model_selection_mode: str = Form("auto"),
    selected_models: str = Form("auto"),
    automl_mode: str = Form("quick"),
    date_column: str | None = Form(None),
    price_column: str | None = Form(None),
    files: list[UploadFile] = File(...),
) -> AnalysisJobStartResponse:
    snapshots = await _snapshot_uploads(files)
    parameters = {
        "target_column": target_column,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "model_selection_mode": model_selection_mode,
        "selected_models": selected_models,
        "automl_mode": automl_mode,
        "date_column": date_column,
        "price_column": price_column,
        "file_count": len(snapshots),
    }

    def runner(progress, should_cancel):
        def execute(uploads: list[UploadFile]) -> dict[str, Any]:
            if len(uploads) == 1:
                return asyncio.run(
                    run_uploaded_agent_workflow(
                        file=uploads[0],
                        target_column=target_column,
                        analysis_mode=analysis_mode,
                        chart_types=chart_types,
                        model_selection_mode=model_selection_mode,
                        selected_models=selected_models,
                        automl_mode=automl_mode,
                        date_column=date_column,
                        price_column=price_column,
                        progress_callback=progress,
                        should_cancel=should_cancel,
                    )
                )
            return asyncio.run(
                run_uploaded_merged_agent_workflow(
                    files=uploads,
                    target_column=target_column,
                    analysis_mode=analysis_mode,
                    chart_types=chart_types,
                    model_selection_mode=model_selection_mode,
                    selected_models=selected_models,
                    automl_mode=automl_mode,
                    date_column=date_column,
                    price_column=price_column,
                    progress_callback=progress,
                    should_cancel=should_cancel,
                )
            )
        return governed_runner(
            run_type="agent_workflow_job",
            snapshots=snapshots,
            parameters=parameters,
            restore_uploads=_restore_uploads,
            execute=execute,
        )

    job = create_analysis_job("agents", runner)
    return AnalysisJobStartResponse(
        job_id=job.job_id,
        status=job.status,
        stage=job.stage,
    )


@app.post("/api/jobs/reports", response_model=AnalysisJobStartResponse)
async def start_report_generation_job(
    target_column: str = Form(...),
    analysis_mode: str = Form("auto"),
    chart_types: str = Form("auto"),
    model_selection_mode: str = Form("auto"),
    selected_models: str = Form("auto"),
    automl_mode: str = Form("quick"),
    date_column: str | None = Form(None),
    price_column: str | None = Form(None),
    files: list[UploadFile] = File(...),
) -> AnalysisJobStartResponse:
    snapshots = await _snapshot_uploads(files)
    parameters = {
        "target_column": target_column,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "model_selection_mode": model_selection_mode,
        "selected_models": selected_models,
        "automl_mode": automl_mode,
        "date_column": date_column,
        "price_column": price_column,
        "file_count": len(snapshots),
    }

    def runner(progress, should_cancel):
        def execute(uploads: list[UploadFile]) -> dict[str, Any]:
            if len(uploads) == 1:
                return asyncio.run(
                    generate_uploaded_report(
                        file=uploads[0],
                        target_column=target_column,
                        analysis_mode=analysis_mode,
                        chart_types=chart_types,
                        model_selection_mode=model_selection_mode,
                        selected_models=selected_models,
                        automl_mode=automl_mode,
                        date_column=date_column,
                        price_column=price_column,
                        progress_callback=progress,
                        should_cancel=should_cancel,
                    )
                )
            return asyncio.run(
                generate_uploaded_merged_report(
                    files=uploads,
                    target_column=target_column,
                    analysis_mode=analysis_mode,
                    chart_types=chart_types,
                    model_selection_mode=model_selection_mode,
                    selected_models=selected_models,
                    automl_mode=automl_mode,
                    date_column=date_column,
                    price_column=price_column,
                    progress_callback=progress,
                    should_cancel=should_cancel,
                )
            )
        return governed_runner(
            run_type="report_generation_job",
            snapshots=snapshots,
            parameters=parameters,
            restore_uploads=_restore_uploads,
            execute=execute,
        )

    job = create_analysis_job("reports", runner)
    return AnalysisJobStartResponse(
        job_id=job.job_id,
        status=job.status,
        stage=job.stage,
    )


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
    snapshots = await _snapshot_uploads([file])

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await analyze_uploaded_dataset(uploads[0])

    result = await governed_async_runner(
        run_type="dataset_profile",
        snapshots=snapshots,
        parameters={"file_count": 1},
        restore_uploads=_restore_uploads,
        execute=execute,
    )
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
    snapshots = await _snapshot_uploads(files)

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await analyze_multiple_uploaded_datasets(uploads)

    result = await governed_async_runner(
        run_type="multiple_dataset_profile",
        snapshots=snapshots,
        parameters={"file_count": len(snapshots), "merge_mode": "auto"},
        restore_uploads=_restore_uploads,
        execute=execute,
    )
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
    snapshots = await _snapshot_uploads([file])
    parameters = {
        "target_column": target_column,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "model_selection_mode": model_selection_mode,
        "selected_models": selected_models,
        "automl_mode": automl_mode,
    }

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await run_uploaded_model_analysis(
            file=uploads[0],
            target_column=target_column,
            analysis_mode=analysis_mode,
            chart_types=chart_types,
            model_selection_mode=model_selection_mode,
            selected_models=selected_models,
            automl_mode=automl_mode,
        )

    result = await governed_async_runner(
        run_type="model_analysis",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
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
    snapshots = await _snapshot_uploads(files)
    parameters = {
        "target_column": target_column,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "model_selection_mode": model_selection_mode,
        "selected_models": selected_models,
        "automl_mode": automl_mode,
        "file_count": len(snapshots),
    }

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await run_uploaded_merged_model_analysis(
            files=uploads,
            target_column=target_column,
            analysis_mode=analysis_mode,
            chart_types=chart_types,
            model_selection_mode=model_selection_mode,
            selected_models=selected_models,
            automl_mode=automl_mode,
        )

    result = await governed_async_runner(
        run_type="merged_model_analysis",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
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
    snapshots = await _snapshot_uploads([file])
    parameters = {
        "target_column": target_column,
        "model_name": model_name,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
    }

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await generate_uploaded_code_artifacts(
            file=uploads[0],
            target_column=target_column,
            model_name=model_name,
            analysis_mode=analysis_mode,
            chart_types=chart_types,
        )

    result = await governed_async_runner(
        run_type="code_generation",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
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
    snapshots = await _snapshot_uploads(files)
    parameters = {
        "target_column": target_column,
        "model_name": model_name,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "file_count": len(snapshots),
    }

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await generate_uploaded_merged_code_artifacts(
            files=uploads,
            target_column=target_column,
            model_name=model_name,
            analysis_mode=analysis_mode,
            chart_types=chart_types,
        )

    result = await governed_async_runner(
        run_type="merged_code_generation",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
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
    snapshots = await _snapshot_uploads([file])
    parameters = {"date_column": date_column, "price_column": price_column}

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await analyze_uploaded_financial_dataset(
            file=uploads[0],
            date_column=date_column,
            price_column=price_column,
        )

    result = await governed_async_runner(
        run_type="financial_analysis",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
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
    snapshots = await _snapshot_uploads(files)
    parameters = {
        "date_column": date_column,
        "price_column": price_column,
        "file_count": len(snapshots),
    }

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await analyze_uploaded_merged_financial_dataset(
            files=uploads,
            date_column=date_column,
            price_column=price_column,
        )

    result = await governed_async_runner(
        run_type="merged_financial_analysis",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
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
    snapshots = await _snapshot_uploads([file])
    parameters = {
        "target_column": target_column,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "model_selection_mode": model_selection_mode,
        "selected_models": selected_models,
        "automl_mode": automl_mode,
        "date_column": date_column,
        "price_column": price_column,
    }

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await run_uploaded_agent_workflow(
            file=uploads[0],
            target_column=target_column,
            analysis_mode=analysis_mode,
            chart_types=chart_types,
            model_selection_mode=model_selection_mode,
            selected_models=selected_models,
            automl_mode=automl_mode,
            date_column=date_column,
            price_column=price_column,
        )

    result = await governed_async_runner(
        run_type="agent_workflow",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
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
    snapshots = await _snapshot_uploads(files)
    parameters = {
        "target_column": target_column,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "model_selection_mode": model_selection_mode,
        "selected_models": selected_models,
        "automl_mode": automl_mode,
        "date_column": date_column,
        "price_column": price_column,
        "file_count": len(snapshots),
    }

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await run_uploaded_merged_agent_workflow(
            files=uploads,
            target_column=target_column,
            analysis_mode=analysis_mode,
            chart_types=chart_types,
            model_selection_mode=model_selection_mode,
            selected_models=selected_models,
            automl_mode=automl_mode,
            date_column=date_column,
            price_column=price_column,
        )

    result = await governed_async_runner(
        run_type="merged_agent_workflow",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
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
    snapshots = await _snapshot_uploads([file])
    parameters = {
        "target_column": target_column,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "model_selection_mode": model_selection_mode,
        "selected_models": selected_models,
        "automl_mode": automl_mode,
        "date_column": date_column,
        "price_column": price_column,
    }

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await generate_uploaded_report(
            file=uploads[0],
            target_column=target_column,
            analysis_mode=analysis_mode,
            chart_types=chart_types,
            model_selection_mode=model_selection_mode,
            selected_models=selected_models,
            automl_mode=automl_mode,
            date_column=date_column,
            price_column=price_column,
        )

    result = await governed_async_runner(
        run_type="report_generation",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
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
    snapshots = await _snapshot_uploads(files)
    parameters = {
        "target_column": target_column,
        "analysis_mode": analysis_mode,
        "chart_types": chart_types,
        "model_selection_mode": model_selection_mode,
        "selected_models": selected_models,
        "automl_mode": automl_mode,
        "date_column": date_column,
        "price_column": price_column,
        "file_count": len(snapshots),
    }

    async def execute(uploads: list[UploadFile]) -> dict[str, Any]:
        return await generate_uploaded_merged_report(
            files=uploads,
            target_column=target_column,
            analysis_mode=analysis_mode,
            chart_types=chart_types,
            model_selection_mode=model_selection_mode,
            selected_models=selected_models,
            automl_mode=automl_mode,
            date_column=date_column,
            price_column=price_column,
        )

    result = await governed_async_runner(
        run_type="merged_report_generation",
        snapshots=snapshots,
        parameters=parameters,
        restore_uploads=_restore_uploads,
        execute=execute,
    )
    return ReportResponse(**result)


async def _snapshot_uploads(
    files: list[UploadFile],
) -> list[tuple[str, bytes]]:
    validate_upload_batch(files)
    snapshots: list[tuple[str, bytes]] = []
    total_size = 0
    for file in files:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="上傳檔案是空的。")
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail="上傳檔案過大，最大限制為 25 MB。",
            )
        total_size += len(content)
        if total_size > MAX_BATCH_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail="單次上傳總容量不可超過 100 MB。",
            )
        snapshots.append((file.filename or "dataset.csv", content))
    return snapshots


def _restore_uploads(
    snapshots: list[tuple[str, bytes]],
) -> list[UploadFile]:
    return [
        UploadFile(
            file=BytesIO(content),
            filename=file_name,
            size=len(content),
        )
        for file_name, content in snapshots
    ]
