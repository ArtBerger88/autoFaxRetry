from pathlib import Path

from src import main as main_module


def make_base_cfg(tmp_path):
    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%mock\n")
    return {
        "phaxio_api_key": "k",
        "phaxio_api_secret": "s",
        "fax_number": "1112223333",
        "pdf_path": str(pdf),
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": str(tmp_path / "logs" / "fax.log"),
    }


def test_main_applies_cli_overrides(monkeypatch, tmp_path):
    cfg = make_base_cfg(tmp_path)
    override_pdf = tmp_path / "override.pdf"
    override_pdf.write_bytes(b"%PDF-1.4\n%override\n")

    captured = {}

    monkeypatch.setattr("src.main.config_module.load_config", lambda _: dict(cfg))

    class FakeApi:
        def __init__(self, key, secret):
            captured["api_key"] = key
            captured["api_secret"] = secret

    monkeypatch.setattr("src.main.PhaxioAPI", FakeApi)

    def fake_run_retry_loop(api, run_cfg):
        captured["cfg"] = run_cfg
        return True

    monkeypatch.setattr("src.main.run_retry_loop", fake_run_retry_loop)

    rc = main_module.main(
        [
            "--config",
            "config/settings.json",
            "--fax-number",
            "9998887777",
            "--pdf-path",
            str(override_pdf),
            "--max-attempts",
            "5",
            "--delay-seconds",
            "2.5",
            "--log-file",
            str(tmp_path / "custom" / "log.jsonl"),
        ]
    )

    assert rc == 0
    assert captured["api_key"] == "k"
    assert captured["api_secret"] == "s"
    assert captured["cfg"]["fax_number"] == "9998887777"
    assert captured["cfg"]["pdf_path"] == str(override_pdf)
    assert captured["cfg"]["max_attempts"] == 5
    assert captured["cfg"]["delay_seconds"] == 2.5
    assert captured["cfg"]["log_file"].endswith("log.jsonl")


def test_main_returns_error_for_invalid_override(monkeypatch, tmp_path, capsys):
    cfg = make_base_cfg(tmp_path)
    missing_pdf = tmp_path / "missing.pdf"

    monkeypatch.setattr("src.main.config_module.load_config", lambda _: dict(cfg))

    rc = main_module.main(["--pdf-path", str(missing_pdf)])
    err = capsys.readouterr().err

    assert rc == 2
    assert "Configuration error" in err


def test_main_returns_failure_exit_code(monkeypatch, tmp_path):
    cfg = make_base_cfg(tmp_path)

    monkeypatch.setattr("src.main.config_module.load_config", lambda _: dict(cfg))
    monkeypatch.setattr("src.main.run_retry_loop", lambda *_: False)

    class DummyApi:
        def __init__(self, *args):
            pass

    monkeypatch.setattr("src.main.PhaxioAPI", DummyApi)

    rc = main_module.main([])
    assert rc == 1
