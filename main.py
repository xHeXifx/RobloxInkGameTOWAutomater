import cv2
import numpy as np
import mss
import time
import os
from pynput.keyboard import Key, Controller

CIRCLE_CENTER = (1060, 633)
CIRCLE_RADIUS = 83

TOP_LEFT = (CIRCLE_CENTER[0] - CIRCLE_RADIUS - 10, CIRCLE_CENTER[1] - CIRCLE_RADIUS - 10)
BOTTOM_RIGHT = (CIRCLE_CENTER[0] + CIRCLE_RADIUS + 10, CIRCLE_CENTER[1] + CIRCLE_RADIUS + 10)

# Red detection circle
RED_CIRCLE_CENTER = (1062, 634)
RED_CIRCLE_RADIUS = 97

# Pynput keyboard define
keyboard = Controller()

# HSV range for red
RED_LOWER1 = np.array([0, 100, 80])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([160, 100, 80])
RED_UPPER2 = np.array([180, 255, 255])

def red_mask_hsv(roi, circle_mask=None):
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)
    mask2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
    mask = cv2.bitwise_or(mask1, mask2)
    if circle_mask is not None:
        mask = cv2.bitwise_and(mask, mask, mask=circle_mask)
    return mask

def main():
    print(f"Monitoring circle: Center {CIRCLE_CENTER}, Radius {CIRCLE_RADIUS}")
    print("Press 'q' to quit, 's' to toggle scanning, 'k' to toggle key presses")
    prev_blur = None
    last_time = time.time()
    frame_count = 0
    fps = 0
    last_red_check_time = 0

    scanning_enabled = True
    keypress_enabled = True

    with mss.mss() as sct:
        monitor = sct.monitors[3]
        win_title = "Screen Monitor"
        cv2.namedWindow(win_title)
        red_line_points = []
        arrow_red_timeout = 0
        while True:
            start_time = time.time()
            sct_img = sct.grab(monitor)
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            roi = frame[TOP_LEFT[1]:BOTTOM_RIGHT[1], TOP_LEFT[0]:BOTTOM_RIGHT[0]]

            mask = np.zeros(roi.shape[:2], dtype=np.uint8)
            cv2.circle(mask, (CIRCLE_RADIUS + 10, CIRCLE_RADIUS + 10), CIRCLE_RADIUS, 255, -1)

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            blur = cv2.bitwise_and(blur, blur, mask=mask)

            moving_bbox = None
            MIN_W, MIN_H = 25, 35
            if prev_blur is not None:
                diff = cv2.absdiff(blur, prev_blur)
                _, thresh_motion = cv2.threshold(diff, 12, 255, cv2.THRESH_BINARY)
                kernel = np.ones((5, 5), np.uint8)
                thresh_motion = cv2.morphologyEx(thresh_motion, cv2.MORPH_OPEN, kernel, iterations=2)
                contours, _ = cv2.findContours(thresh_motion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # Find largest moving object inside the circle
                max_area = 0
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area < 20 or area > 3000:
                        continue
                    x, y, w, h = cv2.boundingRect(cnt)
                    # Minimum size
                    if w < MIN_W:
                        x = max(0, x - (MIN_W - w) // 2)
                        w = MIN_W
                    if h < MIN_H:
                        y = max(0, y - (MIN_H - h) // 2)
                        h = MIN_H
                    cx = x + w // 2
                    cy = y + h // 2
                    dist = np.hypot(cx - (CIRCLE_RADIUS + 10), cy - (CIRCLE_RADIUS + 10))
                    if dist <= CIRCLE_RADIUS:
                        if area > max_area:
                            max_area = area
                            moving_bbox = (x, y, w, h)
                # Draw bounding box around moving object
                if moving_bbox:
                    abs_x = TOP_LEFT[0] + moving_bbox[0]
                    abs_y = TOP_LEFT[1] + moving_bbox[1]
                    cv2.rectangle(frame, (abs_x, abs_y), (abs_x + moving_bbox[2], abs_y + moving_bbox[3]), (0, 255, 255), 2)

            cv2.circle(frame, CIRCLE_CENTER, CIRCLE_RADIUS, (0, 255, 0), 2)
            cv2.rectangle(frame, TOP_LEFT, BOTTOM_RIGHT, (0, 128, 255), 1)

            # --- Red detection circle logic ---
            # Draw red lines after tracking logic to avoid interference with motion detection
            red_top_left = (RED_CIRCLE_CENTER[0] - RED_CIRCLE_RADIUS, RED_CIRCLE_CENTER[1] - RED_CIRCLE_RADIUS)
            red_bottom_right = (RED_CIRCLE_CENTER[0] + RED_CIRCLE_RADIUS, RED_CIRCLE_CENTER[1] + RED_CIRCLE_RADIUS)
            red_roi = frame[red_top_left[1]:red_bottom_right[1], red_top_left[0]:red_bottom_right[0]]

            red_mask = np.zeros(red_roi.shape[:2], dtype=np.uint8)
            cv2.circle(red_mask, (RED_CIRCLE_RADIUS, RED_CIRCLE_RADIUS), RED_CIRCLE_RADIUS, 255, -1)

            mask_red = red_mask_hsv(red_roi, red_mask)
            red_points = cv2.findNonZero(mask_red)
            red_line_points = []
            red_coverage = 0.0
            if red_points is not None:
                red_coverage = len(red_points) / (np.pi * RED_CIRCLE_RADIUS * RED_CIRCLE_RADIUS)
                center = np.array([RED_CIRCLE_RADIUS, RED_CIRCLE_RADIUS])
                vectors = red_points[:,0] - center
                angles = np.arctan2(vectors[:,1], vectors[:,0])
                sorted_idx = np.argsort(angles)
                sorted_points = red_points[sorted_idx][:,0]
                if len(sorted_points) > 10:
                    trimmed_points = sorted_points[5:-5]
                else:
                    trimmed_points = sorted_points
                for pt in trimmed_points[::max(1, len(trimmed_points)//100)]:
                    x, y = pt
                    abs_x = red_top_left[0] + x
                    abs_y = red_top_left[1] + y
                    red_line_points.append((abs_x, abs_y))

            cv2.circle(frame, RED_CIRCLE_CENTER, RED_CIRCLE_RADIUS, (0, 0, 255), 2)

            cv2.putText(
                frame,
                f"Red lines: {len(red_line_points)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )
            cv2.putText(
                frame,
                f"Red coverage: {red_coverage:.2%}",
                (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )

            # --- Check if arrow bbox is inside any red line, with cooldown or pause if everything is red ---
            check_red = scanning_enabled
            now = time.time()
            if red_coverage > 0.10:
                check_red = False
                if now - last_red_check_time > 1.0:
                    print("Red coverage very high, pausing scanning for 1 second.")
                    last_red_check_time = now
            elif len(red_line_points) > 100:
                if now - last_red_check_time < 1.0 and red_coverage <= 0.10:
                    check_red = scanning_enabled
                elif red_coverage <= 0.10:
                    last_red_check_time = now

            if arrow_red_timeout > now:
                check_red = False

            if moving_bbox and red_line_points and check_red:
                abs_x = TOP_LEFT[0] + moving_bbox[0]
                abs_y = TOP_LEFT[1] + moving_bbox[1]
                w, h = moving_bbox[2], moving_bbox[3]
                bbox_rect = (abs_x, abs_y, abs_x + w, abs_y + h)
                arrows_infront = []
                collision_found = False
                bbox_pts = np.array([
                    [bbox_rect[0], bbox_rect[1]],
                    [bbox_rect[2], bbox_rect[1]],
                    [bbox_rect[2], bbox_rect[3]],
                    [bbox_rect[0], bbox_rect[3]]
                ], dtype=np.float32).reshape((-1, 1, 2))
                for rx, ry in red_line_points:
                    inside = cv2.pointPolygonTest(bbox_pts, (float(rx), float(ry)), False)
                    if inside >= 0:
                        if not collision_found:
                            print(f"Arrow bbox {bbox_rect} is colliding with red line at ({rx}, {ry})")
                            if keypress_enabled:
                                # keyboard.press(Key.space)
                                # keyboard.release(Key.space)
                                # Removed key pressing cause script dont work
                                print()
                            collision_found = True
                        bbox_center = (abs_x + w // 2, abs_y + h // 2)
                        direction = np.array([bbox_center[0] - RED_CIRCLE_CENTER[0], bbox_center[1] - RED_CIRCLE_CENTER[1]])
                        direction_norm = np.linalg.norm(direction)
                        if direction_norm > 0:
                            direction_unit = direction / direction_norm
                            for tx, ty in red_line_points:
                                vec = np.array([tx - RED_CIRCLE_CENTER[0], ty - RED_CIRCLE_CENTER[1]])
                                proj = np.dot(vec, direction_unit)
                                if proj > direction_norm:
                                    arrows_infront.append((tx, ty))
                        print(f"Arrows in front of red line.")
                        if keypress_enabled:
                            # keyboard.press(Key.space)
                            # keyboard.release(Key.space)
                            # Removed key pressing cause script dont work
                            print()
                        arrow_red_timeout = now + 1.0 
                        break
                else:
                    bbox_center = (abs_x + w // 2, abs_y + h // 2)
                    direction = np.array([bbox_center[0] - RED_CIRCLE_CENTER[0], bbox_center[1] - RED_CIRCLE_CENTER[1]])
                    direction_norm = np.linalg.norm(direction)
                    if direction_norm > 0:
                        direction_unit = direction / direction_norm
                        for tx, ty in red_line_points:
                            vec = np.array([tx - RED_CIRCLE_CENTER[0], ty - RED_CIRCLE_CENTER[1]])
                            proj = np.dot(vec, direction_unit)
                            if proj > direction_norm:
                                arrows_infront.append((tx, ty))
                        if arrows_infront:
                            print(f"Arrows in front of red line.")
                            if keypress_enabled:
                                # keyboard.press(Key.space)
                                # keyboard.release(Key.space)
                                # Removed key pressing cause script dont work
                                print()                                
                            arrow_red_timeout = now + 1.0

            # Draw red lines after all tracking and logic
            for abs_x, abs_y in red_line_points:
                cv2.line(frame, RED_CIRCLE_CENTER, (abs_x, abs_y), (0, 0, 255), 1)

            frame_count += 1
            if time.time() - last_time >= 1.0:
                fps = frame_count / (time.time() - last_time)
                last_time = time.time()
                frame_count = 0

            title_with_fps = f"{win_title} - FPS: {fps:.1f}"
            cv2.setWindowTitle(win_title, title_with_fps)
            cv2.imshow(win_title, frame)

            prev_blur = blur.copy()

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('c'):
                os.system("cls")
            if key == ord('s'):
                scanning_enabled = not scanning_enabled
                print(f"Scanning {'enabled' if scanning_enabled else 'disabled'}")
            if key == ord('k'):
                keypress_enabled = not keypress_enabled
                print(f"Key presses {'enabled' if keypress_enabled else 'disabled'}")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()