import cv2
from src.utils.device import device
from src.utils.gestures import Gestures
from src.monitor.monitor import PoseMonitor


class ClapMonitor(PoseMonitor):
    def __init__(self):
        super().__init__()
        self.radius = 0.3
        self.circle_radius = int(self.current_resolution[1] * self.radius)
        self.clap = (
            Gestures(frame_shape=self.current_resolution)
            .point(["LEFT_WRIST"])
            .goes_near(["RIGHT_WRIST"], self.radius)
            .for_(0.1)
            .goes_away(["RIGHT_WRIST"], self.radius)
            .for_(0.1)
        )
        self.clap.counter = 0
        self.keypoints_diff_color = ["RIGHT_WRIST", "LEFT_WRIST"]
        self.keypoints_print_coords = []

    def case_specific_process(self, keypoints, frame):
        self.draw_keypoints(keypoints, frame)
        self.clap.update_frame(keypoints, frame, self.current_frame_rate)

        cv2.putText(
            frame,
            f"Count: {self.clap.check()}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.font_size,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    def draw_keypoints(self, keypoints, frame):
        """
        Draw all the keypoints on the frame
        """
        for key, value in keypoints.items():
            if key in self.keypoints_diff_color:
                cv2.circle(frame, value, 5, (0, 0, 255), -1)


if __name__ == "__main__":
    clap_monitor = ClapMonitor()
    clap_monitor.start_loop()
