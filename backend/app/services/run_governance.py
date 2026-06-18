from __future__ import annotations

import hashlib
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import Any, Callable, Iterator

from fastapi import UploadFile

from app.database import repository


@dataclass(frozen=True)
class ArtifactContext:
    user_id: str
    project_id: str
    run_id: str


_artifact_context: ContextVar[ArtifactContext | None] = ContextVar(
    "artifact_context",
    default=None,
)


def current_artifact_context() -> ArtifactContext | None:
    return _artifact_context.get()


@contextmanager
def artifact_context(context: ArtifactContext) -> Iterator[None]:
    token = _artifact_context.set(context)
    try:
        yield
    finally:
        _artifact_context.reset(token)


def hash_uploads(snapshots: list[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for file_name, content in snapshots:
        digest.update(file_name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(content).hexdigest().encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def dataset_hash_for_content(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def schema_fingerprint(profile: dict[str, Any]) -> str:
    schema_payload = {
        "columns": profile.get("columns", []),
        "data_types": profile.get("data_types", {}),
        "row_count": profile.get("row_count"),
        "column_count": profile.get("column_count"),
    }
    return repository.hash_text(repository.stable_json(schema_payload))


def build_run_manifest(
    *,
    run_id: str,
    run_type: str,
    project_id: str,
    dataset_id: str | None,
    parameters: dict[str, Any],
    snapshots: list[tuple[str, bytes]],
    result: dict[str, Any],
    started_epoch: float,
) -> dict[str, Any]:
    artifact_urls = _collect_artifact_urls(result)
    model_results = result.get("model_results")
    return {
        "manifest_version": "2026-06-17.1",
        "run_id": run_id,
        "run_type": run_type,
        "project_id": project_id,
        "dataset_id": dataset_id,
        "created_at_epoch": round(started_epoch, 6),
        "finished_at_epoch": round(time(), 6),
        "duration_seconds": round(time() - started_epoch, 4),
        "input_files": [
            {
                "file_name": file_name,
                "size_bytes": len(content),
                "sha256": dataset_hash_for_content(content),
            }
            for file_name, content in snapshots
        ],
        "combined_input_hash": hash_uploads(snapshots),
        "parameters": parameters,
        "analysis": {
            "file_name": result.get("file_name"),
            "target_column": result.get("target_column"),
            "analysis_mode": result.get("analysis_mode"),
            "problem_type": result.get("problem_type"),
            "row_count_used": result.get("row_count_used") or result.get("row_count"),
            "feature_count_used": result.get("feature_count_used"),
        },
        "models": model_results if isinstance(model_results, list) else [],
        "artifacts": artifact_urls,
        "notes": result.get("notes", []),
    }


def persist_dataset_from_result(
    *,
    project_id: str,
    snapshots: list[tuple[str, bytes]],
    result: dict[str, Any],
) -> str | None:
    profile = _extract_dataset_profile(result)
    if not profile:
        profile = {
            "file_name": result.get("file_name")
            or (snapshots[0][0] if len(snapshots) == 1 else "merged_dataset"),
            "row_count": int(result.get("row_count_used") or result.get("row_count") or 0),
            "column_count": int(
                result.get("feature_count_used") or result.get("column_count") or 0
            ),
            "columns": [],
            "data_types": {},
            "missing_values": {},
            "numeric_summary": {},
            "input_files": [
                {"file_name": file_name, "size_bytes": len(content)}
                for file_name, content in snapshots
            ],
        }

    if len(snapshots) == 1:
        file_name, content = snapshots[0]
        content_hash = dataset_hash_for_content(content)
    else:
        file_name = str(profile.get("file_name") or "merged_dataset")
        content_hash = hash_uploads(snapshots)

    quality_report = profile.get("quality_report")
    if not isinstance(quality_report, dict):
        quality_report = {}

    return repository.create_dataset_record(
        project_id=project_id,
        file_name=str(profile.get("file_name") or file_name),
        content_hash=content_hash,
        schema_fingerprint=str(
            profile.get("schema_fingerprint") or schema_fingerprint(profile)
        ),
        row_count=int(profile.get("row_count") or 0),
        column_count=int(profile.get("column_count") or 0),
        profile=profile,
        quality_report=quality_report,
    )


def finalize_governed_result(
    *,
    run_id: str,
    run_type: str,
    project_id: str,
    snapshots: list[tuple[str, bytes]],
    parameters: dict[str, Any],
    result: dict[str, Any],
    started_epoch: float,
) -> dict[str, Any]:
    dataset_id = persist_dataset_from_result(
        project_id=project_id,
        snapshots=snapshots,
        result=result,
    )
    if isinstance(result.get("model_results"), list):
        repository.create_model_result_records(
            run_id=run_id,
            model_results=result["model_results"],
        )
    manifest = build_run_manifest(
        run_id=run_id,
        run_type=run_type,
        project_id=project_id,
        dataset_id=dataset_id,
        parameters=parameters,
        snapshots=snapshots,
        result=result,
        started_epoch=started_epoch,
    )
    repository.complete_analysis_run(
        run_id=run_id,
        dataset_id=dataset_id,
        manifest=manifest,
    )
    repository.write_audit_log(
        action="complete",
        resource_type="analysis_run",
        resource_id=run_id,
        project_id=project_id,
        run_id=run_id,
        metadata={"run_type": run_type},
    )
    enriched = dict(result)
    enriched["run_id"] = run_id
    enriched["dataset_id"] = dataset_id
    enriched["run_manifest"] = manifest
    return enriched


def governed_runner(
    *,
    run_type: str,
    snapshots: list[tuple[str, bytes]],
    parameters: dict[str, Any],
    restore_uploads: Callable[[list[tuple[str, bytes]]], list[UploadFile]],
    execute: Callable[[list[UploadFile]], dict[str, Any]],
) -> dict[str, Any]:
    identity = repository.ensure_demo_identity()
    run_id = repository.create_analysis_run(
        project_id=identity.project_id,
        run_type=run_type,
        parameters=parameters,
    )
    started = time()
    context = ArtifactContext(
        user_id=identity.user_id,
        project_id=identity.project_id,
        run_id=run_id,
    )
    try:
        with artifact_context(context):
            result = execute(restore_uploads(snapshots))
        return finalize_governed_result(
            run_id=run_id,
            run_type=run_type,
            project_id=identity.project_id,
            snapshots=snapshots,
            parameters=parameters,
            result=result,
            started_epoch=started,
        )
    except Exception as exc:
        repository.fail_analysis_run(run_id=run_id, error=str(exc))
        repository.write_audit_log(
            action="fail",
            resource_type="analysis_run",
            resource_id=run_id,
            project_id=identity.project_id,
            run_id=run_id,
            metadata={"run_type": run_type, "error": str(exc)},
        )
        raise


async def governed_async_runner(
    *,
    run_type: str,
    snapshots: list[tuple[str, bytes]],
    parameters: dict[str, Any],
    restore_uploads: Callable[[list[tuple[str, bytes]]], list[UploadFile]],
    execute: Callable[[list[UploadFile]], Any],
) -> dict[str, Any]:
    identity = repository.ensure_demo_identity()
    run_id = repository.create_analysis_run(
        project_id=identity.project_id,
        run_type=run_type,
        parameters=parameters,
    )
    started = time()
    context = ArtifactContext(
        user_id=identity.user_id,
        project_id=identity.project_id,
        run_id=run_id,
    )
    try:
        with artifact_context(context):
            result = await execute(restore_uploads(snapshots))
        return finalize_governed_result(
            run_id=run_id,
            run_type=run_type,
            project_id=identity.project_id,
            snapshots=snapshots,
            parameters=parameters,
            result=result,
            started_epoch=started,
        )
    except Exception as exc:
        repository.fail_analysis_run(run_id=run_id, error=str(exc))
        repository.write_audit_log(
            action="fail",
            resource_type="analysis_run",
            resource_id=run_id,
            project_id=identity.project_id,
            run_id=run_id,
            metadata={"run_type": run_type, "error": str(exc)},
        )
        raise


def _extract_dataset_profile(result: dict[str, Any]) -> dict[str, Any] | None:
    direct_keys = {
        "file_name",
        "row_count",
        "column_count",
        "columns",
        "data_types",
        "missing_values",
        "numeric_summary",
    }
    if direct_keys.issubset(result.keys()):
        return {
            key: result[key]
            for key in result.keys()
            if key
            in {
                *direct_keys,
                "recommended_target_columns",
                "quality_report",
                "schema_fingerprint",
                "analysis_time_seconds",
                "merge_strategy",
                "merge_notes",
                "merge_plan",
                "common_columns",
                "source_files",
                "source_row_counts",
            }
        }

    merged = result.get("merged")
    if isinstance(merged, dict) and direct_keys.intersection(merged):
        return dict(merged)

    dataset_summary = result.get("dataset_summary")
    if isinstance(dataset_summary, dict) and direct_keys.intersection(dataset_summary):
        return dict(dataset_summary)

    workflow = result.get("workflow")
    if isinstance(workflow, dict):
        nested = workflow.get("dataset_summary")
        if isinstance(nested, dict):
            return dict(nested)

    return None


def _collect_artifact_urls(value: Any) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []

    def visit(node: Any, path: str) -> None:
        if isinstance(node, dict):
            url = node.get("chart_url") or node.get("model_url")
            file_path = node.get("chart_path") or node.get("model_path")
            if isinstance(url, str) and url.startswith("/api/artifacts/"):
                artifacts.append(
                    {
                        "kind": Path(str(file_path or "")).suffix.lstrip(".") or "artifact",
                        "path": file_path,
                        "url": url,
                        "source": path,
                    }
                )
            for key, child in node.items():
                if key.endswith("_url") and isinstance(child, str) and child.startswith(
                    "/api/artifacts/"
                ):
                    sibling_path = node.get(key.removesuffix("_url") + "_path")
                    artifacts.append(
                        {
                            "kind": key.removesuffix("_url"),
                            "path": sibling_path,
                            "url": child,
                            "source": f"{path}.{key}",
                        }
                    )
                else:
                    visit(child, f"{path}.{key}")
        elif isinstance(node, list):
            for index, child in enumerate(node):
                visit(child, f"{path}[{index}]")

    visit(value, "result")
    deduped: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        url = str(artifact.get("url"))
        deduped[url] = artifact
    return list(deduped.values())
