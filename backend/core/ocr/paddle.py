import cv2
import numpy as np


def run_paddle(frame: np.ndarray) -> str:
    """Extract text using PaddleOCR."""
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        return ''

    # Ensure minimum resolution for OCR accuracy
    h, w = frame.shape[:2]
    if min(h, w) < 800:
        scale = 800 / min(h, w)
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    result = ocr.ocr(rgb, cls=True)

    lines = []
    if result:
        for block in result:
            if block:
                for line in block:
                    if line and len(line) >= 2:
                        text, confidence = line[1]
                        if confidence > 0.5:
                            lines.append(text)
    return '\n'.join(lines).strip()
