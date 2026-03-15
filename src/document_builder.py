import tempfile
from pathlib import Path
from typing import Optional


def _import_pdf_dependencies():
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise RuntimeError(
            "PDF merge support requires 'pypdf'. Install it with: pip install pypdf"
        ) from exc

    return PdfReader, PdfWriter


def _import_cover_text_dependencies():
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError(
            "Cover page generation requires 'reportlab'. Install it with: pip install reportlab"
        ) from exc

    return letter, canvas


def _write_cover_page_pdf(output_path: Path, cover_text: str) -> None:
    letter, canvas = _import_cover_text_dependencies()

    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    pdf.setTitle("Fax Cover Page")

    y = height - 72
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, y, "Fax Cover Page")
    y -= 28

    pdf.setFont("Helvetica", 11)
    for raw_line in cover_text.splitlines() or [cover_text]:
        line = raw_line.strip()
        if not line:
            y -= 14
            continue
        if y < 72:
            pdf.showPage()
            y = height - 72
            pdf.setFont("Helvetica", 11)
        pdf.drawString(72, y, line)
        y -= 14

    pdf.save()


def prepare_fax_document(
    pdf_paths: list[str],
    cover_page_text: Optional[str] = None,
    cover_page_file: Optional[str] = None,
):
    """Return (pdf_path_to_send, temp_dir_or_none) for the fax submission."""
    if not pdf_paths:
        raise ValueError("At least one PDF path is required")

    cleaned_paths = [str(Path(p)) for p in pdf_paths]
    has_cover_text = bool(cover_page_text and cover_page_text.strip())
    has_cover_file = bool(cover_page_file and str(cover_page_file).strip())

    if has_cover_text and has_cover_file:
        raise ValueError("Provide either cover_page_text or cover_page_file, not both")

    if has_cover_file:
        cover_path_obj = Path(str(cover_page_file))
        if not cover_path_obj.exists() or not cover_path_obj.is_file():
            raise ValueError(f"cover_page_file does not exist or is not a file: {cover_page_file}")
        cleaned_cover_file = str(cover_path_obj)
    else:
        cleaned_cover_file = None

    if len(cleaned_paths) == 1 and not has_cover_text and not has_cover_file:
        return cleaned_paths[0], None

    PdfReader, PdfWriter = _import_pdf_dependencies()

    temp_dir = tempfile.TemporaryDirectory(prefix="autofax_merge_")
    temp_root = Path(temp_dir.name)
    merged_path = temp_root / "fax_payload.pdf"

    writer = PdfWriter()

    if has_cover_text:
        cover_pdf_path = temp_root / "cover_page.pdf"
        _write_cover_page_pdf(cover_pdf_path, str(cover_page_text))
        cover_reader = PdfReader(str(cover_pdf_path))
        for page in cover_reader.pages:
            writer.add_page(page)
    elif has_cover_file and cleaned_cover_file is not None:
        cover_reader = PdfReader(cleaned_cover_file)
        for page in cover_reader.pages:
            writer.add_page(page)

    for source in cleaned_paths:
        reader = PdfReader(source)
        for page in reader.pages:
            writer.add_page(page)

    with merged_path.open("wb") as out_file:
        writer.write(out_file)

    return str(merged_path), temp_dir