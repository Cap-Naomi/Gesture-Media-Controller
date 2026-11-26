import cv2
import mediapipe as mp
import time
from pathlib import Path


class HandTracker:

    def __init__(self):

        # Locate the pretrained model
        model_path = (
            Path(__file__).resolve().parent
            / "models"
            / "gesture_recognizer.task"
        )

        # Configure the recognizer
        options = mp.tasks.vision.GestureRecognizerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(model_path)
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Initialize the pretrained model
        self.recognizer = (
            mp.tasks.vision.GestureRecognizer
            .create_from_options(options)
        )

        self.last_timestamp = -1

    def process_frame(self, frame):

        # Convert OpenCV BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert NumPy array into MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Generate an increasing timestamp in milliseconds
        timestamp = time.monotonic_ns() // 1_000_000
        timestamp = max(timestamp, self.last_timestamp + 1)
        self.last_timestamp = timestamp

        # Perform model inference
        result = self.recognizer.recognize_for_video(
            mp_image,
            timestamp
        )

        return result

    def close(self):
        self.recognizer.close()

    def draw_landmarks(self, frame, result):

        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]

        height, width = frame.shape[:2]

        for landmarks in result.hand_landmarks:

            points = []

            # Convert normalized coordinates to pixels
            for landmark in landmarks:

                x = int(landmark.x * width)
                y = int(landmark.y * height)

                points.append((x, y))

            # Draw connections between landmarks
            for start, end in connections:

                cv2.line(
                    frame,
                    points[start],
                    points[end],
                    (0, 255, 0),
                    2
                )

            # Draw individual landmarks
            for point in points:

                cv2.circle(
                    frame,
                    point,
                    4,
                    (0, 0, 255),
                    -1
                )

        return frame