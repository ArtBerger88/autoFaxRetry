# Auto Fax Retry Service - Roadmap

## Phase 1: Project Foundation
- [✅] Create initial repository structure
- [✅] Add README, LICENSE, architecture, and roadmap documents
- [✅] Set up src/ and docs/ directories
- [✅] Establish commit conventions and branching workflow

## Phase 2: Core Fax Engine (Mock Implementation)
- [✅] Implement fax_api.py with a mock fax provider
- [✅] Define a consistent response format for success/failure
- [✅] Add basic logging for each attempt
- [✅] Create main.py to demonstrate a single fax send

## Phase 3: Retry Engine
- [✅] Implement retry logic in retry_controller.py
- [✅] Add configurable retry limits and delays
- [✅] Integrate logging for each retry attempt
- [✅] Add success/failure notifications (console or file‑based)

## Phase 4: Configuration System
- [✅] Implement config for:
    [✅]API keys
    [✅]Fax number
    [✅]PDF path
    [✅]Retry limits
    [✅]Delay strategy
- [✅] Add validation for missing or invalid config values

## Phase 5: Real Fax Provider Integration
- [✅] Replace mock API with a real fax provider
- [✅] Add error handling for provider‑specific failure modes
- [✅] Add environment variable support for sensitive values

## Phase 6: Reliability & automation
- [✅] Improve logging format (timestamps, attempt numbers, status codes)
- [✅] Add rotating log files
- [✅] Add CLI arguments for overrides
- [✅] Prepare for scheduled/automated execution

## Phase 7: Release Prep
- [✅] Finalize documentation
- [✅] Tag v1.1.0

## Phase 8: Release
- [✅] Release

## Phase 9: Post-release hardening
- [✅] Add optional pre-send PDF optimization with Ghostscript and persisted preview output
- [✅] Add provider request controls for `sinch_from_number` and `sinch_image_resolution`
- [✅] Default operations tuning to `normal` image resolution for better handshake compatibility
- [✅] Add richer diagnostics (`run_id`, provider status details, auth fingerprints)
- [✅] Expand operations and architecture docs to reflect production behavior and troubleshooting signals