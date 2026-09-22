import os
import sys
from pathlib import Path

import cv2
import numpy as np


from webui.filters import clean_mathsolver_output

# === ПАТЕКИ: MathCalc во sys.path =====================================

# овој фајл е: .../MathCalc/django/web_pipeline.py
BASE_DIR = Path(__file__).resolve().parent      # .../MathCalc/django
PROJECT_ROOT = BASE_DIR.parent                  # .../MathCalc

# додај го MathCalc во PYTHONPATH ако не е додаден
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ======================================================================

from converters_to_str.picture_to_str import main as picture_to_str
from converters_to_str.pdf_to_str import pdf_to_str
from deepseek.mathsolver import solve_math_with_deepseek


PDF_ATTACH_DIR = PROJECT_ROOT / "pdf" / "attachedPDF"


def solve_from_text(text: str) -> str:
    text = text.strip()
    if not text:
        return "Празен текст."
    try:
        raw = solve_math_with_deepseek(text) #TREBA RESPONSE
        return clean_mathsolver_output(raw)
    except Exception as e:
        return f"Грешка при решавање на текст: {e}"


def solve_from_image_bytes(image_bytes: bytes, ocr_type: str = "1") -> str:
    """
    bytes -> OpenCV frame -> picture_to_str -> solve_math_with_deepseek
    """
    arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if frame is None:
        return "Не можам да ја декодирам сликата."

    try:
        text = picture_to_str(ocr_type, frame)
    except Exception as e:
        return f"Грешка при OCR од слика: {e}"

    if not text:
        return "OCR не извлече текст од сликата."

    try:
        raw = solve_math_with_deepseek(text)
        return clean_mathsolver_output(raw)
    except Exception as e:
        return f"Грешка при решавање на задачата од слика: {e}"


def solve_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    снима PDF во pdf/attachedPDF, па pdf_to_str(path) -> solve_math_with_deepseek
    """
    os.makedirs(PDF_ATTACH_DIR, exist_ok=True)

    pdf_path = PDF_ATTACH_DIR / "web_upload.pdf"
    try:
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
    except Exception as e:
        return f"Грешка при снимање PDF: {e}"

    try:
        text = pdf_to_str(str(PDF_ATTACH_DIR))
    except Exception as e:
        return f"Грешка при вадење текст од PDF: {e}"

    if not text:
        return "OCR не извлече текст од PDF."

    try:
        raw = solve_math_with_deepseek(text)
        return clean_mathsolver_output(raw)
    except Exception as e:
        return f"Грешка при решавање на задачата од PDF: {e}"
