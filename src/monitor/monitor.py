from src.utils.points import GetKeypoint
import cv2
from pathlib import Path
from ultralytics import YOLO
from ultralytics.engine.results import Keypoints
from src.utils.device import device
import time


class PoseMonitor:
    def __init__(self):
        self.get_keypoint = GetKeypoint()
        self.model = YOLO(Path("checkpoints", "yolov8n-pose.pt")).to(device)
        self.font_size = 1.0
        self.max_resolution = (1920 / 2, 1080 / 2)
        self.num_people = 1
        self.window_size = (int(1920 / 4), int(1080 / 4))
        self.current_frame_rate = 144  # default frame rate to start with
        self.frame_rate = 1 / 45  #  1 / 60

        self.cap = cv2.VideoCapture(0)
        current_resolution = (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if current_resolution[0] > self.max_resolution[0] and current_resolution[1] > self.max_resolution[1]:
            print(f"Amending resolution: {current_resolution} -> {self.max_resolution}")
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.max_resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.max_resolution[1])
        print(f"Current resolution: {current_resolution}")
        self.current_resolution = (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.prev_time = time.time()

        cv2.namedWindow("Pose Estimation", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.setWindowProperty("Pose Estimation", cv2.WND_PROP_TOPMOST, 1)  # keep it on top

    def start_loop(self):
        assert hasattr(self, "case_specific_process"), "Make sure to define case_specific_process in children"

        while True:
            if self.frame_rate:
                time.sleep(self.frame_rate)

            ret, frame = self.cap.read()
            frame = cv2.flip(frame, 1)

            if not ret:
                break

            # Perform pose estimation
            results = self.model(frame, verbose=False)
            result_keypoint = results[0].keypoints.xyn.cpu().numpy()

            # Fetch keypoints and draw them on the frame
            if result_keypoint.size > 0:
                result_keypoint = result_keypoint[: self.num_people]  # limit the number of people
                for person_keypoints in result_keypoint:
                    keypoints = {
                        name: (
                            int(person_keypoints[getattr(self.get_keypoint, name)][0] * frame.shape[1]),
                            int(person_keypoints[getattr(self.get_keypoint, name)][1] * frame.shape[0]),
                        )
                        for name in self.get_keypoint.model_dump().keys()
                    }

                    # -------- this is the bit that does all the heavy lifting --------
                    self.case_specific_process(keypoints, frame)

            current_time = time.time()
            self.current_frame_rate = 1 / ((current_time - self.prev_time) + 1e-6)
            self.current_frame_rate = min(self.current_frame_rate, 144)
            self.prev_time = current_time

            cv2.putText(
                frame, f"FPS: {self.current_frame_rate:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA
            )
            cv2.imshow("Pose Estimation", cv2.resize(frame, self.window_size))
            cv2.waitKey(1)

        # Release the capture and close the window
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    pose_monitor = PoseMonitor()
    pose_monitor.start_loop()
