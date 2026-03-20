from pathlib import Path

from src import main as main_module


def make_base_cfg(tmp_path):
    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(b"%PDF-1.4\n%mock\n")
    return {
        "sinch_project_id": "proj-123",
        "sinch_key_id": "k",
        "sinch_key_secret": "s",
        "sinch_from_number": "+13526967007",
        "fax_number": "+1112223333",
        "pdf_path": str(pdf),
        "max_attempts": 3,
        "delay_seconds": 1,
        "log_file": str(tmp_path / "logs" / "fax.log"),
    }


def test_main_applies_cli_overrides(monkeypatch, tmp_path):
    cfg = make_base_cfg(tmp_path)
    override_pdf_a = tmp_path / "override_a.pdf"
    override_pdf_b = tmp_path / "override_b.pdf"
    override_pdf_a.write_bytes(b"%PDF-1.4\n%override-a\n")
    override_pdf_b.write_bytes(b"%PDF-1.4\n%override-b\n")
    cover_pdf = tmp_path / "cover.pdf"
    cover_pdf.write_bytes(b"%PDF-1.4\n%cover\n")

    captured = {}

    monkeypatch.setattr("src.main.config_module.load_config", lambda _: dict(cfg))

    class FakeApi:
        def __init__(self, project_id, key_id, key_secret, from_number, base_url):
            captured["project_id"] = project_id
            captured["key_id"] = key_id
            captured["key_secret"] = key_secret
            captured["from_number"] = from_number
            captured["base_url"] = base_url

    monkeypatch.setattr("src.main.SinchFaxAPI", FakeApi)

    def fake_prepare(pdf_paths, cover_page_text, cover_page_file):
        captured["prepared_pdf_paths"] = pdf_paths
        captured["cover_page_text"] = cover_page_text
        captured["cover_page_file"] = cover_page_file
        return str(override_pdf_a), None

    monkeypatch.setattr("src.main.prepare_fax_document", fake_prepare)

    def fake_run_retry_loop(api, run_cfg):
        captured["cfg"] = run_cfg
        return True

    monkeypatch.setattr("src.main.run_retry_loop", fake_run_retry_loop)

    rc = main_module.main(
        [
            "--config",
            "config/settings.json",
            "--fax-number",
            "+19998887777",
            "--pdf-path",
            str(override_pdf_a),
            "--pdf-path",
            str(override_pdf_b),
            "--max-attempts",
            "5",
            "--delay-seconds",
            "2.5",
            "--status-poll-timeout-seconds",
            "180",
            "--log-file",
            str(tmp_path / "custom" / "log.jsonl"),
            "--cover-page-file",
            str(cover_pdf),
        ]
    )

    assert rc == 0
    assert captured["project_id"] == "proj-123"
    assert captured["key_id"] == "k"
    assert captured["key_secret"] == "s"
    assert captured["from_number"] == "+13526967007"
    assert captured["base_url"] == "https://fax.api.sinch.com"
    assert captured["cfg"]["fax_number"] == "+19998887777"
    assert captured["cfg"]["pdf_path"] == str(override_pdf_a)
    assert captured["prepared_pdf_paths"] == [str(override_pdf_a), str(override_pdf_b)]
    assert captured["cover_page_text"] is None
    assert captured["cover_page_file"] == str(cover_pdf)
    assert captured["cfg"]["max_attempts"] == 5
    assert captured["cfg"]["delay_seconds"] == 2.5
    assert captured["cfg"]["status_poll_timeout_seconds"] == 180.0
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
    monkeypatch.setattr("src.main.prepare_fax_document", lambda p, c, f: (p[0], None))

    class DummyApi:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr("src.main.SinchFaxAPI", DummyApi)

    rc = main_module.main([])
    assert rc == 1


def test_main_runs_pdf_optimizer_when_enabled(monkeypatch, tmp_path):
    cfg = make_base_cfg(tmp_path)
    cfg["auto_optimize_pdf_before_send"] = True
    cfg["target_pdf_bytes"] = 120000
    cfg["gs_command"] = "gswin64c"
    cfg["optimized_preview_pdf_path"] = str(tmp_path / "output" / "preview.pdf")

    prepared = tmp_path / "prepared.pdf"
    prepared.write_bytes(b"%PDF-1.4\n%prepared\n")
    optimized = tmp_path / "optimized.pdf"
    optimized.write_bytes(b"%PDF-1.4\n%optimized\n")

    captured = {}

    monkeypatch.setattr("src.main.config_module.load_config", lambda _: dict(cfg))
    monkeypatch.setattr("src.main.prepare_fax_document", lambda p, c, f: (str(prepared), None))

    def fake_optimize(path, target_bytes, gs_command):
        captured["optimize_called"] = True
        captured["path"] = path
        captured["target_bytes"] = target_bytes
        captured["gs_command"] = gs_command
        return str(optimized), None, "optimized"

    monkeypatch.setattr("src.main.optimize_pdf_for_send", fake_optimize)

    class DummyApi:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr("src.main.SinchFaxAPI", DummyApi)

    def fake_run_retry_loop(api, run_cfg):
        captured["pdf_path"] = run_cfg["pdf_path"]
        return True

    monkeypatch.setattr("src.main.run_retry_loop", fake_run_retry_loop)

    rc = main_module.main([])
    assert rc == 0
    assert captured["optimize_called"] is True
    assert captured["path"] == str(prepared)
    assert captured["target_bytes"] == 120000
    assert captured["gs_command"] == "gswin64c"
    assert captured["pdf_path"] == str(optimized)
    assert Path(cfg["optimized_preview_pdf_path"]).exists()