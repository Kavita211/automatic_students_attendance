import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[ERROR] Cannot open webcam")
    exit()

cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)  # Adjust brightness
cap.set(cv2.CAP_PROP_CONTRAST, 0.5)    # Adjust contrast
cap.set(cv2.CAP_PROP_GAIN, 10)         # Adjust gain

ret, frame = cap.read()
if ret:
    cv2.imwrite("opencv_test.jpg", frame)
    print("[INFO] Image saved as opencv_test.jpg")
else:
    print("[ERROR] Failed to capture image")

cap.release()
