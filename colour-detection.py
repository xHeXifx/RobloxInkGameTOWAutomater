import cv2
import numpy as np
import mss

def bgr_to_hsv(bgr):
    bgr_pixel = np.uint8([[bgr]])
    hsv_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)
    return hsv_pixel[0][0]


red_bgr  = [76, 81, 179]
blue_bgr = [169, 113, 68]

red_hsv  = bgr_to_hsv(red_bgr)
blue_hsv = bgr_to_hsv(blue_bgr)

print(f"Red HSV: {red_hsv}")
print(f"Blue HSV: {blue_hsv}")


hue_tol = 10
sat_tol = 50
val_tol = 50

lower_red  = np.array([max(0,   red_hsv[0] - hue_tol), max(0,   red_hsv[1] - sat_tol), max(0,   red_hsv[2] - val_tol)])
upper_red  = np.array([min(179, red_hsv[0] + hue_tol), min(255, red_hsv[1] + sat_tol), min(255, red_hsv[2] + val_tol)])

lower_blue = np.array([max(0,   blue_hsv[0] - hue_tol), max(0,   blue_hsv[1] - sat_tol), max(0,   blue_hsv[2] - val_tol)])
upper_blue = np.array([min(179, blue_hsv[0] + hue_tol), min(255, blue_hsv[1] + sat_tol), min(255, blue_hsv[2] + val_tol)])

print(f"Red HSV range: {lower_red} - {upper_red}")
print(f"Blue HSV range: {lower_blue} - {upper_blue}")

with mss.mss() as sct:
    monitor = sct.monitors[3]
    # 1 = Right Monitor
    # 2 = Left Mointor
    # 3 = Middle Monitor

    while True:
        sct_img = sct.grab(monitor)
        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask_red  = cv2.inRange(hsv, lower_red, upper_red)
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

        combined_mask = cv2.bitwise_or(mask_red, mask_blue)

        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 50:  # ignore noise
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Detected Colors", frame)
        cv2.imshow("Mask", combined_mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
