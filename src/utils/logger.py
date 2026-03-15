import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict

_LOGGER_CACHE: Dict[str, logging.Logger] = {}
_MAX_BYTES = 1_048_576
_BACKUP_COUNT = 5


def _timestamp() -> str:
    """Return an ISO-8601 timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


def _get_logger(log_file: str) -> logging.Logger:
    path = str(Path(log_file))
    if path in _LOGGER_CACHE:
        return _LOGGER_CACHE[path]

    log_path = Path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(f"auto_fax_retry::{path}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Avoid duplicate handlers if this module is reloaded.
    if not logger.handlers:
        handler = RotatingFileHandler(
            filename=path,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    _LOGGER_CACHE[path] = logger
    return logger


def _emit(log_file: str, event: str, **fields: Any) -> None:
    payload = {
        "timestamp": _timestamp(),
        "event": event,
        **fields,
    }
    _get_logger(log_file).info(json.dumps(payload, ensure_ascii=True))


def log(message: str, log_file: str = "logs/fax_attempts.log", **fields: Any) -> None:
    """Write a structured application log event."""
    _emit(log_file, event="message", message=message, **fields)


def log_attempt(log_file: str, attempt_number: int, result: Dict[str, Any], **fields: Any) -> None:
    """Write a structured attempt result event."""
    success = bool(result.get("success"))
    status = "SUCCESS" if success else "FAILURE"
    message = str(result.get("message", ""))
    summary = f"Attempt {attempt_number}: {status} - {message}"

    _emit(
        log_file,
        event="attempt",
        attempt=attempt_number,
        success=success,
        status=status,
        message=message,
        summary=summary,
        **fields,
    )