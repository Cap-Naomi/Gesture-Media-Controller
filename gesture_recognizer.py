import time


class GestureRecognizer:

    def __init__(self):

        # Map gestures to internal commands
        self.gesture_commands = {
            "Closed_Fist": "PLAY_PAUSE",
            "Thumb_Up": "VOLUME_UP",
            "Thumb_Down": "VOLUME_DOWN",
            "Pointing_Up": "MUTE",
            "Victory": "TOGGLE_CONTROLS"
        }

        # Gesture validation settings
        self.confidence_threshold = 0.6
        self.hold_duration = 0.4
        self.volume_interval = 0.2

        # Initial gesture state
        self.current_gesture = None
        self.gesture_start_time = 0
        self.gesture_executed = False
        self.last_volume_time = 0

        # Application state
        self.controls_enabled = True

    def recognize(self, gesture_name, confidence):

        now = time.monotonic()

        # Reject unsupported or uncertain gestures
        if (confidence < self.confidence_threshold
                or gesture_name not in self.gesture_commands):

            self.reset()
            return None

        # Detect a new gesture
        if gesture_name != self.current_gesture:

            self.current_gesture = gesture_name
            self.gesture_start_time = now
            self.gesture_executed = False

        # Check how long the gesture has been held
        held_time = now - self.gesture_start_time

        if held_time < self.hold_duration:
            return None

        command = self.gesture_commands[gesture_name]

        # Handle enabling and disabling controls
        if command == "TOGGLE_CONTROLS":

            if not self.gesture_executed:

                self.controls_enabled = not self.controls_enabled
                self.gesture_executed = True

                return command

            return None

        # Ignore media commands when controls are disabled
        if not self.controls_enabled:
            return None

        # Allow volume commands to repeat
        if command in ("VOLUME_UP", "VOLUME_DOWN"):

            if now - self.last_volume_time >= self.volume_interval:

                self.last_volume_time = now
                return command

            return None

        # Execute other commands only once per gesture
        if not self.gesture_executed:

            self.gesture_executed = True
            return command

        return None

    def reset(self):

        self.current_gesture = None
        self.gesture_start_time = 0
        self.gesture_executed = False