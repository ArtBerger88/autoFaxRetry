# Operations Runbook

## Purpose
Use this guide to run Auto-Fax-Retry safely in production and troubleshoot failures.

## Pre-deployment checklist
- Python 3.11+ installed.
- Valid Sinch Fax credentials configured.
- `pdf_paths` (or `pdf_path`) points to readable file(s).
- `log_file` directory is writable.
- Outbound HTTPS access to `fax.api.sinch.com` is allowed.
- Ghostscript installed if `auto_optimize_pdf_before_send` is enabled.

## Configuration
Primary config file: `config/settings.json`

Sensitive values should come from environment variables:
- `SINCH_PROJECT_ID`
- `SINCH_KEY_ID`
- `SINCH_KEY_SECRET`
- `SINCH_FROM_NUMBER` (optional)
- `SINCH_IMAGE_RESOLUTION` (optional, recommended `normal`)
- `FAX_NUMBER`
- `PDF_PATHS` (comma-separated) or `PDF_PATH`
- `MAX_ATTEMPTS`
- `DELAY_SECONDS`
- `LOG_FILE`
- `STATUS_POLL_TIMEOUT_SECONDS`

## Manual run
```powershell
python -m src.main --config config/settings.json
```

Example with overrides:
```powershell
python -m src.main --fax-number 15551234567 --pdf-path C:\fax\payload.pdf --max-attempts 5 --delay-seconds 60 --status-poll-timeout-seconds 600
```

Example with optimization preview persisted:
```powershell
python -m src.main --config config/settings.json --optimized-preview-pdf-path data/output/last_optimized_preview.pdf
```

## Exit codes
- `0`: Success within retry limit.
- `1`: Retries exhausted.
- `2`: Startup/config validation failed.

## Logging
- Log format: JSON lines.
- Rotation: 1 MB per file, 5 backups.
- Each run includes a `run_id` to correlate all attempts.
- Attempt events include `fax_id`, `provider_status`, `status_code`, and `error_reason`.
- Session-level diagnostics include runtime API base URL and credential fingerprints (`key_fp`, `secret_fp`).

## Delivery tuning guidance
- Use `sinch_image_resolution: "normal"` to improve destination compatibility and speed up handshake outcomes on marginal fax routes.
- Set `sinch_from_number` when your account/routing policy expects a specific source number.
- Enable `auto_optimize_pdf_before_send` to reduce file size and transmission overhead.
- Tune `status_poll_timeout_seconds` to control how long each attempt waits for terminal status before counting as a failure.

## Windows Task Scheduler setup
Use a task action similar to:
```text
Program/script: <path-to-project>\.venv\Scripts\python.exe
Add arguments: -m src.main --config config/settings.json
Start in: <path-to-project>
```

Replace `<path-to-project>` with your actual project root directory.
Set environment variables at the machine/user level so scheduled runs can access secrets.

## Troubleshooting
- `Configuration error` on startup:
  - Verify JSON syntax in `config/settings.json`.
  - Verify `pdf_path` exists and is readable.
  - Verify log directory is writable.
- Repeated `network_error` in logs:
  - Check internet connectivity and firewall rules.
  - Confirm TLS interception/proxy settings if present.
- Repeated provider HTTP failures:
  - Validate API credentials.
  - Inspect provider-side status dashboard and error message.
- Repeated provider `FAILURE` with `Disconnected after permitted retries`:
  - Indicates remote handshake/session instability (destination endpoint or telecom route), not local startup/auth issues.
  - If delay changes only alter cadence but not outcomes, escalate with provider run evidence (`run_id`, `fax_id`, timestamps, failure reasons).

## Recovery procedure
1. Fix underlying issue (credentials, network, file path).
2. Re-run manually once with `python -m src.main`.
3. Confirm log entries show successful submission/delivery.
4. Re-enable scheduler if it was paused.
