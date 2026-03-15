from src.document_builder import prepare_fax_document


def test_prepare_single_document_passthrough(tmp_path):
    one_pdf = tmp_path / "one.pdf"
    one_pdf.write_bytes(b"%PDF-1.4\n%single\n")

    out_path, temp_dir = prepare_fax_document([str(one_pdf)], None)

    assert out_path == str(one_pdf)
    assert temp_dir is None


def test_prepare_requires_dependency_for_merge(monkeypatch, tmp_path):
    one_pdf = tmp_path / "one.pdf"
    two_pdf = tmp_path / "two.pdf"
    one_pdf.write_bytes(b"%PDF-1.4\n%one\n")
    two_pdf.write_bytes(b"%PDF-1.4\n%two\n")

    def fake_imports():
        raise RuntimeError("PDF merge support requires 'pypdf'.")

    monkeypatch.setattr("src.document_builder._import_pdf_dependencies", fake_imports)

    try:
        prepare_fax_document([str(one_pdf), str(two_pdf)], None)
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "pypdf" in str(exc)


def test_prepare_requires_dependency_for_cover_page(monkeypatch, tmp_path):
    one_pdf = tmp_path / "one.pdf"
    one_pdf.write_bytes(b"%PDF-1.4\n%one\n")

    def fake_imports():
        raise RuntimeError("Cover page generation requires 'reportlab'.")

    monkeypatch.setattr("src.document_builder._import_pdf_dependencies", fake_imports)

    try:
        prepare_fax_document([str(one_pdf)], "Cover text")
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "reportlab" in str(exc)


def test_prepare_rejects_missing_cover_page_file(tmp_path):
    one_pdf = tmp_path / "one.pdf"
    one_pdf.write_bytes(b"%PDF-1.4\n%one\n")

    missing_cover = tmp_path / "missing_cover.pdf"
    try:
        prepare_fax_document([str(one_pdf)], None, str(missing_cover))
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "cover_page_file" in str(exc)


def test_prepare_rejects_text_and_file_cover_together(tmp_path):
    one_pdf = tmp_path / "one.pdf"
    cover_pdf = tmp_path / "cover.pdf"
    one_pdf.write_bytes(b"%PDF-1.4\n%one\n")
    cover_pdf.write_bytes(b"%PDF-1.4\n%cover\n")

    try:
        prepare_fax_document([str(one_pdf)], "hello", str(cover_pdf))
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "either cover_page_text or cover_page_file" in str(exc)
