from pathlib import Path
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
    ):
        self.base_url = base_url.rstrip("/")
        self.project_id = project_id
        self.key_id = key_id
        self.key_secret = key_secret
        self.timeout = timeout

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

        try:
            with file_path.open("rb") as file_obj:
                response = requests.post(
                    url,
                    auth=(self.key_id, self.key_secret),
                    files={"file": (file_path.name, file_obj, "application/pdf")},
                    data={"to": to_number},
                    timeout=self.timeout,
                )
        except requests.RequestException as exc:
            return {
                "success": False,
                "fax_id": None,
                "message": f"Network error while submitting fax: {exc}",
                "error_code": "network_error",
                "status_code": None,
            }
        except OSError as exc:
            return {
                "success": False,
                "fax_id": None,
                "message": f"Failed to open PDF file: {exc}",
                "error_code": "file_read_error",
                "status_code": None,
            }

        payload = self._safe_json(response)
        if payload is None:
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

    def get_fax_status(self, fax_id: Any) -> str:
        """Return one of: success, failure, in_progress."""
        url = f"{self._project_base}/faxes/{fax_id}"

        try:
            response = requests.get(
                url,
                auth=(self.key_id, self.key_secret),
                timeout=self.timeout,
            )
        except requests.RequestException:
            return "failure"

        payload = self._safe_json(response)
        if payload is None or not response.ok:
            return "failure"

        status = str(payload.get("status", "")).upper()
        if status == "COMPLETED":
            return "success"
        if status == "FAILURE":
            return "failure"
        return "in_progress"


# Backwards-compatible alias while callers migrate naming.
PhaxioAPI = SinchFaxAPI