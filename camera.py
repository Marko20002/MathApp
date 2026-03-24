import cv2

def open_camera(camera_index: int = 1):
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Не можам да се поврзам со камерата.")
        return None

    window_name = "DroidCam - Telefon kamera"
    print("Притисни 'c' во ПРОЗОРЕЦОТ за да снимиш кадар, 'q' или ESC за излез.")

    captured_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Проблем со читање од камерата.")
            break

        # покажи го live feed-от
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            captured_frame = frame.copy()
            break
        elif key == ord('q') or key == 27:   # 27 = ESC
            captured_frame = None
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured_frame
