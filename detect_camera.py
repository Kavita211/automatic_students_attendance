import cv2

def find_working_camera(max_devices=5):
    print("[INFO] Searching for a working camera...")
    for index in range(max_devices):
        print(f"[INFO] Trying /dev/video{index}...")
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None:
                print(f"[SUCCESS] Found working camera at index {index} (/dev/video{index})")
                return index
            else:
                print(f"[WARNING] /dev/video{index} opened but failed to capture frame.")
        else:
            print(f"[WARNING] /dev/video{index} could not be opened.")
    print("[ERROR] No working camera found.")
    return None

if __name__ == "__main__":
    find_working_camera()
