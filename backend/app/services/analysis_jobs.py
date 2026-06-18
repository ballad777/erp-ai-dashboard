from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass
from threading import RLock
from time import time
from typing import Any
from uuid import uuid4

from fastapi import HTTPException

from app.database import repository
from app.services.analysis_progress import AnalysisCancelledError, ProgressCallback

JobRunner = Callable[[ProgressCallback, Callable[[], bool]], dict[str, Any]]
logger = logging.getLogger(__name__)


@dataclass
class AnalysisJob:
    job_id: str
    kind: str
    status: str
    stage: str
    message: str
    completed_items: int | None
    total_items: int | None
    created_at: float
    started_at: float | None = None
    finished_at: float | None = None
    cancel_requested: bool = False
    result: dict[str, Any] | None = None
    error: str | None = None


_jobs: dict[str, AnalysisJob] = {}
_lock = RLock()
_job_ttl_seconds = 4 * 60 * 60


def create_analysis_job(kind: str, runner: JobRunner) -> AnalysisJob:
    _cleanup_jobs()
    job = AnalysisJob(
        job_id=uuid4().hex,
        kind=kind,
        status="queued",
        stage="queued",
        message="分析工作已排入佇列。",
        completed_items=None,
        total_items=None,
        created_at=time(),
    )
    with _lock:
        _jobs[job.job_id] = job
    repository.create_or_update_job_record(**asdict(job))
    asyncio.create_task(asyncio.to_thread(_execute_job, job.job_id, runner))
    return job


def get_analysis_job(job_id: str) -> dict[str, Any]:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            record = repository.get_job_record(job_id)
            if record is None:
                raise HTTPException(status_code=404, detail="找不到指定的分析工作。")
            return _job_payload_from_record(record)
        payload = asdict(job)

    started_at = job.started_at
    finished_at = job.finished_at
    payload["elapsed_seconds"] = round(
        max(0.0, (finished_at or time()) - (started_at or job.created_at)),
        2,
    )
    return payload


def cancel_analysis_job(job_id: str) -> dict[str, Any]:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="找不到指定的分析工作。")
        if job.status in {"completed", "failed", "cancelled"}:
            return get_analysis_job(job_id)
        job.cancel_requested = True
        job.message = "已收到取消要求，會在目前步驟結束後停止。"
        repository.mark_job_cancel_requested(job_id)
        repository.create_or_update_job_record(**asdict(job))
    return get_analysis_job(job_id)


def _execute_job(job_id: str, runner: JobRunner) -> None:
    _update_job(
        job_id,
        status="running",
        stage="reading_data",
        message="正在讀取資料。",
        started_at=time(),
    )

    def progress(
        stage: str,
        message: str,
        completed: int | None = None,
        total: int | None = None,
    ) -> None:
        _update_job(
            job_id,
            stage=stage,
            message=message,
            completed_items=completed,
            total_items=total,
        )

    def should_cancel() -> bool:
        with _lock:
            job = _jobs.get(job_id)
            return bool(job and job.cancel_requested)

    try:
        result = runner(progress, should_cancel)
        if should_cancel():
            raise AnalysisCancelledError("分析已由使用者取消。")
        _update_job(
            job_id,
            status="completed",
            stage="completed",
            message="分析完成。",
            result=result,
            finished_at=time(),
        )
    except AnalysisCancelledError:
        _update_job(
            job_id,
            status="cancelled",
            stage="cancelled",
            message="分析已取消。",
            finished_at=time(),
        )
    except HTTPException as exc:
        _update_job(
            job_id,
            status="failed",
            stage="failed",
            message="分析無法完成。",
            error=str(exc.detail),
            finished_at=time(),
        )
    except Exception:
        logger.exception("Analysis job %s failed", job_id)
        _update_job(
            job_id,
            status="failed",
            stage="failed",
            message="分析服務暫時無法完成工作。",
            error="伺服器暫時無法完成分析，請稍後再試。",
            finished_at=time(),
        )


def _update_job(job_id: str, **changes: Any) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        for key, value in changes.items():
            setattr(job, key, value)
        repository.create_or_update_job_record(**asdict(job))


def _cleanup_jobs() -> None:
    cutoff = time() - _job_ttl_seconds
    with _lock:
        expired = [
            job_id
            for job_id, job in _jobs.items()
            if (job.finished_at or job.created_at) < cutoff
        ]
        for job_id in expired:
            _jobs.pop(job_id, None)


def _job_payload_from_record(record: dict[str, Any]) -> dict[str, Any]:
    started_at = record.get("started_at")
    finished_at = record.get("finished_at")
    created_at = record.get("created_at") or time()
    payload = {
        "job_id": record["id"],
        "kind": record["kind"],
        "status": record["status"],
        "stage": record["stage"],
        "message": record["message"],
        "completed_items": record.get("completed_items"),
        "total_items": record.get("total_items"),
        "created_at": created_at,
        "started_at": started_at,
        "finished_at": finished_at,
        "cancel_requested": bool(record.get("cancel_requested")),
        "result": record.get("result"),
        "error": record.get("error"),
        "elapsed_seconds": round(
            max(0.0, (finished_at or time()) - (started_at or created_at)),
            2,
        ),
    }
    return payload
