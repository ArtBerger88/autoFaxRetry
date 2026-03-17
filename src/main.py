import argparse
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Optional

from src import config as config_module
from src.document_builder import prepare_fax_document
from src.fax_api import SinchFaxAPI
from src.pdf_optimizer import optimize_pdf_for_send
from src.retry_controller import run_retry_loop
from src.utils.logger import log


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
    parser.add_argument(
        "--pdf-path",
        dest="pdf_paths",
        action="append",
        help="Override PDF file path (repeat for multiple documents)",
    )
    parser.add_argument(
        "--cover-page-text",
        help="Optional plain-text cover page to prepend before merged documents",
    )
    parser.add_argument(
        "--cover-page-file",
        help="Optional PDF cover page file to prepend before merged documents",
    )
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
    if args.pdf_paths is not None:
        merged["pdf_paths"] = list(args.pdf_paths)
        merged["pdf_path"] = args.pdf_paths[0]
    if args.cover_page_text is not None:
        merged["cover_page_text"] = args.cover_page_text
    if args.cover_page_file is not None:
        merged["cover_page_file"] = args.cover_page_file
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
    temp_dirs: list[TemporaryDirectory] = []

    try:
        cfg = config_module.load_config(Path(args.config))
        cfg = _apply_cli_overrides(cfg, args)
        source_pdf_paths = cfg.get("pdf_paths") or [cfg["pdf_path"]]
        prepared_pdf_path, temp_dir = prepare_fax_document(
            source_pdf_paths,
            cfg.get("cover_page_text"),
            cfg.get("cover_page_file"),
        )
        if temp_dir is not None:
            temp_dirs.append(temp_dir)

        if cfg.get("auto_optimize_pdf_before_send", False):
            optimized_path, optimize_temp_dir, optimize_status = optimize_pdf_for_send(
                prepared_pdf_path,
                int(cfg.get("target_pdf_bytes", 150_000)),
                cfg.get("gs_command"),
            )
            log(optimize_status, cfg["log_file"])
            prepared_pdf_path = optimized_path
            if optimize_temp_dir is not None:
                temp_dirs.append(optimize_temp_dir)

        cfg["pdf_path"] = prepared_pdf_path
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    api = SinchFaxAPI(
        project_id=cfg["sinch_project_id"],
        key_id=cfg["sinch_key_id"],
        key_secret=cfg["sinch_key_secret"],
        base_url=cfg.get("sinch_base_url", "https://fax.api.sinch.com"),
    )

    try:
        success = run_retry_loop(api, cfg)
        return 0 if success else 1
    finally:
        for one_temp_dir in temp_dirs:
            one_temp_dir.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())