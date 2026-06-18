from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from threading import RLock

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SQLITE_PATH = REPO_ROOT / ".local" / "finai.sqlite3"

_INIT_LOCK = RLock()
_INITIALIZED_DATABASES: set[str] = set()


def database_url() -> str:
    configured = os.getenv("DATABASE_URL", "").strip()
    if configured:
        return configured
    return f"sqlite:///{DEFAULT_SQLITE_PATH}"


def is_sqlite_url(url: str | None = None) -> bool:
    selected_url = url or database_url()
    return selected_url.startswith("sqlite:///")


def sqlite_path(url: str | None = None) -> Path:
    selected_url = url or database_url()
    if selected_url == "sqlite:///:memory:":
        return Path(":memory:")
    if not selected_url.startswith("sqlite:///"):
        raise RuntimeError(
            "目前本機執行層使用 sqlite3。正式 PostgreSQL 請依 backend/database/postgres_schema.sql 建立 schema，"
            "並在部署層接上 PostgreSQL repository/driver。"
        )
    return Path(selected_url.removeprefix("sqlite:///")).expanduser().resolve()


def connect() -> sqlite3.Connection:
    path = sqlite_path()
    if path != Path(":memory:"):
        path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def initialize_database() -> None:
    url = database_url()
    with _INIT_LOCK:
        if url in _INITIALIZED_DATABASES:
            return
        if not is_sqlite_url(url):
            return
        with connect() as connection:
            connection.executescript(_SQLITE_SCHEMA)
        _INITIALIZED_DATABASES.add(url)


_SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    schema_fingerprint TEXT NOT NULL,
    row_count INTEGER NOT NULL,
    column_count INTEGER NOT NULL,
    profile_json TEXT NOT NULL,
    quality_report_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_datasets_project_created
    ON datasets(project_id, created_at DESC);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    dataset_id TEXT REFERENCES datasets(id) ON DELETE SET NULL,
    run_type TEXT NOT NULL,
    status TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    manifest_json TEXT NOT NULL,
    error TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    revoked_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_analysis_runs_project_created
    ON analysis_runs(project_id, created_at DESC);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_id TEXT REFERENCES analysis_runs(id) ON DELETE SET NULL,
    artifact_type TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    content_type TEXT,
    expires_at INTEGER NOT NULL,
    revoked_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(run_id, relative_path)
);

CREATE INDEX IF NOT EXISTS idx_artifacts_run
    ON artifacts(run_id);

CREATE TABLE IF NOT EXISTS model_results (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    model_key TEXT NOT NULL,
    model_name TEXT NOT NULL,
    rank INTEGER NOT NULL,
    metrics_json TEXT NOT NULL,
    artifact_path TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_model_results_run_rank
    ON model_results(run_id, rank);

CREATE TABLE IF NOT EXISTS analysis_jobs (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
    run_id TEXT REFERENCES analysis_runs(id) ON DELETE SET NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    stage TEXT NOT NULL,
    message TEXT NOT NULL,
    completed_items INTEGER,
    total_items INTEGER,
    result_json TEXT,
    error TEXT,
    cancel_requested INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL,
    started_at REAL,
    finished_at REAL
);

CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status_created
    ON analysis_jobs(status, created_at DESC);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    project_id TEXT,
    run_id TEXT,
    artifact_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_project_created
    ON audit_logs(project_id, created_at DESC);
"""
