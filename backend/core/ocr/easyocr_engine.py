import cv2
import numpy as np

_reader = None  # cached so we only load the model once per server start


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        # english + macedonian (latin script) — downloads model on first run (~100MB)
        _reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    return _reader


def run_easyocr(frame: np.ndarray) -> str:
    """Extract text from an image using EasyOCR."""
    # Upscale small images for better accuracy
    h, w = frame.shape[:2]
    if min(h, w) < 800:
        scale = 800 / min(h, w)
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    reader = _get_reader()
    results = reader.readtext(frame, detail=0, paragraph=True)
    return '\n'.join(results).strip()
