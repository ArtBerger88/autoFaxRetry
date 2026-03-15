# Auto-Fax-Retry

Lightweight Python service that sends a PDF to a fax number and retries failed attempts automatically. Built for unattended monthly or scheduled fax jobs.

## Features
- Retry loop with configurable attempts and delay.
- Phaxio API integration with timeout and error normalization.
- JSON structured logs with file rotation.
- Configuration from JSON plus environment variable overrides.
- CLI overrides for one-off runs and scheduler integration.

## Quick start
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip pytest requests
```

Configure `config/settings.json` with valid values, especially:
- `phaxio_api_key`
- `phaxio_api_secret`
- `fax_number`
- `pdf_path`
- `log_file`

Run:
```powershell
python -m src.main
```

## CLI usage
```powershell
python -m src.main --config config/settings.json --fax-number 15551234567 --pdf-path data/sample.pdf --max-attempts 5 --delay-seconds 30 --log-file data/logs/fax.log
```

Supported arguments:
- `--config`
- `--fax-number`
- `--pdf-path`
- `--max-attempts`
- `--delay-seconds`
- `--log-file`

Exit codes:
- `0`: fax delivered within retry limits
- `1`: retry loop exhausted without delivery
- `2`: configuration/startup validation error

## Production docs
- Architecture: `docs/architecture.md`
- Roadmap: `docs/roadmap.md`
- Operations runbook: `docs/operations_runbook.md`
- Release prep: `docs/release_prep.md`
- Changelog: `CHANGELOG.md`

## Project structure
```text
config/
src/
  config.py
  fax_api.py
  main.py
  retry_controller.py
  send_fax_once.py
  utils/
    logger.py
tests/
docs/
```