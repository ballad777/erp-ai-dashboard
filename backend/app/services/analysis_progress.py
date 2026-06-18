from __future__ import annotations

from collections.abc import Callable

ProgressCallback = Callable[[str, str, int | None, int | None], None]
CancelCheck = Callable[[], bool]


class AnalysisCancelledError(Exception):
    """Raised when a cooperative analysis job receives a cancellation request."""


def emit_progress(
    callback: ProgressCallback | None,
    stage: str,
    message: str,
    completed: int | None = None,
    total: int | None = None,
) -> None:
    if callback:
        callback(stage, message, completed, total)


def ensure_not_cancelled(should_cancel: CancelCheck | None) -> None:
    if should_cancel and should_cancel():
        raise AnalysisCancelledError("分析已由使用者取消。")

