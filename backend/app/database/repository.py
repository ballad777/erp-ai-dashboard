from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from app.database.connection import connect, initialize_database


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    return json.loads(value)


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@contextmanager
def database() -> Iterator[Any]:
    initialize_database()
    with connect() as connection:
        yield connection


@dataclass(frozen=True)
class IdentityContext:
    user_id: str
    project_id: str
    email: str
    project_name: str


def ensure_demo_identity(
    *,
    email: str = "demo@datapilot.local",
    display_name: str = "Demo User",
    project_name: str = "預設分析專案",
) -> IdentityContext:
    user_id = f"user_{hash_text(email)[:24]}"
    project_id = f"project_{hash_text(f'{email}:{project_name}')[:24]}"
    timestamp = now_iso()

    with database() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO users (id, email, display_name, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, email, display_name, timestamp),
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO projects (id, user_id, name, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, user_id, project_name, timestamp),
        )
    return IdentityContext(
        user_id=user_id,
        project_id=project_id,
        email=email,
        project_name=project_name,
    )


def create_dataset_record(
    *,
    project_id: str,
    file_name: str,
    content_hash: str,
    schema_fingerprint: str,
    row_count: int,
    column_count: int,
    profile: dict[str, Any],
    quality_report: dict[str, Any],
) -> str:
    dataset_id = new_id("dataset")
    with database() as connection:
        connection.execute(
            """
            INSERT INTO datasets (
                id, project_id, file_name, content_hash, schema_fingerprint,
                row_count, column_count, profile_json, quality_report_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_id,
                project_id,
                file_name,
                content_hash,
                schema_fingerprint,
                row_count,
                column_count,
                stable_json(profile),
                stable_json(quality_report),
                now_iso(),
            ),
        )
    return dataset_id


def create_analysis_run(
    *,
    project_id: str,
    run_type: str,
    parameters: dict[str, Any],
    dataset_id: str | None = None,
) -> str:
    run_id = new_id("run")
    timestamp = now_iso()
    with database() as connection:
        connection.execute(
            """
            INSERT INTO analysis_runs (
                id, project_id, dataset_id, run_type, status,
                parameters_json, manifest_json, created_at, started_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                project_id,
                dataset_id,
                run_type,
                "running",
                stable_json(parameters),
                stable_json({}),
                timestamp,
                timestamp,
            ),
        )
    return run_id


def complete_analysis_run(
    *,
    run_id: str,
    dataset_id: str | None,
    manifest: dict[str, Any],
) -> None:
    with database() as connection:
        connection.execute(
            """
            UPDATE analysis_runs
            SET status = ?, dataset_id = ?, manifest_json = ?, finished_at = ?
            WHERE id = ?
            """,
            ("completed", dataset_id, stable_json(manifest), now_iso(), run_id),
        )


def fail_analysis_run(*, run_id: str, error: str) -> None:
    with database() as connection:
        connection.execute(
            """
            UPDATE analysis_runs
            SET status = ?, error = ?, finished_at = ?
            WHERE id = ?
            """,
            ("failed", error, now_iso(), run_id),
        )


def create_or_update_job_record(
    *,
    job_id: str,
    kind: str,
    status: str,
    stage: str,
    message: str,
    created_at: float,
    project_id: str | None = None,
    run_id: str | None = None,
    completed_items: int | None = None,
    total_items: int | None = None,
    started_at: float | None = None,
    finished_at: float | None = None,
    cancel_requested: bool = False,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    with database() as connection:
        connection.execute(
            """
            INSERT INTO analysis_jobs (
                id, project_id, run_id, kind, status, stage, message,
                completed_items, total_items, result_json, error, cancel_requested,
                created_at, started_at, finished_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                project_id = excluded.project_id,
                run_id = COALESCE(excluded.run_id, analysis_jobs.run_id),
                status = excluded.status,
                stage = excluded.stage,
                message = excluded.message,
                completed_items = excluded.completed_items,
                total_items = excluded.total_items,
                result_json = excluded.result_json,
                error = excluded.error,
                cancel_requested = excluded.cancel_requested,
                started_at = excluded.started_at,
                finished_at = excluded.finished_at
            """,
            (
                job_id,
                project_id,
                run_id,
                kind,
                status,
                stage,
                message,
                completed_items,
                total_items,
                stable_json(result) if result is not None else None,
                error,
                1 if cancel_requested else 0,
                created_at,
                started_at,
                finished_at,
            ),
        )


def get_job_record(job_id: str) -> dict[str, Any] | None:
    with database() as connection:
        row = connection.execute(
            "SELECT * FROM analysis_jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
    if row is None:
        return None
    payload = dict(row)
    payload["cancel_requested"] = bool(payload["cancel_requested"])
    payload["result"] = load_json(payload.pop("result_json"), None)
    return payload


def mark_job_cancel_requested(job_id: str) -> None:
    with database() as connection:
        connection.execute(
            "UPDATE analysis_jobs SET cancel_requested = 1 WHERE id = ?",
            (job_id,),
        )


def register_artifact(
    *,
    project_id: str,
    run_id: str,
    relative_path: str,
    artifact_type: str,
    expires_at: int,
    content_type: str | None = None,
) -> str:
    artifact_id = new_id("artifact")
    timestamp = now_iso()
    with database() as connection:
        existing = connection.execute(
            """
            SELECT id FROM artifacts
            WHERE run_id = ? AND relative_path = ?
            """,
            (run_id, relative_path),
        ).fetchone()
        if existing:
            artifact_id = str(existing["id"])
            connection.execute(
                """
                UPDATE artifacts
                SET expires_at = ?, content_type = ?, revoked_at = NULL
                WHERE id = ?
                """,
                (expires_at, content_type, artifact_id),
            )
        else:
            connection.execute(
                """
                INSERT INTO artifacts (
                    id, project_id, run_id, artifact_type, relative_path,
                    content_type, expires_at, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    project_id,
                    run_id,
                    artifact_type,
                    relative_path,
                    content_type,
                    expires_at,
                    timestamp,
                ),
            )
    return artifact_id


def validate_artifact_record(
    *,
    artifact_id: str,
    run_id: str | None,
    project_id: str | None,
    relative_path: str,
    now_epoch: int,
) -> None:
    with database() as connection:
        row = connection.execute(
            "SELECT * FROM artifacts WHERE id = ?",
            (artifact_id,),
        ).fetchone()
    if row is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Artifact is not registered.")
    if row["revoked_at"]:
        from fastapi import HTTPException

        raise HTTPException(status_code=410, detail="Artifact has been revoked.")
    if int(row["expires_at"]) <= now_epoch:
        from fastapi import HTTPException

        raise HTTPException(status_code=410, detail="Artifact URL has expired.")
    if row["relative_path"] != relative_path:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Artifact path does not match token.")
    if run_id and row["run_id"] != run_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Artifact run does not match token.")
    if project_id and row["project_id"] != project_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Artifact project does not match token.")


def create_model_result_records(
    *,
    run_id: str,
    model_results: list[dict[str, Any]],
) -> None:
    with database() as connection:
        connection.execute("DELETE FROM model_results WHERE run_id = ?", (run_id,))
        for index, result in enumerate(model_results, start=1):
            connection.execute(
                """
                INSERT INTO model_results (
                    id, run_id, model_key, model_name, rank,
                    metrics_json, artifact_path, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_id("model_result"),
                    run_id,
                    str(result.get("model_key") or result.get("model_name") or "unknown"),
                    str(result.get("model_name") or result.get("model_key") or "Unknown"),
                    index,
                    stable_json(
                        {
                            key: value
                            for key, value in result.items()
                            if key
                            in {
                                "r2",
                                "rmse",
                                "mae",
                                "accuracy",
                                "f1_score",
                                "training_time_seconds",
                                "automl_best_params",
                            }
                        }
                    ),
                    result.get("model_path"),
                    now_iso(),
                ),
            )


def write_audit_log(
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    user_id: str | None = None,
    project_id: str | None = None,
    run_id: str | None = None,
    artifact_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    with database() as connection:
        connection.execute(
            """
            INSERT INTO audit_logs (
                id, user_id, project_id, run_id, artifact_id, action,
                resource_type, resource_id, metadata_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id("audit"),
                user_id,
                project_id,
                run_id,
                artifact_id,
                action,
                resource_type,
                resource_id,
                stable_json(metadata or {}),
                now_iso(),
            ),
        )


def revoke_artifacts_for_run(run_id: str) -> int:
    timestamp = now_iso()
    with database() as connection:
        cursor = connection.execute(
            """
            UPDATE artifacts
            SET revoked_at = ?
            WHERE run_id = ? AND revoked_at IS NULL
            """,
            (timestamp, run_id),
        )
        return int(cursor.rowcount or 0)


def artifact_type_from_path(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
        return "chart"
    if suffix in {".py", ".ipynb"}:
        return "code"
    if suffix in {".docx", ".pdf", ".html"}:
        return "report"
    if suffix in {".joblib", ".pkl"}:
        return "model"
    if suffix in {".csv", ".xlsx"}:
        return "data"
    return "artifact"
