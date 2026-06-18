from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any, NoReturn

from fastapi import HTTPException

from app.database import repository
from app.services.run_governance import current_artifact_context

ARTIFACT_TTL_SECONDS = 4 * 60 * 60
_PROCESS_LOCAL_SECRET = secrets.token_bytes(32)


def create_artifact_url(
    path: str | Path,
    *,
    root: str | Path,
    now: float | None = None,
    ttl_seconds: int = ARTIFACT_TTL_SECONDS,
) -> str:
    root_path = Path(root).resolve()
    artifact_path = Path(path)
    if not artifact_path.is_absolute():
        artifact_path = root_path / artifact_path
    relative_path = _relative_artifact_path(artifact_path, root_path)
    current_time = time.time() if now is None else now
    expires_at = int(current_time + ttl_seconds)
    payload = {
        "exp": expires_at,
        "path": relative_path.as_posix(),
    }
    context = current_artifact_context()
    if context is not None:
        artifact_id = repository.register_artifact(
            project_id=context.project_id,
            run_id=context.run_id,
            relative_path=relative_path.as_posix(),
            artifact_type=repository.artifact_type_from_path(relative_path),
            expires_at=expires_at,
        )
        payload.update(
            {
                "artifact_id": artifact_id,
                "project_id": context.project_id,
                "run_id": context.run_id,
                "user_id": context.user_id,
            }
        )
    payload_bytes = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    signature = hmac.new(
        _signing_secret(),
        payload_bytes,
        hashlib.sha256,
    ).digest()
    token = f"{_encode(payload_bytes)}.{_encode(signature)}"
    return f"/api/artifacts/{token}"


def resolve_artifact_token(
    token: str,
    *,
    root: str | Path,
    now: float | None = None,
) -> Path:
    try:
        payload_part, signature_part = token.split(".", maxsplit=1)
        payload_bytes = _decode(payload_part)
        supplied_signature = _decode(signature_part)
    except (TypeError, ValueError):
        _invalid_token()

    expected_signature = hmac.new(
        _signing_secret(),
        payload_bytes,
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(expected_signature, supplied_signature):
        _invalid_token()

    try:
        payload: Any = json.loads(payload_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError):
        _invalid_token()

    if not isinstance(payload, dict):
        _invalid_token()
    relative_path = payload.get("path")
    expires_at = payload.get("exp")
    if (
        not isinstance(relative_path, str)
        or not relative_path
        or not isinstance(expires_at, int)
        or isinstance(expires_at, bool)
    ):
        _invalid_token()

    current_time = time.time() if now is None else now
    if current_time >= expires_at:
        raise HTTPException(status_code=410, detail="Artifact URL has expired.")

    artifact_id = payload.get("artifact_id")
    if artifact_id is not None:
        if not isinstance(artifact_id, str) or not artifact_id:
            _invalid_token()
        run_id = payload.get("run_id")
        project_id = payload.get("project_id")
        if run_id is not None and not isinstance(run_id, str):
            _invalid_token()
        if project_id is not None and not isinstance(project_id, str):
            _invalid_token()
        repository.validate_artifact_record(
            artifact_id=artifact_id,
            run_id=run_id,
            project_id=project_id,
            relative_path=relative_path,
            now_epoch=int(current_time),
        )
        repository.write_audit_log(
            action="download",
            resource_type="artifact",
            resource_id=artifact_id,
            user_id=payload.get("user_id") if isinstance(payload.get("user_id"), str) else None,
            project_id=project_id,
            run_id=run_id,
            artifact_id=artifact_id,
            metadata={"path": relative_path},
        )

    root_path = Path(root).resolve()
    artifact_path = root_path / relative_path
    resolved_path = _resolve_within_root(artifact_path, root_path)
    if not resolved_path.is_file():
        raise HTTPException(status_code=404, detail="Artifact not found.")
    return resolved_path


def _relative_artifact_path(path: Path, root: Path) -> Path:
    resolved_path = _resolve_within_root(path, root)
    return resolved_path.relative_to(root)


def _resolve_within_root(path: Path, root: Path) -> Path:
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(root)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Artifact path is not allowed.",
        ) from None
    return resolved_path


def _signing_secret() -> bytes:
    configured_secret = os.getenv("ARTIFACT_SIGNING_SECRET")
    if configured_secret:
        return configured_secret.encode("utf-8")
    return _PROCESS_LOCAL_SECRET


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    if not value:
        raise ValueError("empty base64 value")
    padding = "=" * (-len(value) % 4)
    decoded = base64.b64decode(
        value + padding,
        altchars=b"-_",
        validate=True,
    )
    if _encode(decoded) != value:
        raise ValueError("noncanonical base64 value")
    return decoded


def _invalid_token() -> NoReturn:
    raise HTTPException(status_code=403, detail="Invalid artifact token.")
