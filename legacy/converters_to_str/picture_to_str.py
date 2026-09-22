from engines.paddle_ocr import paddle_ocr
from engines.tessaract_ocr import tessaract_ocr





def main(engine_choice: str,frame)->str:
    text=""
    if engine_choice == "1":
        text = tessaract_ocr(frame)
    elif engine_choice == "2":
        text = paddle_ocr(frame)
    else:
        print("Neam takov engine")
    return text

