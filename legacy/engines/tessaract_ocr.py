import cv2
import pytesseract
from camera import open_camera

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def tessaract_ocr(frame) -> str:

    if frame is None:
        print("Нема снимен кадар (стисна 'q' или има проблем со камерата).")
        return ""

    # 1) Grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2) Мал blur за да се намали шум
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # 3) Зумирај ја сликата (Tesseract сака поголеми букви)
    scale = 2.0
    gray = cv2.resize(
        gray, None,
        fx=scale, fy=scale,
        interpolation=cv2.INTER_CUBIC
    )

    # 4) Binarization (црно-бело) – adaptive threshold
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 15
    )

    # (опционално) прикажи што му праќаме на tesseract
    # cv2.imshow("OCR input", gray)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    text = pytesseract.image_to_string(
        gray,
        lang="eng",
        config="--oem 1 --psm 6"
    )

    return text
