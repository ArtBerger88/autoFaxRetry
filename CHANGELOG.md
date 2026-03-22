# Changelog

All notable changes to this project are documented in this file.

## [1.1.0] - 2026-03-21

### Added
- Optional pre-send PDF optimization using Ghostscript with optimization status logging.
- Optional persisted optimized preview output (`optimized_preview_pdf_path`).
- Provider request controls for optional `sinch_from_number` and `sinch_image_resolution`.
- Expanded per-run diagnostics including runtime auth fingerprints and API base URL.
- Expanded attempt diagnostics including provider status and provider failure reason.

### Changed
- Poll timeout is now configurable via `status_poll_timeout_seconds` and CLI override.
- Operational guidance now recommends `sinch_image_resolution: normal` to improve handshake compatibility on unstable routes.

### Docs
- Updated architecture and operations runbook for current module flow and troubleshooting.
- Updated roadmap with completed post-release hardening items.
- Removed dependency on `data/sample.pdf` from documentation examples.

## [1.0.0] - 2026-03-15

### Added
- Retry controller for automatic resend attempts with configurable delay and attempt limits.
- Phaxio provider client integration with send and status polling flows.
- Configuration loading from JSON with environment variable overrides.
- Startup validation for required settings, readable PDF path, and writable log path.
- Structured JSON logging with rotating file support.
- CLI overrides in `src.main` for one-off execution and scheduler jobs.
- Operations runbook for production usage and troubleshooting.
- Unit tests for config, logger, retry flow, fax API wrapper, and CLI behavior.

### Changed
- Logging output format changed from plain text to JSON lines.
- Main entrypoint now returns explicit process exit codes:
  - `0` success
  - `1` retries exhausted
  - `2` configuration/startup error

### Notes
- This release is intended for backend automation and scheduled execution.
- No web UI is included in v1.0.0.
