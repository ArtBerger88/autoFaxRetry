from pathlib import Path
import time
from typing import Any, Dict, Optional

import requests


class SinchFaxAPI:
    """Small wrapper around the Sinch Fax REST API."""

    def __init__(
        self,
        project_id: str,
        key_id: str,
        key_secret: str,
        base_url: str = "https://fax.api.sinch.com",
        timeout: tuple[float, float] = (10.0, 30.0),
        network_retries: int = 2,
        network_retry_backoff: float = 1.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.project_id = project_id
        self.key_id = key_id
        self.key_secret = key_secret
        self.timeout = timeout
        self.network_retries = max(0, int(network_retries))
        self.network_retry_backoff = max(0.0, float(network_retry_backoff))

    @property
    def _project_base(self) -> str:
        return f"{self.base_url}/v3/projects/{self.project_id}"

    @staticmethod
    def _safe_json(response: requests.Response) -> Optional[Dict[str, Any]]:
        try:
            payload = response.json()
            return payload if isinstance(payload, dict) else None
        except ValueError:
            return None

    @staticmethod
    def _is_transient_network_error(exc: requests.RequestException) -> bool:
        # SSL EOF and similar transport failures can be transient and benefit from
        # a short in-call retry before counting as a full retry-loop failure.
        if isinstance(
            exc,
            (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.SSLError,
            ),
        ):
            return True
        return "SSLEOFError" in str(exc)

    def send_fax(self, to_number: str, pdf_path: str) -> Dict[str, Any]:
        """Submit a fax and return a normalized result dictionary."""
        url = f"{self._project_base}/faxes"
        file_path = Path(pdf_path)

        if not file_path.exists() or not file_path.is_file():
            return {
                "success": False,
                "fax_id": None,
                "message": f"PDF file not found: {pdf_path}",
                "error_code": "file_not_found",
                "status_code": None,
            }

        response: Optional[requests.Response] = None
        last_network_error: Optional[requests.RequestException] = None

        for network_attempt in range(1, self.network_retries + 2):
            try:
                with file_path.open("rb") as file_obj:
                    response = requests.post(
                        url,
                        auth=(self.key_id, self.key_secret),
                        files={"file": (file_path.name, file_obj, "application/pdf")},
                        data={"to": to_number},
                        timeout=self.timeout,
                        headers={"Connection": "close"},
                    )
                break
            except requests.RequestException as exc:
                last_network_error = exc
                if network_attempt > self.network_retries or not self._is_transient_network_error(exc):
                    break
                if self.network_retry_backoff > 0:
                    time.sleep(self.network_retry_backoff * network_attempt)
            except OSError as exc:
                return {
                    "success": False,
                    "fax_id": None,
                    "message": f"Failed to open PDF file: {exc}",
                    "error_code": "file_read_error",
                    "status_code": None,
                }

        if response is None:
            if isinstance(last_network_error, requests.exceptions.SSLError) or (
                last_network_error is not None and "SSLEOFError" in str(last_network_error)
            ):
                message = (
                    f"Network SSL handshake error while submitting fax: {last_network_error}"
                )
            else:
                message = f"Network error while submitting fax: {last_network_error}"
            return {
                "success": False,
                "fax_id": None,
                "message": message,
                "error_code": "network_error",
                "status_code": None,
            }

        payload = self._safe_json(response)
        if payload is None:
            if response.status_code in (401, 403):
                return {
                    "success": False,
                    "fax_id": None,
                    "message": (
                        "Unauthorized by provider (HTTP "
                        f"{response.status_code}). Verify sinch_project_id, "
                        "sinch_key_id, and sinch_key_secret belong to the same project."
                    ),
                    "error_code": "http_error",
                    "status_code": response.status_code,
                }
            return {
                "success": False,
                "fax_id": None,
                "message": "Provider returned a non-JSON response.",
                "error_code": "invalid_response",
                "status_code": response.status_code,
            }

        if not response.ok:
            return {
                "success": False,
                "fax_id": None,
                "message": str(
                    payload.get("message")
                    or payload.get("errorMessage")
                    or "Provider HTTP error."
                ),
                "error_code": "http_error",
                "status_code": response.status_code,
            }

        fax_id = payload.get("id")
        if fax_id:
            return {
                "success": True,
                "fax_id": fax_id,
                "message": "Fax submitted successfully.",
                "error_code": None,
                "status_code": response.status_code,
            }

        return {
            "success": False,
            "fax_id": None,
            "message": str(
                payload.get("message")
                or payload.get("errorMessage")
                or "Unknown provider error."
            ),
            "error_code": "provider_error",
            "status_code": response.status_code,
        }

    def get_fax_status_details(self, fax_id: Any) -> Dict[str, Any]:
        """Return normalized fax status details for diagnostics and retry logic."""
        url = f"{self._project_base}/faxes/{fax_id}"

        try:
            response = requests.get(
                url,
                auth=(self.key_id, self.key_secret),
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            return {
                "status": "failure",
                "status_code": None,
                "provider_status": None,
                "error_reason": f"status_request_error: {exc}",
            }

        payload = self._safe_json(response)
        if payload is None:
            return {
                "status": "failure",
                "status_code": response.status_code,
                "provider_status": None,
                "error_reason": "status_invalid_json",
            }

        if not response.ok:
            return {
                "status": "failure",
                "status_code": response.status_code,
                "provider_status": str(payload.get("status", "")).upper() or None,
                "error_reason": str(
                    payload.get("message")
                    or payload.get("errorMessage")
                    or "status_http_error"
                ),
            }

        status = str(payload.get("status", "")).upper()
        if status == "COMPLETED":
            return {
                "status": "success",
                "status_code": response.status_code,
                "provider_status": status,
                "error_reason": None,
            }
        if status == "FAILURE":
            return {
                "status": "failure",
                "status_code": response.status_code,
                "provider_status": status,
                "error_reason": str(
                    payload.get("failureReason")
                    or payload.get("message")
                    or payload.get("errorMessage")
                    or "provider_reported_failure"
                ),
            }

        return {
            "status": "in_progress",
            "status_code": response.status_code,
            "provider_status": status or None,
            "error_reason": None,
        }

    def get_fax_status(self, fax_id: Any) -> str:
        """Return one of: success, failure, in_progress."""
        details = self.get_fax_status_details(fax_id)
        return str(details.get("status") or "failure")


# Backwards-compatible alias while callers migrate naming.
PhaxioAPI = SinchFaxAPI