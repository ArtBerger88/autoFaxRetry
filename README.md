# Auto-Fax-Retry

Lightweight Python service that sends a PDF to a fax number and retries failed attempts automatically. Built for unattended monthly or scheduled fax jobs.

## Features
- Retry loop with configurable attempts and delay.
- Sinch Fax API integration with timeout and error normalization.
- JSON structured logs with file rotation.
- Configuration from JSON plus environment variable overrides.
- CLI overrides for one-off runs and scheduler integration.
- Single fax payload from multiple source PDFs (merged before send).
- Optional generated text cover page prepended before merged documents.

## Quick start
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip pytest requests
```

Configure `config/settings.json` with valid values, especially:
- `sinch_project_id`
- `sinch_key_id`
- `sinch_key_secret`
- `fax_number`
- `pdf_path`
- `log_file`

Run:
```powershell
python -m src.main
```

## CLI usage
```powershell
python -m src.main --config config/settings.json --fax-number 15551234567 --pdf-path data/intake.pdf --pdf-path data/labs.pdf --cover-page-text "Patient: Jane Doe" --max-attempts 5 --delay-seconds 30 --log-file data/logs/fax.log
```

Use a branded cover PDF instead of generated text:
```powershell
python -m src.main --pdf-path data/intake.pdf --pdf-path data/labs.pdf --cover-page-file data/cover_template.pdf
```

Supported arguments:
- `--config`
- `--fax-number`
- `--pdf-path`
- `--cover-page-text`
- `--cover-page-file`
- `--max-attempts`
- `--delay-seconds`
- `--log-file`

Dependency note:
- Multi-document merge requires `pypdf`.
- Generated text cover page requires `reportlab`.
- `--cover-page-text` and `--cover-page-file` are mutually exclusive.

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