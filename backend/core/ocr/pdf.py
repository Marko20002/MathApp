import io
import pdfplumber
from core.errors import PipelineError


def extract_pdf_text(pdf_source) -> str:
    """Extract all text from a PDF. Accepts a file path (str) or BytesIO."""
    text_parts = []
    try:
        src = io.BytesIO(pdf_source) if isinstance(pdf_source, bytes) else pdf_source
        with pdfplumber.open(src) as pdf:
            if len(pdf.pages) > 20:
                raise PipelineError('pdf_too_long', 'Select at most 20 PDF pages.', 400)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
    except PipelineError:
        raise
    except Exception as e:
        raise PipelineError('invalid_pdf', 'Could not read this PDF.', 400) from e
    return '\n\n'.join(text_parts).strip()
