import time
from collections import deque


class SwipeDetector:

    def __init__(self):

        # Swipe detection settings
        self.confidence_threshold = 0.5
        self.time_window = 0.7
        self.min_displacement = 0.15
        self.max_vertical_displacement = 0.20
        self.min_velocity = 0.25

        # Validation settings
        self.cooldown = 1.0
        self.release_duration = 0.25

        # Store historical hand positions
        self.position_history = deque()

        # Swipe state
        self.last_swipe_time = float("-inf")
        self.swipe_latched = False
        self.release_start_time = None

    def detect(self, landmarks, gesture_name, confidence):

        now = time.monotonic()

        # Confirm that an open palm is detected
        valid_palm = (
            landmarks is not None
            and gesture_name == "Open_Palm"
            and confidence >= self.confidence_threshold
        )

        # Handle invalid gestures or hand release
        if not valid_palm:

            # Clear history if hand tracking is lost
            if landmarks is None:
                self.position_history.clear()

            # Start release timer
            if self.release_start_time is None:
                self.release_start_time = now

            # Confirm release after a sustained interruption
            if now - self.release_start_time >= self.release_duration:

                self.position_history.clear()
                self.swipe_latched = False

            return None

        # Open palm is detected again
        self.release_start_time = None

        # Require gesture release after a successful swipe
        if self.swipe_latched:
            return None

        # Prevent swipes from executing too frequently
        if now - self.last_swipe_time < self.cooldown:
            return None

        # Track landmark 9 (base of the middle finger)
        palm = landmarks[9]

        x = palm.x
        y = palm.y

        # Store current position and timestamp
        self.position_history.append((x, y, now))

        # Remove positions outside the time window
        while (
            self.position_history
            and now - self.position_history[0][2]
            > self.time_window
        ):
            self.position_history.popleft()

        # Require at least three position samples
        if len(self.position_history) < 3:
            return None

        # Retrieve the oldest recorded position
        start_x, start_y, start_time = self.position_history[0]

        # Calculate displacement and movement duration
        dx = x - start_x
        dy = y - start_y
        duration = now - start_time

        # Prevent division by zero
        if duration <= 0:
            return None

        # Calculate average horizontal velocity
        velocity = dx / duration

        # Reject insufficient horizontal movement
        if abs(dx) < self.min_displacement:
            return None

        # Reject excessive vertical movement
        if abs(dy) > self.max_vertical_displacement:
            return None

        # Reject movements that are too slow
        if abs(velocity) < self.min_velocity:
            return None

        # Determine swipe direction
        if dx > 0:
            command = "NEXT_TRACK"
        else:
            command = "PREVIOUS_TRACK"

        # Record successful swipe
        self.last_swipe_time = now
        self.swipe_latched = True
        self.position_history.clear()

        return command

    def reset(self):

        # Reset swipe detection state
        self.position_history.clear()
        self.swipe_latched = False
        self.release_start_time = None