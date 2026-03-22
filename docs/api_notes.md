# API Notes (Sinch Fax)

## Submission endpoint
- `POST /v3/projects/{project_id}/faxes`

Request fields used by this service:
- `to` (required)
- `file` (multipart PDF)
- `from` (optional, via `sinch_from_number`)
- `imageResolution` (optional, via `sinch_image_resolution`)

## Status endpoint
- `GET /v3/projects/{project_id}/faxes/{fax_id}`

Normalized attempt outcomes used by app logic:
- `success`
- `failure`
- `in_progress`

Provider status and failure details are captured per attempt in logs:
- `provider_status`
- `error_reason`
- `status_code`
- `fax_id`

## Operational notes
- `sinch_image_resolution: normal` is currently recommended for better route compatibility and faster handshake outcomes on unstable destinations.
- Repeated `FAILURE` with `Disconnected after permitted retries` indicates downstream/session instability, not startup config/auth failure.
- Runtime auth diagnostics are logged as credential fingerprints (`key_fp`, `secret_fp`) and can be used to verify the active auth context without exposing secrets.
