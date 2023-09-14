import cv2
from src.utils.device import device
from src.utils.gestures import Gestures
from src.monitor.monitor import PoseMonitor


class SquatMonitor(PoseMonitor):
    def __init__(self):
        super().__init__()
        # ----------------
        self.squat = (
            Gestures(frame_shape=self.current_resolution).point("NOSE").goes_above(0.5).for_(0.1).goes_below(0.5).for_(0.1)
        )
        self.squat.counter = 0
        self.keypoints_diff_color = ["NOSE"]
        self.keypoints_print_coords = ["NOSE"]

    def case_specific_process(self, keypoints, frame):
        self.draw_keypoints(keypoints, frame)
        self.squat.update_frame(keypoints, frame, self.current_frame_rate)
        cv2.line(frame, (0, int(frame.shape[0] / 2)), (frame.shape[1], int(frame.shape[0] / 2)), (0, 0, 255), 2)

        cv2.putText(
            frame,
            f"Count: {self.squat.check()}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.font_size,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        y_offset = 30
        for coord_name in self.keypoints_print_coords:
            if coord_name in keypoints:
                cv2.putText(
                    frame,
                    f"{coord_name}: {keypoints[coord_name]}",
                    (int(self.current_resolution[0] - 400), y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )
                y_offset += 20

    def draw_keypoints(self, keypoints, frame):
        """Draw all the keypoints on the frame"""
        for key, value in keypoints.items():
            if key in self.keypoints_diff_color:
                cv2.circle(frame, value, 5, (0, 0, 255), -1)


if __name__ == "__main__":
    squat_monitor = SquatMonitor()
    squat_monitor.start_loop()
