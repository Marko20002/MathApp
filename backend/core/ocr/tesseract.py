"""
Tesseract OCR — kept for reference but no longer used.
Images are now handled directly by GPT-4o Vision in core/pipeline.py,
which reads AND solves math from images in one step without needing
a local OCR binary installation.
"""

# import os
# import cv2
# import numpy as np
# import pytesseract
# from django.conf import settings
#
#
# def run_tesseract(frame: np.ndarray) -> str:
#     tesseract_path = getattr(settings, 'TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
#     if os.path.exists(tesseract_path):
#         pytesseract.pytesseract.tesseract_cmd = tesseract_path
#
#     gray      = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     blurred   = cv2.GaussianBlur(gray, (3, 3), 0)
#     upscaled  = cv2.resize(blurred, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
#     _, binary = cv2.threshold(upscaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#
#     config = '--oem 1 --psm 6'
#     try:
#         return pytesseract.image_to_string(binary, config=config).strip()
#     except pytesseract.TesseractNotFoundError:
#         raise RuntimeError('Tesseract is not installed.')
