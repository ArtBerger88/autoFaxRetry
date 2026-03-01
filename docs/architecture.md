# Architecture Overview

Auto‑Fax‑Retry is a modular Python service designed to send a PDF fax and automatically retry failed attempts. The system is composed of four core modules.

## 1. config.py — Configuration Layer
Loads and validates all runtime settings:
- Fax number
- PDF file path
- Retry limit
- Delay strategy
- API credentials
- Logging options

Configuration may come from environment variables, a .env file, or defaults during early development.

## 2. fax_api.py — Fax Provider Abstraction
A wrapper around the fax provider’s API.

Responsibilities:
- Send a fax request
- Return a normalized success/failure response
- Handle provider-specific errors
- Allow easy swapping of providers

A mock provider is used during early development.

## 3. retry_engine.py — Retry Logic
Controls retry behavior when a fax fails.

Responsibilities:
- Attempt fax send
- Log each attempt
- Apply delay strategy between attempts
- Stop after success or max retries
- Return final status to the caller

The retry engine is provider‑agnostic.

## 4. main.py — Entry Point
A simple script demonstrating how to run the service.

Responsibilities:
- Load configuration
- Call the retry engine
- Output final result
- Serve as a reference for future CLI or automation scripts

## Data Flow

main.py  
→ config.py (loads settings)  
→ retry_engine.py (manages attempts)  
→ fax_api.py (sends fax via provider)  
→ logs/ (records attempt history)

## Logging
The system logs:
- Timestamp
- Attempt number
- Provider response
- Success/failure
- Final outcome

Logs are stored in a dedicated directory and may later support rotation or JSON formatting.

