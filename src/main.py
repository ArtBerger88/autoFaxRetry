import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from src import config as config_module
from src.fax_api import PhaxioAPI
from src.retry_controller import run_retry_loop


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def _non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Auto Fax Retry runner")
    parser.add_argument(
        "--config",
        default=str(config_module.DEFAULT_CONFIG_PATH),
        help="Path to settings JSON file",
    )
    parser.add_argument("--fax-number", help="Override target fax number")
    parser.add_argument("--pdf-path", help="Override PDF file path")
    parser.add_argument("--max-attempts", type=_positive_int, help="Override max retry attempts")
    parser.add_argument(
        "--delay-seconds",
        type=_non_negative_float,
        help="Override delay in seconds between attempts",
    )
    parser.add_argument("--log-file", help="Override log output path")
    return parser


def _apply_cli_overrides(cfg: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    merged = dict(cfg)
    if args.fax_number is not None:
        merged["fax_number"] = args.fax_number
    if args.pdf_path is not None:
        merged["pdf_path"] = args.pdf_path
    if args.max_attempts is not None:
        merged["max_attempts"] = args.max_attempts
    if args.delay_seconds is not None:
        merged["delay_seconds"] = args.delay_seconds
    if args.log_file is not None:
        merged["log_file"] = args.log_file
    config_module._validate_config(merged)
    return merged


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        cfg = config_module.load_config(Path(args.config))
        cfg = _apply_cli_overrides(cfg, args)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    api = PhaxioAPI(
        cfg["phaxio_api_key"],
        cfg["phaxio_api_secret"],
    )

    success = run_retry_loop(api, cfg)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())