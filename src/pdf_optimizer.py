import shutil
import subprocess
import tempfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Tuple


def _find_ghostscript(configured_command: Optional[str] = None) -> Optional[str]:
	if configured_command:
		return configured_command

	for candidate in ("gswin64c", "gswin32c", "gs"):
		resolved = shutil.which(candidate)
		if resolved:
			return resolved
	return None


def _optimize_once(gs_command: str, source: Path, output: Path, profile: str) -> bool:
	cmd = [
		gs_command,
		"-sDEVICE=pdfwrite",
		"-dCompatibilityLevel=1.4",
		"-dNOPAUSE",
		"-dBATCH",
		"-dSAFER",
		"-dQUIET",
		f"-dPDFSETTINGS={profile}",
		"-dDetectDuplicateImages=true",
		"-dCompressFonts=true",
		"-dSubsetFonts=true",
		f"-sOutputFile={str(output)}",
		str(source),
	]

	proc = subprocess.run(
		cmd,
		capture_output=True,
		text=True,
		check=False,
	)
	return proc.returncode == 0 and output.exists() and output.stat().st_size > 0


def optimize_pdf_for_send(
	pdf_path: str,
	target_bytes: int,
	gs_command: Optional[str] = None,
) -> Tuple[str, Optional[TemporaryDirectory], str]:
	"""Try to optimize a PDF file and return (path, temp_dir, status_message).

	When optimization cannot run or does not improve size, the original path is
	returned and temp_dir is ``None``.
	"""
	source = Path(pdf_path)
	if not source.exists() or not source.is_file():
		return pdf_path, None, "PDF optimization skipped: source PDF does not exist."

	original_size = source.stat().st_size
	if original_size <= target_bytes:
		return (
			pdf_path,
			None,
			f"PDF optimization skipped: size {original_size} B already <= target {target_bytes} B.",
		)

	resolved_gs = _find_ghostscript(gs_command)
	if not resolved_gs:
		return (
			pdf_path,
			None,
			"PDF optimization skipped: Ghostscript not found (gswin64c/gswin32c/gs).",
		)

	temp_dir = tempfile.TemporaryDirectory(prefix="autofax_opt_")
	temp_root = Path(temp_dir.name)
	candidates = [
		("/ebook", temp_root / "optimized_ebook.pdf"),
		("/screen", temp_root / "optimized_screen.pdf"),
	]

	best_path: Optional[Path] = None
	best_size = original_size

	for profile, out_path in candidates:
		if not _optimize_once(resolved_gs, source, out_path, profile):
			continue
		out_size = out_path.stat().st_size
		if out_size < best_size:
			best_size = out_size
			best_path = out_path
		if out_size <= target_bytes:
			best_path = out_path
			best_size = out_size
			break

	if best_path is None or best_size >= original_size:
		temp_dir.cleanup()
		return (
			pdf_path,
			None,
			(
				"PDF optimization ran but did not reduce size "
				f"(original {original_size} B)."
			),
		)

	status = (
		"PDF optimized before send: "
		f"{original_size} B -> {best_size} B using Ghostscript."
	)
	return str(best_path), temp_dir, status
