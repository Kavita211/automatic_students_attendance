import cv2

image_path = "images/trupti.png"
image = cv2.imread(image_path)

if image is None:
    print("[ERROR] Image not found or can't be opened!")
else:
    output_path = "output_image.jpg"
    cv2.imwrite(output_path, image)
    print(f"[INFO] Image saved as {output_path}. Transfer it to view on your PC.")

