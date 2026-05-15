import io
import pdfplumber


def extract_pdf_text(pdf_source) -> str:
    """Extract all text from a PDF. Accepts a file path (str) or BytesIO."""
    text_parts = []
    try:
        src = io.BytesIO(pdf_source) if isinstance(pdf_source, bytes) else pdf_source
        with pdfplumber.open(src) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
    except Exception as e:
        return f'[PDF extraction error: {e}]'
    return '\n\n'.join(text_parts).strip()
