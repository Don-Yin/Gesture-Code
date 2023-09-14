"""

"""

import pyautogui
import time
import math
from threading import Thread


class KeyPresser:
    def __init__(self, inner_circle_radius):
        self.inner_circle_radius = inner_circle_radius
        self.angle = 0
        self.distance = 0
        self.active_keys = self.get_active_keys(self.angle)
        self.ratio = self.calculate_ratio(self.angle)
        self.running = True
        self.all_keys = ["w", "a", "s", "d"]

    def get_active_keys(self, angle):
        if angle is None:  # A check to prevent a None value from causing issues
            return "w", "d"  # Default case

        if -180 <= angle < -90:
            return "w", "a"  # Up-Right
        elif -90 <= angle < 0:
            return "w", "d"  # Up-Left
        elif 0 <= angle < 90:
            return "s", "d"  # Down-Left
        elif 90 <= angle < 180:
            return "s", "a"  # Down-Right
        else:
            return "w", "d"  # Catch-all case, might not be necessary given the above ranges

    def calculate_ratio(self, angle):
        angle %= 90
        angle_rad = math.radians(angle)
        ratio = math.cos(angle_rad)
        return ratio, 1 - ratio

    def update_angle(self, angle, distance):
        self.angle = angle
        self.distance = distance
        self.active_keys = self.get_active_keys(angle)
        self.release_inactive_keys()
        self.ratio = self.calculate_ratio(angle)
        self.running = distance > self.inner_circle_radius

    def release_inactive_keys(self):
        for key in self.all_keys:
            if key not in self.active_keys:
                pyautogui.keyUp(key)

    def pause_key_presses(self):
        self.running = False

    def resume_key_presses(self):
        self.running = True

    def shift_keys(self, angle_queue):
        while True:
            angle, distance = angle_queue.get()
            self.update_angle(angle, distance)

            if self.running:
                # Press and hold the first key
                pyautogui.keyDown(self.active_keys[0])
                time.sleep(0.005 + 0.02 * self.ratio[0])
                pyautogui.keyUp(self.active_keys[0])

                # Press and hold the second key
                pyautogui.keyDown(self.active_keys[1])
                time.sleep(0.005 + 0.02 * self.ratio[1])
                pyautogui.keyUp(self.active_keys[1])
            else:
                # Release both keys when not running
                [pyautogui.keyUp(key) for key in self.all_keys]
                time.sleep(0.1)  # Sleep for a short duration when paused


if __name__ == "__main__":

    def update_angle_in_loop(key_presser):
        angle = 0
        while True:
            key_presser.update_angle(angle)
            time.sleep(0.01)
            angle = (angle + 1) % 360

    # Usage:
    key_presser = KeyPresser()
    angle_update_thread = Thread(target=update_angle_in_loop, args=(key_presser,))
    angle_update_thread.start()
