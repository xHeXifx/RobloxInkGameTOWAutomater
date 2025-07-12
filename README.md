# Roblox Ink Game - Tug Of War Automater

> Okay so this doesnt actually work but its still pretty cool to watch on the CV2 screen. 

> Going through the code and testing, uncommenting the keypresses on lines 232 and 233 typically get the closest to the red and being correct. I found best way to test is to open the youtube video present in the credits and run the script, the script presses space when it believes it should and pauses the video. This will show you how close it gets.

---

## How Ink Game's TOW (Tug Of War) System Works

A blue arrow spins around a circle and the user has to click space whenever this arrow is pointing within the red section of the circle  
(An example of this can be found in `sample.png`).

---

## About This Script

This script was an attempt to automate this. It works by using CV2 to detect these factors and calculate when to press space.

The processing behind this script can be seen when running `main.py`:  
A series of circles and lines are drawn on the cv2 window when opened.

---

## Visual Elements

- **Red Circle:**  
    This circle is the area where the red (shown in `sample.png`) can be. Each frame, the script checks if it can find red within this circle.

- **Red Lines:**  
    The red lines represent where red can be found within the red circle. If it can find red within this circle it draws lines from the center to where the red is found.

- **Green Circle:**  
    This circle is the area in which the arrow rotates around in game. The script uses this section to determine where the arrow is. It checks for any moving object moving within this green circle and places a yellow bounding box around it.

- **Yellow Box (The Bounding Box):**  
    This box represents the script's guess on the arrow's position. This is here just to visually show where the script believes the arrow is.

- **Orange Rectangle:**  
    This rectangle shows the Area Of Interest. This is where the script monitors behaviour; it won't check for anything outside of the rectangle. This is semi-redundant as the circles are used for AOIs.

---

## Errors Within `main.py`

> I'm unsure at this point to what is broken within the script but when implementing Pynput's key presses it chooses to press space whenever it feels like. Console logs whenever it believes the arrow is within the red which looks okay but it presses space at the wrong time.  
> It's difficult to see if the script is really detecting the arrow in red well as looking at 2 screens at once isn't possible (obviously) so I have to look back and forth to see if it detects it.

---

## Other Testing Files in Codebase

> **Note:** None of these files are imported or used in `main.py` however some of their logic is.

- **`colour-detection.py`:**  
    This script is used to detect for red and blue within the screen. It creates 2 windows, one for displaying the screen and drawing boxes around red and blue objects, and a mask window, to show again where these colours are present in a mask format.

- **`colour-picker.py`:**  
    This script was used for me to determine the real RGB values of the red outline and blue arrow.

- **`coord-finder`:**  
    This script was modified and used to draw squares however now it draws circles. It was used so I can draw a circle and get the radius and center point instead of manually typing screen coords to find the exact circle. This was used to get the coords for the red and green circle coords for tracking.

- **`keypress-test.py`:**  
    One of the final test scripts, very simple. Imports pynput and simulates a space keypress after waiting 5 seconds. This was a quick script to see how fast pynput sends keystrokes and if it could interact with the roblox window.

- **`live-monitor.py`:**  
    Simply used to take a screenshot of the frame on the screen when opening.

---

## How to Run Yourself

The script needs a few tweaks to get it running yourself.

1. Run  
   ```sh
   pip install opencv-python numpy pillow mss pynput
   ```  

2. Go into `main.py` and change the monitor variable on line 49:  
   ```python
   monitor = sct.monitors[1]
   ```
   `3` represents the monitor number, just go through numbers (1 upwards) until you find whichever is the monitor that roblox is on.

3. Run the script. If circles aren't inline with your game, change the following variables:
    - `CIRCLE_CENTER` + `CIRCLE_RADIUS` = coords for green circle (arrow rotation point)
    - `RED_CIRCLE_CENTER` + `RED_CIRCLE_RADIUS` = Red circle coords for red detection points.
    - You can use `coord-finder.py` to help get these values.

---

## Credits

- **Development:** [Me myself and I](https://hexif.vercel.app)
- **Youtube video used for testing:**  [https://www.youtube.com/watch?v=pidrci81uTU](https://www.youtube.com/watch?v=pidrci81uTU) (13 mins in)
