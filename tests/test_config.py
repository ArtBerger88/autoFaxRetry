import json
from pathlib import Path

from src import config as config_module


def make_temp_config(tmp_path, data):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps(data))
    return p


def make_paths(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%mock\n")
    log_file = tmp_path / "logs" / "fax.log"
    return str(pdf_path), str(log_file)


def test_load_config_file_only(tmp_path, monkeypatch):
    for env_key in config_module._ENV_OVERRIDES:
        monkeypatch.delenv(env_key, raising=False)

    pdf_path, log_file = make_paths(tmp_path)
    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_path": pdf_path,
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
    }
    cfg_file = make_temp_config(tmp_path, data)
    cfg = config_module.load_config(cfg_file)
    assert cfg == data


def test_env_overrides(tmp_path, monkeypatch):
    pdf_path, log_file = make_paths(tmp_path)
    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_path": pdf_path,
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
    }
    cfg_file = make_temp_config(tmp_path, data)
    monkeypatch.setenv("FAX_NUMBER", "+999")
    monkeypatch.setenv("MAX_ATTEMPTS", "5")
    cfg = config_module.load_config(cfg_file)
    assert cfg["fax_number"] == "+999"
    assert cfg["max_attempts"] == 5


def test_missing_keys(tmp_path):
    data = {"fax_number": "+123"}
    cfg_file = make_temp_config(tmp_path, data)
    try:
        config_module.load_config(cfg_file)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "Missing config keys" in str(e)


def test_invalid_types(tmp_path):
    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_path": "file.pdf",
        "max_attempts": "notint",
        "delay_seconds": -1,
        "log_file": "log.txt",
    }
    cfg_file = make_temp_config(tmp_path, data)
    try:
        config_module.load_config(cfg_file)
        assert False
    except ValueError:
        pass


def test_pdf_paths_list_is_supported(tmp_path):
    pdf1, log_file = make_paths(tmp_path)
    pdf2 = tmp_path / "sample2.pdf"
    pdf2.write_bytes(b"%PDF-1.4\n%mock2\n")

    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_paths": [pdf1, str(pdf2)],
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
        "cover_page_text": "Hello",
    }
    cfg_file = make_temp_config(tmp_path, data)
    cfg = config_module.load_config(cfg_file)

    assert cfg["pdf_paths"] == [pdf1, str(pdf2)]
    assert cfg["cover_page_text"] == "Hello"


def test_cover_page_text_must_be_string(tmp_path):
    pdf_path, log_file = make_paths(tmp_path)
    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_path": pdf_path,
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
        "cover_page_text": 123,
    }
    cfg_file = make_temp_config(tmp_path, data)

    try:
        config_module.load_config(cfg_file)
        assert False
    except ValueError as exc:
        assert "cover_page_text" in str(exc)


def test_cover_page_file_validation(tmp_path):
    pdf_path, log_file = make_paths(tmp_path)
    cover_pdf = tmp_path / "cover.pdf"
    cover_pdf.write_bytes(b"%PDF-1.4\n%cover\n")

    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_path": pdf_path,
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
        "cover_page_file": str(cover_pdf),
    }
    cfg_file = make_temp_config(tmp_path, data)
    cfg = config_module.load_config(cfg_file)
    assert cfg["cover_page_file"] == str(cover_pdf)


def test_cover_page_text_and_file_are_mutually_exclusive(tmp_path):
    pdf_path, log_file = make_paths(tmp_path)
    cover_pdf = tmp_path / "cover.pdf"
    cover_pdf.write_bytes(b"%PDF-1.4\n%cover\n")

    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_path": pdf_path,
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
        "cover_page_text": "hello",
        "cover_page_file": str(cover_pdf),
    }
    cfg_file = make_temp_config(tmp_path, data)

    try:
        config_module.load_config(cfg_file)
        assert False
    except ValueError as exc:
        assert "either cover_page_text or cover_page_file" in str(exc)


def test_optimization_env_overrides(tmp_path, monkeypatch):
    pdf_path, log_file = make_paths(tmp_path)
    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_path": pdf_path,
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
    }
    cfg_file = make_temp_config(tmp_path, data)

    monkeypatch.setenv("AUTO_OPTIMIZE_PDF_BEFORE_SEND", "true")
    monkeypatch.setenv("TARGET_PDF_BYTES", "120000")
    monkeypatch.setenv("GS_COMMAND", "gswin64c")
    monkeypatch.setenv("STATUS_POLL_TIMEOUT_SECONDS", "180")
    monkeypatch.setenv("OPTIMIZED_PREVIEW_PDF_PATH", str(tmp_path / "preview" / "last.pdf"))

    cfg = config_module.load_config(cfg_file)
    assert cfg["auto_optimize_pdf_before_send"] is True
    assert cfg["target_pdf_bytes"] == 120000
    assert cfg["gs_command"] == "gswin64c"
    assert cfg["status_poll_timeout_seconds"] == 180.0
    assert cfg["optimized_preview_pdf_path"].endswith("last.pdf")


def test_invalid_target_pdf_bytes(tmp_path):
    pdf_path, log_file = make_paths(tmp_path)
    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_path": pdf_path,
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
        "target_pdf_bytes": 0,
    }
    cfg_file = make_temp_config(tmp_path, data)

    try:
        config_module.load_config(cfg_file)
        assert False
    except ValueError as exc:
        assert "target_pdf_bytes" in str(exc)


def test_invalid_status_poll_timeout_seconds(tmp_path):
    pdf_path, log_file = make_paths(tmp_path)
    data = {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "fax_number": "+123",
        "pdf_path": pdf_path,
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
        "status_poll_timeout_seconds": 0,
    }
    cfg_file = make_temp_config(tmp_path, data)

    try:
        config_module.load_config(cfg_file)
        assert False
    except ValueError as exc:
        assert "status_poll_timeout_seconds" in str(exc)