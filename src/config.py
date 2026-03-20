import json
import os
from pathlib import Path
from typing import Any, Dict, Union

DEFAULT_CONFIG_PATH = Path("config/settings.json")

# mapping of environment variable -> configuration key
_ENV_OVERRIDES = {
    "SINCH_PROJECT_ID": "sinch_project_id",
    "SINCH_KEY_ID": "sinch_key_id",
    "SINCH_KEY_SECRET": "sinch_key_secret",
    "SINCH_FROM_NUMBER": "sinch_from_number",
    "SINCH_BASE_URL": "sinch_base_url",
    "FAX_NUMBER": "fax_number",
    "PDF_PATH": "pdf_path",
    "PDF_PATHS": "pdf_paths",
    "COVER_PAGE_FILE": "cover_page_file",
    "MAX_ATTEMPTS": "max_attempts",
    "DELAY_SECONDS": "delay_seconds",
    "LOG_FILE": "log_file",
    "STATUS_POLL_TIMEOUT_SECONDS": "status_poll_timeout_seconds",
    "AUTO_OPTIMIZE_PDF_BEFORE_SEND": "auto_optimize_pdf_before_send",
    "OPTIMIZED_PREVIEW_PDF_PATH": "optimized_preview_pdf_path",
    "TARGET_PDF_BYTES": "target_pdf_bytes",
    "GS_COMMAND": "gs_command",
}


def load_config(path: Union[str, Path] = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """Load and validate configuration.

    Values are read from a JSON file and may be overridden via environment
    variables.  The returned dictionary is guaranteed to contain the keys
    documented in ``DEFAULT_CONFIG_PATH``.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    json.JSONDecodeError
        If the file is not valid JSON.
    ValueError
        If required keys are missing or a value has an invalid type.
    """
    cfg_path = Path(path)
    with cfg_path.open(encoding="utf-8") as f:
        cfg: Dict[str, Any] = json.load(f)

    # apply any environment overrides
    for env_key, cfg_key in _ENV_OVERRIDES.items():
        if env_key in os.environ:
            val = os.environ[env_key]
            if cfg_key in (
                "max_attempts",
                "delay_seconds",
                "target_pdf_bytes",
                "status_poll_timeout_seconds",
            ):
                try:
                    if cfg_key in ("max_attempts", "target_pdf_bytes"):
                        val = int(val)
                    else:
                        val = float(val)
                except ValueError:
                    raise ValueError(f"{env_key} must be a number")
            if cfg_key == "auto_optimize_pdf_before_send":
                val = str(val).strip().lower() in {"1", "true", "yes", "on"}
            if cfg_key == "pdf_paths":
                val = [part.strip() for part in str(val).split(",") if part.strip()]
            cfg[cfg_key] = val

    _validate_config(cfg)
    return cfg


def _validate_config(cfg: Dict[str, Any]) -> None:
    """Raise ``ValueError`` if the configuration dictionary is invalid."""
    required = [
        "sinch_project_id",
        "sinch_key_id",
        "sinch_key_secret",
        "fax_number",
        "max_attempts",
        "delay_seconds",
        "log_file",
    ]
    missing = [k for k in required if k not in cfg]
    if missing:
        raise ValueError(f"Missing config keys: {', '.join(missing)}")

    if not isinstance(cfg["max_attempts"], int) or cfg["max_attempts"] < 1:
        raise ValueError("max_attempts must be a positive integer")

    if not isinstance(cfg["delay_seconds"], (int, float)) or cfg["delay_seconds"] < 0:
        raise ValueError("delay_seconds must be a non-negative number")

    if "status_poll_timeout_seconds" in cfg:
        if not isinstance(cfg["status_poll_timeout_seconds"], (int, float)):
            raise ValueError("status_poll_timeout_seconds must be a positive number")
        if float(cfg["status_poll_timeout_seconds"]) <= 0:
            raise ValueError("status_poll_timeout_seconds must be a positive number")

    for key in ("fax_number", "log_file"):
        if not isinstance(cfg[key], str) or not cfg[key].strip():
            raise ValueError(f"{key} must be a non-empty string")

    fax_number = str(cfg["fax_number"]).strip()
    if not fax_number.startswith("+"):
        raise ValueError("fax_number must be in E.164 format (for example +14155551234)")

    for key in ("sinch_project_id", "sinch_key_id", "sinch_key_secret"):
        if not isinstance(cfg[key], str) or not cfg[key].strip():
            raise ValueError(f"{key} must be a non-empty string")

    if "sinch_from_number" in cfg and cfg["sinch_from_number"] is not None:
        if not isinstance(cfg["sinch_from_number"], str) or not cfg["sinch_from_number"].strip():
            raise ValueError("sinch_from_number must be a non-empty string when provided")
        if not str(cfg["sinch_from_number"]).strip().startswith("+"):
            raise ValueError(
                "sinch_from_number must be in E.164 format (for example +14155551234)"
            )

    if "sinch_base_url" in cfg and cfg["sinch_base_url"] is not None:
        if not isinstance(cfg["sinch_base_url"], str) or not cfg["sinch_base_url"].strip():
            raise ValueError("sinch_base_url must be a non-empty string when provided")

    if "auto_optimize_pdf_before_send" in cfg and not isinstance(
        cfg["auto_optimize_pdf_before_send"], bool
    ):
        raise ValueError("auto_optimize_pdf_before_send must be a boolean")

    if "target_pdf_bytes" in cfg:
        if not isinstance(cfg["target_pdf_bytes"], int) or cfg["target_pdf_bytes"] < 1:
            raise ValueError("target_pdf_bytes must be a positive integer")

    if "gs_command" in cfg and cfg["gs_command"] is not None:
        if not isinstance(cfg["gs_command"], str) or not cfg["gs_command"].strip():
            raise ValueError("gs_command must be a non-empty string when provided")

    if "optimized_preview_pdf_path" in cfg and cfg["optimized_preview_pdf_path"] is not None:
        if not isinstance(cfg["optimized_preview_pdf_path"], str) or not cfg[
            "optimized_preview_pdf_path"
        ].strip():
            raise ValueError("optimized_preview_pdf_path must be a non-empty string when provided")

    pdf_paths: list[str] = []
    if "pdf_paths" in cfg:
        if not isinstance(cfg["pdf_paths"], list) or not cfg["pdf_paths"]:
            raise ValueError("pdf_paths must be a non-empty list of file paths")
        if any(not isinstance(p, str) or not p.strip() for p in cfg["pdf_paths"]):
            raise ValueError("pdf_paths must contain non-empty strings")
        pdf_paths = [str(p).strip() for p in cfg["pdf_paths"]]
    elif "pdf_path" in cfg:
        if not isinstance(cfg["pdf_path"], str) or not cfg["pdf_path"].strip():
            raise ValueError("pdf_path must be a non-empty string")
        pdf_paths = [cfg["pdf_path"].strip()]
    else:
        raise ValueError("Either pdf_path or pdf_paths must be provided")

    for one_path in pdf_paths:
        path_obj = Path(one_path)
        if not path_obj.exists() or not path_obj.is_file():
            raise ValueError(f"PDF path does not exist or is not a file: {one_path}")
        if not os.access(path_obj, os.R_OK):
            raise ValueError(f"PDF path is not readable: {one_path}")

    if "cover_page_text" in cfg and cfg["cover_page_text"] is not None:
        if not isinstance(cfg["cover_page_text"], str):
            raise ValueError("cover_page_text must be a string")

    if "cover_page_file" in cfg and cfg["cover_page_file"] is not None:
        if not isinstance(cfg["cover_page_file"], str) or not cfg["cover_page_file"].strip():
            raise ValueError("cover_page_file must be a non-empty string")
        cover_file = Path(cfg["cover_page_file"].strip())
        if not cover_file.exists() or not cover_file.is_file():
            raise ValueError(
                f"cover_page_file does not exist or is not a file: {cfg['cover_page_file']}"
            )
        if not os.access(cover_file, os.R_OK):
            raise ValueError(f"cover_page_file is not readable: {cfg['cover_page_file']}")

    if cfg.get("cover_page_text") and cfg.get("cover_page_file"):
        raise ValueError("Provide either cover_page_text or cover_page_file, not both")

    log_file_path = Path(cfg["log_file"])
    log_dir = log_file_path.parent if log_file_path.parent != Path("") else Path(".")
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ValueError(f"Could not create log directory '{log_dir}': {exc}") from exc

    try:
        with log_file_path.open("a", encoding="utf-8"):
            pass
    except OSError as exc:
        raise ValueError(f"log_file is not writable: {cfg['log_file']} ({exc})") from exc

    if cfg.get("optimized_preview_pdf_path"):
        preview_path = Path(str(cfg["optimized_preview_pdf_path"]).strip())
        preview_dir = preview_path.parent if preview_path.parent != Path("") else Path(".")
        try:
            preview_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ValueError(f"Could not create optimized preview directory '{preview_dir}': {exc}") from exc

        try:
            with preview_path.open("ab"):
                pass
        except OSError as exc:
            raise ValueError(
                f"optimized_preview_pdf_path is not writable: {cfg['optimized_preview_pdf_path']} ({exc})"
            ) from exc
