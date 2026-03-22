# Architecture Overview

Auto-Fax-Retry is a modular Python service that builds a fax payload, optionally optimizes it, sends it through the Sinch Fax API, and retries until delivery or retry exhaustion.

## Runtime Modules

## 1. `config.py` - Configuration Layer
Loads and validates settings from JSON plus environment overrides.

Core responsibilities:
- Validate required auth/runtime settings.
- Validate PDF/cover inputs and writable log/output paths.
- Normalize provider options such as `sinch_from_number` and `sinch_image_resolution`.

## 2. `document_builder.py` - Payload Assembly
Builds the outbound PDF payload.

Core responsibilities:
- Accept single or multiple source PDFs.
- Optionally prepend either a generated text cover page or a provided cover PDF.
- Emit a temporary merged payload when composition is required.

## 3. `pdf_optimizer.py` - Pre-Send Optimization
Optionally compresses the payload with Ghostscript before submission.

Core responsibilities:
- Try optimization profiles (`/ebook`, fallback `/screen`).
- Keep original PDF if optimization does not improve size.
- Return status text used by structured logs.

## 4. `fax_api.py` - Provider Adapter (Sinch)
Wraps provider HTTP calls and normalizes responses.

Core responsibilities:
- Submit fax payload and return normalized send status.
- Poll fax status details and normalize provider outcomes.
- Include transport-level retry for transient network/SSL failures.
- Forward optional provider request fields (`from`, `imageResolution`).

## 5. `send_fax_once.py` - Single Attempt Controller
Executes one send+poll cycle.

Core responsibilities:
- Submit once via provider adapter.
- Poll status until success, failure, or per-attempt timeout.
- Return normalized attempt result with provider metadata.

## 6. `retry_controller.py` - Retry Loop Orchestration
Coordinates repeated attempts.

Core responsibilities:
- Generate and attach `run_id` to all events in a session.
- Log per-attempt outcomes and summary events.
- Stop on success, fatal auth rejection (HTTP 401/403), or max attempts.

## 7. `main.py` - CLI Entry Point
Main runtime bootstrap used by manual execution and schedulers.

Core responsibilities:
- Parse CLI overrides.
- Build/optimize payload and persist optimized preview when configured.
- Initialize provider adapter and invoke retry loop.
- Return deterministic exit codes (`0`, `1`, `2`).

## Data Flow

`main.py`
-> `config.py` (load + validate)
-> `document_builder.py` (compose payload)
-> `pdf_optimizer.py` (optional compression)
-> `retry_controller.py` (attempt orchestration)
-> `send_fax_once.py` (single send+poll)
-> `fax_api.py` (provider I/O)
-> structured logs (`data/logs/*.log`)

## Observability and Diagnostics

Structured JSON logs include:
- UTC timestamp and event type (`message` / `attempt`)
- `run_id` for end-to-end correlation
- attempt index and normalized status
- provider metadata (`provider_status`, `status_code`, `error_reason`, `fax_id`)
- runtime auth fingerprints (`key_fp`, `secret_fp`) and API base URL for quick environment verification

This diagnostic model enables post-run analysis of retry pacing, provider behavior, and delivery failure patterns without exposing raw credentials.

