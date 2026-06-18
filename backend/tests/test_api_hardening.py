import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient

from app.main import app, get_cors_origins, unhandled_exception_handler
from app.services.dataset_analyzer import (
    MAX_BATCH_UPLOAD_BYTES,
    MAX_UPLOAD_FILES,
    validate_upload_batch,
)


def make_upload(name: str, size: int) -> UploadFile:
    return UploadFile(
        file=BytesIO(b"x"),
        filename=name,
        size=size,
    )


def test_upload_batch_rejects_too_many_files() -> None:
    files = [
        make_upload(f"dataset-{index}.csv", 1)
        for index in range(MAX_UPLOAD_FILES + 1)
    ]

    with pytest.raises(HTTPException) as exc_info:
        validate_upload_batch(files)

    assert exc_info.value.status_code == 413
    assert str(MAX_UPLOAD_FILES) in str(exc_info.value.detail)


def test_upload_batch_rejects_excessive_total_size() -> None:
    files = [
        make_upload("first.csv", MAX_BATCH_UPLOAD_BYTES // 2 + 1),
        make_upload("second.csv", MAX_BATCH_UPLOAD_BYTES // 2 + 1),
    ]

    with pytest.raises(HTTPException) as exc_info:
        validate_upload_batch(files)

    assert exc_info.value.status_code == 413
    assert "100 MB" in str(exc_info.value.detail)


def test_unhandled_exception_response_does_not_expose_internal_details() -> None:
    response = asyncio.run(
        unhandled_exception_handler(
            object(),
            RuntimeError("/private/app/secret.py database-password"),
        )
    )

    body = response.body.decode("utf-8")
    assert response.status_code == 500
    assert "secret.py" not in body
    assert "database-password" not in body
    assert "稍後再試" in body


def test_api_responses_include_security_headers() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"


def test_default_cors_origins_include_local_frontend_ports(monkeypatch) -> None:
    monkeypatch.delenv("FRONTEND_ORIGINS", raising=False)

    origins = get_cors_origins()

    assert "http://127.0.0.1:3012" in origins
    assert "http://localhost:3012" in origins
