import json

from src.utils.logger import log, log_attempt


def read_log(path):
    with open(path, "r") as f:
        return f.read()


def test_log_writes_message(tmp_path):
    log_file = tmp_path / "log.txt"
    log("hello world", log_file=str(log_file))
    contents = read_log(str(log_file))
    payload = json.loads(contents.strip())
    assert payload["message"] == "hello world"
    assert payload["event"] == "message"


def test_log_attempt_formats_correctly(tmp_path):
    log_file = tmp_path / "log.txt"
    result = {"success": True, "message": "ok"}
    log_attempt(str(log_file), 3, result)
    contents = read_log(str(log_file))
    payload = json.loads(contents.strip())
    assert payload["event"] == "attempt"
    assert payload["attempt"] == 3
    assert payload["status"] == "SUCCESS"
    assert "Attempt 3" in payload["summary"]
