import cv2

from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from media_controller import MediaController
from swipe_detector import SwipeDetector


def main():

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access webcam.")
        return

    tracker = None

    try:

        # Initialize application components
        tracker = HandTracker()
        recognizer = GestureRecognizer()
        controller = MediaController()
        swipe_detector = SwipeDetector()

        last_action = "None"

        while True:

            # Capture webcam frame
            success, frame = cap.read()

            if not success:
                print("Error: Unable to capture frame.")
                break

            # Mirror the frame horizontally
            frame = cv2.flip(frame, 1)

            # Perform hand tracking and gesture recognition
            result = tracker.process_frame(frame)

            # Draw hand landmarks
            tracker.draw_landmarks(frame, result)

            # Initialize default gesture information
            gesture_text = "No hand detected"
            gesture_name = None
            confidence = 0.0
            landmarks = None

            # Extract hand landmarks
            if result.hand_landmarks:

                landmarks = result.hand_landmarks[0]
                gesture_text = "No recognized gesture"

            # Extract gesture classification
            if result.gestures and result.gestures[0]:

                gesture = result.gestures[0][0]

                gesture_name = gesture.category_name
                confidence = gesture.score

                gesture_text = (
                    f"{gesture_name}: {confidence:.1%}"
                )

            # Process static gestures
            command = recognizer.recognize(
                gesture_name,
                confidence
            )

            # Process dynamic swipe gestures
            if recognizer.controls_enabled:

                swipe_command = swipe_detector.detect(
                    landmarks,
                    gesture_name,
                    confidence
                )

                # Static commands take priority
                if command is None:
                    command = swipe_command

            else:

                # Clear swipe history when controls are disabled
                swipe_detector.reset()

            # Handle application state changes
            if command == "TOGGLE_CONTROLS":

                if recognizer.controls_enabled:
                    last_action = "Controls enabled"
                else:
                    last_action = "Controls disabled"

                swipe_detector.reset()

                print(last_action)

            # Execute media commands
            elif command is not None:

                if controller.execute(command):

                    last_action = command
                    print(f"Executed: {command}")

            # Determine control status
            status = (
                "ACTIVE" if recognizer.controls_enabled
                else "DISABLED"
            )

            status_color = (
                (0, 255, 0) if recognizer.controls_enabled
                else (0, 0, 255)
            )

            # Display detected gesture and confidence
            cv2.putText(
                frame,
                gesture_text,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            # Display control status
            cv2.putText(
                frame,
                f"Controls: {status}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                status_color,
                2
            )

            # Display last executed action
            cv2.putText(
                frame,
                f"Last action: {last_action}",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            # Display processed webcam frame
            cv2.imshow("Gesture Media Controller", frame)

            # Exit when Q is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        # Release application resources
        if tracker is not None:
            tracker.close()

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()