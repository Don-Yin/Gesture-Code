from typing import Any
import cv2
from ultralytics.engine.results import Keypoints
from src.utils.device import device
import numpy as np
from src.controls.keyboard import KeyPresser
from threading import Thread
from src.monitor.monitor import PoseMonitor
from queue import Queue


class BodyController(PoseMonitor):
    def __init__(self):
        super().__init__()
        self.nose_radius = 250
        self.nose_inner_radius = 60

        self.angle_queue = Queue()
        self.keypresser = KeyPresser(self.nose_inner_radius)
        self.keypresser_thread = Thread(target=self.keypresser.shift_keys, args=(self.angle_queue,))
        self.keypresser_thread.start()

    def case_specific_process(self, keypoints: Keypoints, frame: Any) -> None:
        # -------- draw nose --------
        nose_value = keypoints.get("NOSE", None)
        if nose_value:
            cv2.circle(frame, nose_value, self.nose_radius, (0, 255, 0), 2)
            cv2.circle(frame, nose_value, self.nose_inner_radius, (0, 0, 255), 2)

        # -------- draw two wraists --------
        left_wrist = keypoints.get("LEFT_WRIST", None)
        right_wrist = keypoints.get("RIGHT_WRIST", None)
        if left_wrist and right_wrist:
            cv2.circle(frame, left_wrist, 5, (0, 255, 0), -1)
            cv2.circle(frame, right_wrist, 5, (0, 255, 0), -1)

            middle_wrist_dot = ((left_wrist[0] + right_wrist[0]) // 2, (left_wrist[1] + right_wrist[1]) // 2)
            cv2.line(frame, left_wrist, right_wrist, (0, 255, 0), 2)
            cv2.circle(frame, middle_wrist_dot, 5, (0, 0, 255), -1)

        # -------- draw angle line --------
        if all([nose_value, left_wrist, right_wrist]):
            cv2.line(frame, nose_value, middle_wrist_dot, (255, 255, 0), 2)
            dx = middle_wrist_dot[0] - nose_value[0]
            dy = middle_wrist_dot[1] - nose_value[1]
            angle = np.arctan2(dy, dx) * (180 / np.pi)
            distance = np.sqrt(dx**2 + dy**2)
            while not self.angle_queue.empty():
                self.angle_queue.get_nowait()
            self.angle_queue.put((angle, distance))


if __name__ == "__main__":
    body_controller = BodyController()
    body_controller.start_loop()
