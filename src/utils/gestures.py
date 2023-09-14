import platform
import numpy as np

try:
    import winsound
except:
    import simpleaudio as sa


class Gestures:
    def __init__(self, frame_shape):
        self.counter = 0
        self.points_of_interest = []
        self.conditions = []
        self.current_condition_index = 0
        self.timestamp = 0
        self.frame_shape = frame_shape

        # -------- pregenerate some audio signal --------
        self.audio_signal = self.generate_audio_signal()
        self.system = platform.system()

    def generate_audio_signal(self):
        frequency = 440  # Frequency of the sound in Hz
        duration = 0.1  # Duration of the sound in seconds
        sample_rate = 44100  # Sample rate in Hz
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        x = np.sin(2 * np.pi * frequency * t)
        return (x * 32767).astype(np.int16)

    def play_sound(self):
        if self.system == "Windows":
            winsound.MessageBeep()

        else:
            sample_rate = 44100  # Sample rate in Hz
            play_obj = sa.play_buffer(self.audio_signal, 1, 2, sample_rate)
            play_obj.wait_done()

    def update_frame(self, keypoints, frame, frame_rate):
        self.keypoints = keypoints
        self.frame = frame
        self.frame_rate = frame_rate
        self.timestamp += 1 / frame_rate

        # Process the conditions
        if self.current_condition_index < len(self.conditions):
            condition = self.conditions[self.current_condition_index]
            if condition.check(self.keypoints, self.timestamp):
                self.current_condition_index += 1
                if self.current_condition_index == len(self.conditions):
                    self.counter += 1
                    self.play_sound()
                    self.reset_conditions()

    def reset_conditions(self):
        """for when the condition is met and we need to reset the conditions for accumulating"""
        self.current_condition_index = 0
        for condition in self.conditions:
            condition.start_timestamp = None

    # ----------------- points -----------------
    def point(self, point):
        if isinstance(point, str):
            self.points_of_interest.append(point)
        if isinstance(point, list):
            self.points_of_interest.extend(point)
        return self

    # ----------------- conditions -----------------
    def goes_below(self, threshold_percentage):
        threshold = self.frame_shape[1] * threshold_percentage
        self.conditions.append(GoesBelowCondition(self.points_of_interest, threshold))
        return self

    def goes_above(self, threshold_percentage):
        threshold = self.frame_shape[1] * threshold_percentage
        self.conditions.append(GoesAboveCondition(self.points_of_interest, threshold))
        return self

    def goes_near(self, points, distance_percentage):
        """
        points can be either coordinates or strings
        the distance percentage is a percentage of the frame width
        """
        distance_threshold = self.frame_shape[1] * distance_percentage
        if isinstance(points, str):
            points = [points]
        self.conditions.append(GoesNearCondition(self.points_of_interest, points, distance_threshold))
        return self

    def goes_away(self, points, distance_percentage):
        """As above"""
        distance_threshold = self.frame_shape[1] * distance_percentage
        if isinstance(points, str):
            points = [points]
        self.conditions.append(GoesAwayCondition(self.points_of_interest, points, distance_threshold))
        return self

    # ----------------- duration -----------------
    def for_(self, seconds):
        self.conditions[-1].duration = seconds
        return self

    # ----------------- check -----------------
    def check(self):
        return self.counter


class Condition:
    def __init__(self, points, threshold):
        self.points = points
        self.threshold = threshold
        self.duration = 0
        self.start_timestamp = None

    def check(self, keypoints, timestamp):
        raise NotImplementedError


class GoesBelowCondition(Condition):
    def check(self, keypoints, timestamp):
        if all(keypoints[point][1] < self.threshold for point in self.points):
            if self.start_timestamp is None:
                self.start_timestamp = timestamp
            elif timestamp - self.start_timestamp >= self.duration:
                return True
        else:
            self.start_timestamp = None
        return False


class GoesAboveCondition(Condition):
    def check(self, keypoints, timestamp):
        if all(keypoints[point][1] > self.threshold for point in self.points):
            if self.start_timestamp is None:
                self.start_timestamp = timestamp
            elif timestamp - self.start_timestamp >= self.duration:
                return True
        else:
            self.start_timestamp = None
        return False


class GoesNearCondition(Condition):
    def __init__(self, points, target_points, distance_threshold):
        super().__init__(points, distance_threshold)
        self.target_points = target_points

    def check(self, keypoints, timestamp):
        for target_point in self.target_points:
            if any(
                np.linalg.norm(np.array(keypoints[point]) - np.array(keypoints[target_point])) < self.threshold
                for point in self.points
            ):
                if self.start_timestamp is None:
                    self.start_timestamp = timestamp
                elif timestamp - self.start_timestamp >= self.duration:
                    return True
            else:
                self.start_timestamp = None
        return False


class GoesAwayCondition(Condition):
    def __init__(self, points, target_points, distance_threshold):
        super().__init__(points, distance_threshold)
        self.target_points = target_points

    def check(self, keypoints, timestamp):
        for target_point in self.target_points:
            if any(
                np.linalg.norm(np.array(keypoints[point]) - np.array(keypoints[target_point])) > self.threshold
                for point in self.points
            ):
                if self.start_timestamp is None:
                    self.start_timestamp = timestamp
                elif timestamp - self.start_timestamp >= self.duration:
                    return True
            else:
                self.start_timestamp = None
        return False


"""
desired syntax:
squat = Gesture().point(["LEFT_HIP", "RIGHT_HIP"]).goes_below(300).for_(2).goes_above(300).for_(2)
# it has to maintain the order of the conditions being met
- first goes below 300 for 2 seconds
- then goes above 300 for 2 seconds

squat.update_frame(keypoints, frame)



"""
