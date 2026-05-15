"""
pipeline.py — orchestrates input → OCR (if needed) → DeepSeek solve

Three public functions used by solver/views.py:
  solve_text(text)               → dict
  solve_image_bytes(bytes)       → dict   (EasyOCR → DeepSeek)
  solve_pdf_bytes(bytes)         → dict   (pdfplumber → DeepSeek)

Each returns: { solution, domain, problem_text }
"""
import cv2
import numpy as np

from core.mathsolver import solve_math
from core.ocr.easyocr_engine import run_easyocr
from core.ocr.pdf import extract_pdf_text


def _detect_domain(text: str) -> str:
    t = text.lower()
    scores = {
        'calculus':    sum(w in t for w in ['integral', 'derivative', 'limit', 'lim', 'dx', '∫', 'd/dx', 'differentiat']),
        'probability': sum(w in t for w in ['probability', 'distribution', 'expected', 'variance', 'random', 'p(']),
        'discrete':    sum(w in t for w in ['graph', 'permutation', 'combination', 'set', 'logic', 'modulo', 'induction']),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'unknown'


def _build_result(problem_text: str, solution: str) -> dict:
    return {
        'problem_text': problem_text,
        'solution':     solution,
        'domain':       _detect_domain(problem_text + ' ' + solution),
    }


def solve_text(text: str) -> dict:
    text = text.strip()
    if not text:
        return _build_result('', '[No text provided.]')
    return _build_result(text, solve_math(text))


def solve_image_bytes(image_bytes: bytes, ocr_engine: str = '1') -> dict:
    arr   = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if frame is None:
        return _build_result('', '[Could not decode image.]')

    text = run_easyocr(frame)
    if not text:
        return _build_result('', '[Could not extract text from image. Try a clearer photo.]')

    return _build_result(text, solve_math(text))


def solve_pdf_bytes(pdf_bytes: bytes) -> dict:
    # pdfplumber accepts BytesIO directly — no temp file needed
    text = extract_pdf_text(pdf_bytes)

    if not text:
        return _build_result('', '[No text found in PDF.]')

    return _build_result(text, solve_math(text))
