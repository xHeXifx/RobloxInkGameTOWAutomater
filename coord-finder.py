import cv2
import numpy as np
import mss

def grab_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[3]
        sct_img = sct.grab(monitor)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

drawing = False 
ix, iy = -1, -1
ex, ey = -1, -1

# Mouse callback function
def draw_circle(event, x, y, flags, param):
    global ix, iy, ex, ey, drawing, img_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        ex, ey = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            ex, ey = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        ex, ey = x, y
        center_x = int((ix + ex) / 2)
        center_y = int((iy + ey) / 2)
        radius = int(np.hypot(ex - ix, ey - iy) / 2)
        print(f"Center: ({center_x}, {center_y}), Radius: {radius}")

img = grab_screen()
img_copy = img.copy()

cv2.namedWindow("Draw Circle")
cv2.setMouseCallback("Draw Circle", draw_circle)

while True:
    display_img = img.copy()
    if drawing or (ix != -1 and iy != -1 and ex != -1 and ey != -1):
        center_x = int((ix + ex) / 2)
        center_y = int((iy + ey) / 2)
        radius = int(np.hypot(ex - ix, ey - iy) / 2)
        if radius > 0:
            cv2.circle(display_img, (center_x, center_y), radius, (0, 255, 0), 2)

    cv2.imshow("Draw Circle", display_img)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break

cv2.destroyAllWindows()
