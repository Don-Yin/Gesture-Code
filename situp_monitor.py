import cv2
from src.utils.device import device
from src.utils.gestures import Gestures
from src.monitor.monitor import PoseMonitor


class SitUpMonitor(PoseMonitor):
    def __init__(self):
        super().__init__()
        self.radius = 0.2
        self.circle_radius = int(self.current_resolution[1] * self.radius)
        self.situp = (
            Gestures(frame_shape=self.current_resolution)
            .point(["LEFT_KNEE", "RIGHT_KNEE"])
            .goes_near(["NOSE"], self.radius)
            .for_(0.1)
            .goes_away(["NOSE"], self.radius)
            .for_(0.1)
        )
        self.situp.counter = 0
        self.keypoints_diff_color = ["LEFT_KNEE", "RIGHT_KNEE", "NOSE"]
        self.keypoints_print_coords = []

    def case_specific_process(self, keypoints, frame):
        self.draw_keypoints(keypoints, frame)
        self.situp.update_frame(keypoints, frame, self.current_frame_rate)

        value = keypoints.get("NOSE", None)
        if value:
            cv2.circle(frame, value, self.circle_radius, (0, 255, 0), 2)

        cv2.putText(
            frame,
            f"Count: {self.situp.check()}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.font_size,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        # Print coordinates for points in keypoints_print_coords on the frame at the top right
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
        """
        Draw all the keypoints on the frame
        """
        for key, value in keypoints.items():
            if key in self.keypoints_diff_color:
                cv2.circle(frame, value, 5, (0, 0, 255), -1)


if __name__ == "__main__":
    squat_monitor = SitUpMonitor()
    squat_monitor.start_loop()
