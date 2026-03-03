# Auto‑Fax‑Retry
A lightweight Python service that sends a PDF to a fax number and automatically retries when the transmission fails. Designed for simple, reliable, unattended monthly faxing without daily attempt limits or email‑based confirmation steps.

## Features
-Automatic retry on failed fax attempts, up to a configurable limit
-No Per day cap on attempts
-Direct fax API integration (no email confirmation, no two‑step workflow)
-Logs attempts (including detailed messages to `logs/fax_attempts.log`)
-Notification upon successful send

## Project structure
config/

src/
  fax_api.py       # Wrapper around the chosen fax provider
  retry_controller.py # Application retry loop; logs via utils/logger
  utils/logger.py  # Simple timestamped logging helpers
  main.py          # Example invocation / entry point

docs/
  architecture.md  # System design and module interactions
  roadmap.md       # Planned features and milestones
  notes.md         # Additional design notes

LICENSE
README.md