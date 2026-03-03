import os

from src.retry_controller import run_retry_loop


def test_run_retry_loop_logs_and_stops(tmp_path, monkeypatch, capsys):
    """Verify that the retry loop writes to the log file and stops on success."""

    # monkeypatch send_fax_once used by retry_controller
    calls = []

    def fake_send(api, fax, pdf):
        calls.append(1)
        if len(calls) < 2:
            return {"success": False, "message": "fail"}
        return {"success": True, "message": "ok"}

    monkeypatch.setattr("src.retry_controller.send_fax_once", fake_send)

    config = {
        "fax_number": "123",
        "pdf_path": "file.pdf",
        "max_attempts": 3,
        "delay_seconds": 0,
        "log_file": str(tmp_path / "log.txt"),
    }
    run_retry_loop(None, config)
    contents = open(config["log_file"]).read()
    assert "Attempt 1" in contents
    assert "Attempt 2" in contents

    captured = capsys.readouterr()
    assert "Fax delivered on attempt 2" in captured.out
