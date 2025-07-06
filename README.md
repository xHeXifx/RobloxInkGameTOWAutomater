Roblox Ink Game - Tug Of War automater

Okay so this doesnt actually work but its still pretty cool to watch on the CV2 screen.


Ink Game's TOW (Tug Of War) system works as so:
a blue arrow spins around a circle and the user has to click space whenever this arrow is pointing within the red section of the circle
(An exmaple of this can be found in sample.png)

This script was an attempt to automate this, it works by using CV2 to detect these factors and calculate when to press space. 

The processing behind this script can be seen when running "main.py", a series of circles and lines are drew on the cv2 window when opened.

Red Circle:
    This circle is the area where the red (shown in sample.png) can be. Each frame, the script checks if it can find red within this circle, if it can it draws lines from the center to where the red is found.