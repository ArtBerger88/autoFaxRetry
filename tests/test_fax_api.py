import requests

from src.fax_api import SinchFaxAPI


class FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=None):
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        if self._json_error is not None:
            raise self._json_error
        return self._payload


def make_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%mock\n")
    return pdf_path


def test_send_fax_success(monkeypatch, tmp_path):
    pdf_path = make_pdf(tmp_path)

    def fake_post(*args, **kwargs):
        return FakeResponse(
            status_code=200,
            payload={"id": "01HDF5S9P29WC29J578J8EKC1C", "status": "IN_PROGRESS"},
        )

    monkeypatch.setattr("src.fax_api.requests.post", fake_post)
    api = SinchFaxAPI("project", "k", "s")

    result = api.send_fax("+15551234567", str(pdf_path))
    assert result["success"] is True
    assert result["fax_id"] == "01HDF5S9P29WC29J578J8EKC1C"
    assert result["error_code"] is None
    assert result["status_code"] == 200


def test_send_fax_missing_pdf(tmp_path):
    api = SinchFaxAPI("project", "k", "s")
    result = api.send_fax("+15551234567", str(tmp_path / "missing.pdf"))

    assert result["success"] is False
    assert result["error_code"] == "file_not_found"


def test_send_fax_network_error(monkeypatch, tmp_path):
    pdf_path = make_pdf(tmp_path)

    def fake_post(*args, **kwargs):
        raise requests.Timeout("timed out")

    monkeypatch.setattr("src.fax_api.requests.post", fake_post)
    api = SinchFaxAPI("project", "k", "s")

    result = api.send_fax("+15551234567", str(pdf_path))
    assert result["success"] is False
    assert result["error_code"] == "network_error"
    assert result["status_code"] is None


def test_send_fax_non_json_response(monkeypatch, tmp_path):
    pdf_path = make_pdf(tmp_path)

    def fake_post(*args, **kwargs):
        return FakeResponse(status_code=502, json_error=ValueError("bad json"))

    monkeypatch.setattr("src.fax_api.requests.post", fake_post)
    api = SinchFaxAPI("project", "k", "s")

    result = api.send_fax("+15551234567", str(pdf_path))
    assert result["success"] is False
    assert result["error_code"] == "invalid_response"
    assert result["status_code"] == 502


def test_send_fax_http_error_with_provider_message(monkeypatch, tmp_path):
    pdf_path = make_pdf(tmp_path)

    def fake_post(*args, **kwargs):
        return FakeResponse(
            status_code=401,
            payload={"message": "Invalid credentials"},
        )

    monkeypatch.setattr("src.fax_api.requests.post", fake_post)
    api = SinchFaxAPI("project", "k", "s")

    result = api.send_fax("+15551234567", str(pdf_path))
    assert result["success"] is False
    assert result["error_code"] == "http_error"
    assert result["message"] == "Invalid credentials"
    assert result["status_code"] == 401


def test_get_fax_status_success_mapping(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse(status_code=200, payload={"status": "COMPLETED"})

    monkeypatch.setattr("src.fax_api.requests.get", fake_get)
    api = SinchFaxAPI("project", "k", "s")

    assert api.get_fax_status("123") == "success"


def test_get_fax_status_failure_on_request_exception(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("no route")

    monkeypatch.setattr("src.fax_api.requests.get", fake_get)
    api = SinchFaxAPI("project", "k", "s")

    assert api.get_fax_status("123") == "failure"


def test_get_fax_status_in_progress_mapping(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse(status_code=200, payload={"status": "IN_PROGRESS"})

    monkeypatch.setattr("src.fax_api.requests.get", fake_get)
    api = SinchFaxAPI("project", "k", "s")

    assert api.get_fax_status("123") == "in_progress"