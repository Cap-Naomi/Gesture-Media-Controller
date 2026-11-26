import time


class GestureRecognizer:

    def __init__(self):

        self.gesture_commands = {
            "Closed_Fist": "PLAY_PAUSE",
            "Thumb_Up": "VOLUME_UP",
            "Thumb_Down": "VOLUME_DOWN",
            "Pointing_Up": "MUTE",
            "Victory": "TOGGLE_CONTROLS"
        }

        # Validation settings
        self.confidence_threshold = 0.6
        self.hold_duration = 0.4
        self.volume_interval = 0.2
        self.release_duration = 0.25
        self.command_cooldown = 0.5

        # Gesture state
        self.current_gesture = None
        self.gesture_start_time = None
        self.release_start_time = None
        self.gesture_executed = False

        # Command timing
        self.last_volume_time = float("-inf")
        self.last_command_time = float("-inf")

        # Application state
        self.controls_enabled = True

    def recognize(self, gesture_name, confidence):

        now = time.monotonic()

        valid_gesture = (
            confidence >= self.confidence_threshold
            and gesture_name in self.gesture_commands
        )

        # Check whether the current gesture has changed
        # or is no longer confidently detected
        if self.current_gesture is not None:

            if (not valid_gesture
                    or gesture_name != self.current_gesture):

                # Start release timer
                if self.release_start_time is None:
                    self.release_start_time = now

                # Confirm that the gesture was released
                if (now - self.release_start_time
                        >= self.release_duration):

                    self.reset()

                return None

        # Ignore unsupported gestures
        if not valid_gesture:
            return None

        # Recover from a brief interruption
        if self.release_start_time is not None:

            # Exclude interrupted time from the hold duration
            self.gesture_start_time += (
                now - self.release_start_time
            )

            self.release_start_time = None

        # Register a new gesture
        if self.current_gesture is None:

            self.current_gesture = gesture_name
            self.gesture_start_time = now
            self.gesture_executed = False

        # Confirm gesture hold duration
        held_time = now - self.gesture_start_time

        if held_time < self.hold_duration:
            return None

        command = self.gesture_commands[gesture_name]

        # Enable or disable controls
        if command == "TOGGLE_CONTROLS":

            if self.gesture_executed:
                return None

            if (now - self.last_command_time
                    < self.command_cooldown):
                return None

            self.controls_enabled = not self.controls_enabled
            self.gesture_executed = True
            self.last_command_time = now

            return command

        # Ignore media gestures when disabled
        if not self.controls_enabled:
            return None

        # Repeating volume commands
        if command in ("VOLUME_UP", "VOLUME_DOWN"):

            if now - self.last_volume_time >= self.volume_interval:

                self.last_volume_time = now
                return command

            return None

        # Prevent repeated discrete commands
        if self.gesture_executed:
            return None

        # Check command cooldown
        if now - self.last_command_time < self.command_cooldown:
            return None

        # Execute discrete command
        self.gesture_executed = True
        self.last_command_time = now

        return command

    def reset(self):

        self.current_gesture = None
        self.gesture_start_time = None
        self.release_start_time = None
        self.gesture_executed = False