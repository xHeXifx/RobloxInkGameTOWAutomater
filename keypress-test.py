from pynput.keyboard import Key, Controller
import time

keyboard = Controller()

time.sleep(5)

keyboard.press(Key.space)
keyboard.release(Key.space)