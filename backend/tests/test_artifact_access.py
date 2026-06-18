import base64
import hashlib
import hmac
import importlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from urllib.parse import unquote

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app


def _artifact_access_module() -> ModuleType:
    spec = importlib.util.find_spec("app.services.artifact_access")
    assert spec is not None, "artifact access service is not implemented"
    return importlib.import_module("app.services.artifact_access")


def _token_from_url(url: str) -> str:
    prefix = "/api/artifacts/"
    assert url.startswith(prefix)
    return unquote(url.removeprefix(prefix))


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _sign_payload(payload: dict[str, object], secret: str) -> str:
    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    signature = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).digest()
    return f"{_encode(payload_bytes)}.{_encode(signature)}"


def test_artifact_token_resolves_file_and_supports_epoch_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_access = _artifact_access_module()
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "unit-test-secret")
    artifact = tmp_path / "reports" / "summary.csv"
    artifact.parent.mkdir()
    artifact.write_text("metric,value\nr2,0.91\n", encoding="utf-8")

    url = artifact_access.create_artifact_url(
        artifact,
        root=tmp_path,
        now=0,
        ttl_seconds=10,
    )
    resolved = artifact_access.resolve_artifact_token(
        _token_from_url(url),
        root=tmp_path,
        now=0,
    )

    assert resolved == artifact.resolve()
    assert "%2E" in url


def test_artifact_token_rejects_tampering(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_access = _artifact_access_module()
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "unit-test-secret")
    artifact = tmp_path / "chart.png"
    artifact.write_bytes(b"png")
    token = _token_from_url(
        artifact_access.create_artifact_url(artifact, root=tmp_path)
    )
    payload, signature = token.split(".", maxsplit=1)
    replacement = "A" if signature[0] != "A" else "B"
    tampered = f"{payload}.{replacement}{signature[1:]}"

    with pytest.raises(HTTPException) as exc_info:
        artifact_access.resolve_artifact_token(tampered, root=tmp_path)

    assert exc_info.value.status_code == 403


def test_artifact_token_rejects_noncanonical_base64_tampering(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_access = _artifact_access_module()
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "unit-test-secret")
    artifact = tmp_path / "chart.png"
    artifact.write_bytes(b"png")
    token = _token_from_url(
        artifact_access.create_artifact_url(artifact, root=tmp_path)
    )
    payload, signature = token.split(".", maxsplit=1)
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    final_index = alphabet.index(signature[-1])
    noncanonical_signature = f"{signature[:-1]}{alphabet[final_index + 1]}"

    with pytest.raises(HTTPException) as exc_info:
        artifact_access.resolve_artifact_token(
            f"{payload}.{noncanonical_signature}",
            root=tmp_path,
        )

    assert exc_info.value.status_code == 403


def test_artifact_token_rejects_expired_token(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_access = _artifact_access_module()
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "unit-test-secret")
    artifact = tmp_path / "report.docx"
    artifact.write_bytes(b"docx")
    token = _token_from_url(
        artifact_access.create_artifact_url(
            artifact,
            root=tmp_path,
            now=0,
            ttl_seconds=10,
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        artifact_access.resolve_artifact_token(token, root=tmp_path, now=11)

    assert exc_info.value.status_code == 410


def test_artifact_token_rejects_path_escape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_access = _artifact_access_module()
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "unit-test-secret")
    token = _sign_payload(
        {"exp": 10, "path": "../outside.csv"},
        "unit-test-secret",
    )

    with pytest.raises(HTTPException) as exc_info:
        artifact_access.resolve_artifact_token(token, root=tmp_path, now=0)

    assert exc_info.value.status_code == 403


@pytest.mark.parametrize("relative_path", ["missing.csv", "folder"])
def test_artifact_token_rejects_missing_or_non_file(
    relative_path: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_access = _artifact_access_module()
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "unit-test-secret")
    if relative_path == "folder":
        (tmp_path / relative_path).mkdir()
    token = _token_from_url(
        artifact_access.create_artifact_url(
            tmp_path / relative_path,
            root=tmp_path,
            now=0,
            ttl_seconds=10,
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        artifact_access.resolve_artifact_token(token, root=tmp_path, now=0)

    assert exc_info.value.status_code == 404


def test_artifact_secret_reads_environment_without_module_reload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_access = _artifact_access_module()
    artifact = tmp_path / "result.csv"
    artifact.write_text("value\n1\n", encoding="utf-8")
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "first-secret")
    token = _token_from_url(
        artifact_access.create_artifact_url(artifact, root=tmp_path)
    )
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "second-secret")

    with pytest.raises(HTTPException) as exc_info:
        artifact_access.resolve_artifact_token(token, root=tmp_path)

    assert exc_info.value.status_code == 403
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "first-secret")
    assert artifact_access.resolve_artifact_token(token, root=tmp_path) == artifact.resolve()


def test_artifact_image_endpoint_is_inline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_access = _artifact_access_module()
    main_module = importlib.import_module("app.main")
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "endpoint-secret")
    monkeypatch.setattr(main_module, "GENERATED_OUTPUTS_DIR", tmp_path)
    image_path = tmp_path / "charts" / "result.png"
    image_path.parent.mkdir()
    image_path.write_bytes(b"\x89PNG\r\n\x1a\n")
    url = artifact_access.create_artifact_url(image_path, root=tmp_path)

    response = TestClient(app).get(url)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["content-disposition"].startswith("inline;")
    assert 'filename="result.png"' in response.headers["content-disposition"]
    assert response.headers["cache-control"] == "private, no-store"


@pytest.mark.parametrize(
    ("file_name", "content"),
    [
        ("indicators.csv", b"date,price\n2026-01-01,100\n"),
        ("trained.joblib", b"model"),
        ("analysis.docx", b"report"),
    ],
)
def test_artifact_download_endpoint_uses_attachment(
    file_name: str,
    content: bytes,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_access = _artifact_access_module()
    main_module = importlib.import_module("app.main")
    monkeypatch.setenv("ARTIFACT_SIGNING_SECRET", "endpoint-secret")
    monkeypatch.setattr(main_module, "GENERATED_OUTPUTS_DIR", tmp_path)
    artifact = tmp_path / file_name
    artifact.write_bytes(content)
    url = artifact_access.create_artifact_url(artifact, root=tmp_path)

    response = TestClient(app).get(url)

    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment;")
    assert f'filename="{file_name}"' in response.headers["content-disposition"]
    assert response.headers["cache-control"] == "private, no-store"


def test_artifact_endpoint_rejects_invalid_token() -> None:
    response = TestClient(app).get("/api/artifacts/not-a-valid-token")

    assert response.status_code == 403
    assert response.headers["cache-control"] == "private, no-store"


def test_generated_outputs_are_not_publicly_mounted() -> None:
    response = TestClient(app).get("/generated_outputs/README.md")

    assert response.status_code == 404
