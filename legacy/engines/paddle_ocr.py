import cv2
from paddleocr import PaddleOCR

from camera import open_camera

ocr = PaddleOCR(
    lang="en",
    use_angle_cls=True
)

def paddle_ocr(frame) -> str:

    if frame is None:
        print("Нема снимен кадар (стисна 'q' или има проблем со камерата).")
        return ""

    img = frame.copy()
    h, w = img.shape[:2]

    # ако најдолгата страна е помала од 800 пиксели, зголеми до 800
    max_side = max(h, w)
    if max_side < 800:
        scale = 800 / max_side
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)

    # 2) BGR -> RGB (PaddleOCR очекува RGB)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 3) OCR со Paddle (cls=True за да си ја сврти ако е накривена)
    result = ocr.ocr(img_rgb)

    lines = []
    for line in result[0]:
        data = line[1]

        # случај: [box, (text, score)]
        if isinstance(data, (list, tuple)):
            if not data:
                continue
            text = str(data[0])

        # случај: [box, text] или нешто слично
        else:
            text = str(data)

        text_line = text.replace("\n", " ").strip()
        if text_line:
            lines.append(text_line)

    return " ".join(lines)


