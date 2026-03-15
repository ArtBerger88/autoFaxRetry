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


def test_load_config_file_only(tmp_path):
    pdf_path, log_file = make_paths(tmp_path)
    data = {
        "phaxio_api_key": "k",
        "phaxio_api_secret": "s",
        "fax_number": "123",
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
        "phaxio_api_key": "k",
        "phaxio_api_secret": "s",
        "fax_number": "123",
        "pdf_path": pdf_path,
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": log_file,
    }
    cfg_file = make_temp_config(tmp_path, data)
    monkeypatch.setenv("FAX_NUMBER", "999")
    monkeypatch.setenv("MAX_ATTEMPTS", "5")
    cfg = config_module.load_config(cfg_file)
    assert cfg["fax_number"] == "999"
    assert cfg["max_attempts"] == 5


def test_missing_keys(tmp_path):
    data = {"fax_number": "123"}
    cfg_file = make_temp_config(tmp_path, data)
    try:
        config_module.load_config(cfg_file)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "Missing config keys" in str(e)


def test_invalid_types(tmp_path):
    data = {
        "phaxio_api_key": "k",
        "phaxio_api_secret": "s",
        "fax_number": "123",
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
