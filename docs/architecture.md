# Auto-fax-retry — Simplified Architecture

Goal: reliably send faxes, persist status/artifacts, and retry transient failures with minimal components.

Components
- API (Webhooks): accept send requests and provider callbacks; validate and create fax record.
- Storage: blob store for documents/receipts; SQL for fax metadata and status.
- Queue: simple message queue (RabbitMQ / Redis Streams / SQS) for send jobs and delayed retries.
- Worker: stateless sender that consumes jobs, calls provider, updates DB, stores receipts.
- UI (optional): simple dashboard for viewing/cancelling jobs.
- Monitoring: logs + basic metrics (success, retries, failures).

Core principles
- Idempotency: use a unique fax_id for all operations.
- Single source of truth: DB stores canonical status; queue only drives work.
- Simple retry: worker increments retry_count and re-enqueues with delay; use exponential backoff and a max attempts limit.
- Dead-letter: move permanently failed items to DLQ for manual review.

Typical flow
1. Client → API: create fax record, upload document to Storage, enqueue send job.
2. Worker consumes job → call Fax Provider.
3. On success: update DB status to SENT, store receipt.
4. On transient failure: increment retry_count; if < max, re-enqueue with delay; else move to DLQ and mark FAILED.
5. Provider callback → API reconciles status and cancels pending retries if needed.

Retry policy (example)
- Backoff: delay = base_delay * 2^(retry_count-1) (e.g., base_delay = 30s)
- Max attempts: 5
- Immediate requeue on transient network/provider errors; final failures go to DLQ.

Minimal reliability tips
- Persist DB changes before enqueuing (or use outbox pattern).
- Authenticate provider callbacks and validate fax_id.
- Expose retry_count and next_attempt in DB for visibility.