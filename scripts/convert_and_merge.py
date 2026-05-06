"""Convert rendered PDFs to JPG and merge per the YAML config.

CLI:
    uv run python scripts/convert_and_merge.py --config options.yml --project-root .
"""

import argparse
import sys
from pathlib import Path

from pdf2image import convert_from_path
from pypdf import PdfWriter

# Allow `python scripts/convert_and_merge.py` to work from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.load_yaml import load_options


def pdf_to_jpg(path_pdf: str, path_jpg: str) -> None:
    """Convert a PDF file to one or more JPEG images.

    Page 1 always writes to '{path_jpg}.jpg' so downstream consumers (gh-pages
    cover, CI artifact upload) can rely on a stable filename. Additional pages
    write to '{path_jpg}-page2.jpg', '{path_jpg}-page3.jpg', ...

    Args:
        path_pdf: Path to the source PDF.
        path_jpg: Base path (without extension) for the output JPEG(s).

    Raises:
        ValueError: If the input is not a .pdf file.
        FileNotFoundError: If the input file does not exist.
    """
    if not path_pdf.endswith(".pdf"):
        raise ValueError("The input file must be a PDF file.")
    if not Path(path_pdf).exists():
        raise FileNotFoundError(f"The PDF file {path_pdf} does not exist.")

    pages = convert_from_path(path_pdf)
    pages[0].save(f"{path_jpg}.jpg", "JPEG")
    for i, page in enumerate(pages[1:], start=2):
        page.save(f"{path_jpg}-page{i}.jpg", "JPEG")


def merge_pdfs(pdfs: list[str], new_path: str) -> None:
    """Merge a list of PDF files into a single output PDF."""
    writer = PdfWriter()
    for pdf in pdfs:
        writer.append(pdf)
    Path(new_path).parent.mkdir(parents=True, exist_ok=True)
    writer.write(new_path)
    writer.close()


def _resolve(project_root: Path, rel: str) -> Path:
    """Resolve a path from the YAML config relative to --project-root."""
    p = Path(rel)
    return p if p.is_absolute() else (project_root / p)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert + merge rendered resume PDFs.")
    parser.add_argument("--config", default="options.yml", help="Path to YAML config.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Root directory for resolving relative paths in the YAML.",
    )
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    cfg = load_options(args.config)

    languages = cfg["languages"]
    resumes = cfg["paths"]["resumes"]
    merged_pdf = _resolve(project_root, cfg["paths"]["merged_pdf"])

    # Compiled PDFs live next to the .tex source with .pdf extension.
    pdf_paths = []
    for lang in languages:
        tex = _resolve(project_root, resumes[lang])
        pdf = tex.with_suffix(".pdf")
        if not pdf.exists():
            raise FileNotFoundError(f"Expected compiled PDF not found: {pdf}")
        pdf_paths.append(str(pdf))
        # Convert the per-language PDF to JPG next to it.
        pdf_to_jpg(str(pdf), str(pdf.with_suffix("")))

    merge_pdfs(pdf_paths, str(merged_pdf))

    # Optional: copy merged PDF to site/docs location if configured.
    docs_pdf_rel = cfg["paths"].get("docs_pdf")
    if docs_pdf_rel:
        docs_pdf = _resolve(project_root, docs_pdf_rel)
        docs_pdf.parent.mkdir(parents=True, exist_ok=True)
        docs_pdf.write_bytes(merged_pdf.read_bytes())

    print(f"Merged PDF: {merged_pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
