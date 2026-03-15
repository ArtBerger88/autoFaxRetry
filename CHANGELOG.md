# Changelog

All notable changes to this project are documented in this file.

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
