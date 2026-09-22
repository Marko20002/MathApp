import pdfplumber
import argparse
from pathlib import Path

def get_last_pdf(dir_path: str) -> Path | None:
    folder = Path(dir_path)
    pdf_files = list(folder.glob("*.pdf"))

    if not pdf_files:
        return None

    # најнов по време на измени
    last_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
    return last_pdf

def pdf_to_str(pdf_path: str) -> str:
    pdf_path=get_last_pdf(pdf_path)
    all_pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            all_pages.append(text)
    return "\n\n".join(all_pages)


