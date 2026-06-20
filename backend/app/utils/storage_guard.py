from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib

REPO_ROOT = Path(__file__).resolve().parents[3]
GENERATED_OUTPUTS_DIR = REPO_ROOT / "generated_outputs"
MODELS_DIR = GENERATED_OUTPUTS_DIR / "models"
CHARTS_DIR = GENERATED_OUTPUTS_DIR / "charts"
REPORTS_DIR = GENERATED_OUTPUTS_DIR / "reports"
DATA_DIR = GENERATED_OUTPUTS_DIR / "data"
MODEL_EXTENSIONS = {".joblib", ".pkl", ".pickle", ".model", ".bin"}
DEFAULT_MODEL_MAX_MB = 200
MODEL_DIR_WARNING_MB = 2048

logger = logging.getLogger(__name__)


def get_dir_size(path: str | Path) -> dict[str, float | int]:
    directory = Path(path)
    total = 0
    if directory.exists():
        for item in directory.rglob("*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except OSError:
                    logger.warning("Unable to stat file while measuring storage: %s", item)
    return _size_payload(total)


def safe_save_model(
    model: Any,
    path: str | Path,
    *,
    max_mb: int = DEFAULT_MODEL_MAX_MB,
    enabled: bool = False,
) -> dict[str, Any]:
    model_path = Path(path)
    if not enabled:
        return {
            "saved": False,
            "path": None,
            "size_mb": 0,
            "warning": "save_model=false，未保存完整模型物件。",
        }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    size_mb = model_path.stat().st_size / 1024 / 1024
    if size_mb > max_mb:
        model_path.unlink(missing_ok=True)
        warning = f"模型檔案超過 {max_mb}MB，已自動刪除。分析結果仍可使用。"
        logger.warning("%s path=%s size_mb=%.2f", warning, model_path, size_mb)
        return {
            "saved": False,
            "path": None,
            "size_mb": round(size_mb, 4),
            "warning": warning,
        }

    return {
        "saved": True,
        "path": _display_path(model_path),
        "size_mb": round(size_mb, 4),
        "warning": None,
    }


def cleanup_old_models(models_dir: str | Path = MODELS_DIR, *, keep_latest: int = 5) -> dict[str, Any]:
    directory = Path(models_dir)
    if not directory.exists():
        return {"deleted_files": [], "kept_files": [], "deleted_count": 0}

    model_files = sorted(
        [item for item in directory.rglob("*") if item.is_file() and item.suffix.lower() in MODEL_EXTENSIONS],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    kept = model_files[: max(0, keep_latest)]
    deleted: list[str] = []
    for item in model_files[max(0, keep_latest):]:
        try:
            item.unlink(missing_ok=True)
            deleted.append(_display_path(item))
        except OSError:
            logger.exception("Unable to delete old model file: %s", item)

    return {
        "deleted_files": deleted,
        "kept_files": [_display_path(item) for item in kept],
        "deleted_count": len(deleted),
    }


def cleanup_large_files(
    directory: str | Path = GENERATED_OUTPUTS_DIR,
    *,
    max_mb: int = DEFAULT_MODEL_MAX_MB,
) -> dict[str, Any]:
    root = Path(directory)
    if not root.exists():
        return {"deleted_files": [], "deleted_count": 0}

    deleted: list[dict[str, Any]] = []
    max_bytes = max_mb * 1024 * 1024
    for item in root.rglob("*"):
        if not item.is_file() or item.suffix.lower() not in MODEL_EXTENSIONS:
            continue
        try:
            size = item.stat().st_size
        except OSError:
            logger.warning("Unable to stat generated output while cleaning: %s", item)
            continue
        if size <= max_bytes:
            continue
        item.unlink(missing_ok=True)
        deleted.append(
            {
                "path": _display_path(item),
                "size_mb": round(size / 1024 / 1024, 4),
            }
        )

    return {"deleted_files": deleted, "deleted_count": len(deleted)}


def cleanup_all_models(models_dir: str | Path = MODELS_DIR) -> dict[str, Any]:
    directory = Path(models_dir)
    if not directory.exists():
        return {"deleted_files": [], "deleted_count": 0}

    deleted: list[str] = []
    for item in directory.rglob("*"):
        if item.is_file() and item.suffix.lower() in MODEL_EXTENSIONS:
            item.unlink(missing_ok=True)
            deleted.append(_display_path(item))
    return {"deleted_files": deleted, "deleted_count": len(deleted)}


def cleanup_latest_only(outputs_dir: str | Path = GENERATED_OUTPUTS_DIR) -> dict[str, Any]:
    root = Path(outputs_dir)
    if not root.exists():
        return {"deleted_files": [], "deleted_count": 0}

    deleted: list[str] = []
    for directory in (MODELS_DIR, CHARTS_DIR, REPORTS_DIR, DATA_DIR):
        if not directory.exists():
            continue
        files = sorted(
            [item for item in directory.iterdir() if item.is_file()],
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        keep = files[:1]
        for item in files[1:]:
            try:
                item.unlink(missing_ok=True)
                deleted.append(_display_path(item))
            except OSError:
                logger.exception("Unable to delete generated output: %s", item)
        if directory == MODELS_DIR:
            cleanup_old_models(directory, keep_latest=len(keep))
    return {"deleted_files": deleted, "deleted_count": len(deleted)}


def get_storage_status() -> dict[str, Any]:
    generated = get_dir_size(GENERATED_OUTPUTS_DIR)
    models = get_dir_size(MODELS_DIR)
    charts = get_dir_size(CHARTS_DIR)
    reports = get_dir_size(REPORTS_DIR)
    data = get_dir_size(DATA_DIR)
    large_files = _list_large_model_files(GENERATED_OUTPUTS_DIR)
    models_warning = float(models["mb"]) > MODEL_DIR_WARNING_MB
    return {
        "generated_outputs": generated,
        "models": models,
        "charts": charts,
        "reports": reports,
        "data": data,
        "warning": models_warning,
        "warning_message": (
            "模型輸出資料夾過大，建議清理舊模型。"
            if models_warning
            else None
        ),
        "large_model_files": large_files,
    }


def startup_storage_audit() -> dict[str, Any]:
    status = get_storage_status()
    large_cleanup = cleanup_large_files(GENERATED_OUTPUTS_DIR)
    if status["warning"] or large_cleanup["deleted_count"]:
        logger.warning(
            "Generated output storage audit warning: status=%s cleanup=%s",
            status,
            large_cleanup,
        )
    return {"status": get_storage_status(), "cleanup": large_cleanup}


def _list_large_model_files(directory: Path, *, max_mb: int = DEFAULT_MODEL_MAX_MB) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    max_bytes = max_mb * 1024 * 1024
    large_files: list[dict[str, Any]] = []
    for item in directory.rglob("*"):
        if not item.is_file() or item.suffix.lower() not in MODEL_EXTENSIONS:
            continue
        try:
            size = item.stat().st_size
        except OSError:
            continue
        if size > max_bytes:
            large_files.append(
                {
                    "path": _display_path(item),
                    "size_mb": round(size / 1024 / 1024, 4),
                }
            )
    return large_files


def _size_payload(size_bytes: int) -> dict[str, float | int]:
    return {
        "bytes": int(size_bytes),
        "mb": round(size_bytes / 1024 / 1024, 4),
        "gb": round(size_bytes / 1024 / 1024 / 1024, 4),
    }


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)
