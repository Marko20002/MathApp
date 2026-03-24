from pathlib import Path

import cv2


def last_screenshot(dirpath: str) -> Path | None:
    folder = Path(dirpath)
    exts = {".png", ".jpg", ".jpeg"}

    candidates = [
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in exts
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)
