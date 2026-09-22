import cv2

from camera import open_camera
from converters_to_str.picture_to_str import main as picture_to_str
from converters_to_str.pdf_to_str import pdf_to_str
from converters_to_str.screenshots_to_str import last_screenshot
from deepseek.mathsolver import solve_math_with_deepseek


def main(type_detail: str)->str:
    if type_detail == "1":
        print("Vnesi 1 za Tesarect 2 za Paddle")
        type = input().strip()
        return picture_to_str(type,open_camera())
    elif type_detail == "2":
        print("PDF PATH")
        path = r"C:\Users\marko\OneDrive\Desktop\MathCalc\pdf\attachedPDF"
        return pdf_to_str(path)
    elif type_detail == "3":
        print("Screemshot")
        path = r"C:\Users\marko\OneDrive\Desktop\MathCalc\screenshots"
        print("Vnesi 1 za Tesarect 2 za Paddle")
        type = input().strip()
        path_last_screenshot = last_screenshot(path)
        if path_last_screenshot is None:
            print("Neam")
            return ""
        frame = cv2.imread(str(path_last_screenshot))
        return picture_to_str(type,frame)
    else:
        print("Непозната опција, користи 1 или 2 ili 3.")
        return ""


if __name__ == "__main__":
    print("ako se slika 1 a za pdf 2,3 za schreenshot")
    type = input().strip()
    #print(main(type))
    resenie = solve_math_with_deepseek(main(type))
    print(resenie)
