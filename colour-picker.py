import cv2
import numpy as np
import sys

# --- Configuration ---
IMAGE_PATH = 'Sample.png' 

# --- Global variables ---
img = None
window_name = "Image Pixel Sampler (Click to get BGR)"

# --- Mouse callback function ---
def mouse_callback(event, x, y, flags, param):
    global img

    if event == cv2.EVENT_LBUTTONDOWN:
        if img is not None:
            bgr_values = img[y, x]
            blue = bgr_values[0]
            green = bgr_values[1]
            red = bgr_values[2]

            print(f"Clicked at (x={x}, y={y})")
            print(f"BGR: ({blue}, {green}, {red})")
            print(f"RGB: ({red}, {green}, {blue})\n")

            color_sample = np.zeros((100, 100, 3), np.uint8)
            color_sample[:] = bgr_values
            cv2.imshow("Sampled Color", color_sample)
        else:
            print("Error: No image loaded.")

# --- Main script execution ---
if __name__ == "__main__":

    if len(sys.argv) > 1:
        IMAGE_PATH = sys.argv[1]

    # Load image
    img = cv2.imread(IMAGE_PATH)

    # Check if image was loaded
    if img is None:
        print(f"Error: Could not load image from '{IMAGE_PATH}'.")
        print("Please ensure the image path is correct and the file exists.")
        print("Usage: python your_script_name.py [path_to_image.png]")
        sys.exit(1) # Exit if image load fails

    cv2.namedWindow(window_name)

    cv2.setMouseCallback(window_name, mouse_callback)

    print(f"Image '{IMAGE_PATH}' loaded successfully.")
    print("Click on any pixel in the image window to get its BGR/RGB values.")
    print("Press 'q' or 'ESC' to quit the application.")

    cv2.imshow(window_name, img)

    while True:
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break

    # Destroy all OpenCV windows
    cv2.destroyAllWindows()
    print("Application closed.")