import cv2
import numpy as np
import mss
import time

# Which screen to capture
MONITOR_INDEX = 3
SAVE_FILENAME = "screenshot.png"

def main():
    with mss.mss() as sct:
        monitor = sct.monitors[MONITOR_INDEX]

        print("Press 's' in the window to save a frame.")
        print("Press 'q' to quit.")

        while True:
            start_time = time.time()

            # Grab frame
            sct_img = sct.grab(monitor)
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            cv2.imshow("Live Screen", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                cv2.imwrite(SAVE_FILENAME, frame)
                print(f"Saved frame to {SAVE_FILENAME}")

            elapsed = time.time() - start_time
            fps = 1 / elapsed
            cv2.setWindowTitle("Live Screen", f"Live Screen - FPS: {fps:.1f}")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
