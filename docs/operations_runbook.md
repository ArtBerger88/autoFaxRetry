# Operations Runbook

## Purpose
Use this guide to run Auto-Fax-Retry safely in production and troubleshoot failures.

## Pre-deployment checklist
- Python 3.11+ installed.
- Valid Phaxio credentials configured.
- `pdf_path` points to a readable file.
- `log_file` directory is writable.
- Outbound HTTPS access to `api.phaxio.com` is allowed.

## Configuration
Primary config file: `config/settings.json`

Sensitive values should come from environment variables:
- `PHAXIO_API_KEY`
- `PHAXIO_API_SECRET`
- `FAX_NUMBER`
- `PDF_PATH`
- `MAX_ATTEMPTS`
- `DELAY_SECONDS`
- `LOG_FILE`

## Manual run
```powershell
python -m src.main --config config/settings.json
```

Example with overrides:
```powershell
python -m src.main --fax-number 15551234567 --pdf-path data/sample.pdf --max-attempts 5 --delay-seconds 60
```

## Exit codes
- `0`: Success within retry limit.
- `1`: Retries exhausted.
- `2`: Startup/config validation failed.

## Logging
- Log format: JSON lines.
- Rotation: 1 MB per file, 5 backups.
- Each run includes a `run_id` to correlate all attempts.

## Windows Task Scheduler setup
Use a task action similar to:
```text
Program/script: C:\Users\artyz\ProjectFile\Auto-fax-retry\autoFaxRetry\.venv\Scripts\python.exe
Add arguments: -m src.main --config config/settings.json
Start in: C:\Users\artyz\ProjectFile\Auto-fax-retry\autoFaxRetry
```

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

## Recovery procedure
1. Fix underlying issue (credentials, network, file path).
2. Re-run manually once with `python -m src.main`.
3. Confirm log entries show successful submission/delivery.
4. Re-enable scheduler if it was paused.
