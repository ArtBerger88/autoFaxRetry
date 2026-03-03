import json
import os
from pathlib import Path
from typing import Any, Dict, Union

DEFAULT_CONFIG_PATH = Path("config/settings.json")

# mapping of environment variable -> configuration key
_ENV_OVERRIDES = {
    "PHAXIO_API_KEY": "phaxio_api_key",
    "PHAXIO_API_SECRET": "phaxio_api_secret",
    "FAX_NUMBER": "fax_number",
    "PDF_PATH": "pdf_path",
    "MAX_ATTEMPTS": "max_attempts",
    "DELAY_SECONDS": "delay_seconds",
    "LOG_FILE": "log_file",
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
            if cfg_key in ("max_attempts", "delay_seconds"):
                try:
                    val = int(val) if cfg_key == "max_attempts" else float(val)
                except ValueError:
                    raise ValueError(f"{env_key} must be a number")
            cfg[cfg_key] = val

    _validate_config(cfg)
    return cfg


def _validate_config(cfg: Dict[str, Any]) -> None:
    """Raise ``ValueError`` if the configuration dictionary is invalid."""
    required = [
        "phaxio_api_key",
        "phaxio_api_secret",
        "fax_number",
        "pdf_path",
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

    for key in ("fax_number", "pdf_path", "log_file"):
        if not isinstance(cfg[key], str) or not cfg[key].strip():
            raise ValueError(f"{key} must be a non-empty string")

    for key in ("phaxio_api_key", "phaxio_api_secret"):
        if not isinstance(cfg[key], str) or not cfg[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
