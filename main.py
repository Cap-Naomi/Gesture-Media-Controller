import cv2

from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from media_controller import MediaController


def main():

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

        last_action = "None"

        while True:

            success, frame = cap.read()

            if not success:
                print("Error: Unable to capture frame.")
                break

            frame = cv2.flip(frame, 1)

            # Perform machine learning inference
            result = tracker.process_frame(frame)

            # Draw hand landmarks
            tracker.draw_landmarks(frame, result)

            gesture_text = "No hand detected"

            if result.hand_landmarks:
                gesture_text = "No recognized gesture"

            if result.gestures and result.gestures[0]:

                gesture = result.gestures[0][0]

                gesture_name = gesture.category_name
                confidence = gesture.score

                gesture_text = (
                    f"{gesture_name}: {confidence:.1%}"
                )

                # Interpret and validate gesture
                command = recognizer.recognize(
                    gesture_name,
                    confidence
                )

                # Execute validated command
                if command == "TOGGLE_CONTROLS":

                    if recognizer.controls_enabled:
                        last_action = "Controls enabled"
                    else:
                        last_action = "Controls disabled"

                    print(last_action)

                elif command is not None:

                    if controller.execute(command):

                        last_action = command
                        print(f"Executed: {command}")

            else:

                # Allow the recognizer to confirm gesture release
                recognizer.recognize(None, 0.0)

            # Determine control status
            status = (
                "ACTIVE" if recognizer.controls_enabled
                else "DISABLED"
            )

            status_color = (
                (0, 255, 0) if recognizer.controls_enabled
                else (0, 0, 255)
            )

            # Display detected gesture
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

            cv2.imshow("Gesture Media Controller", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        if tracker is not None:
            tracker.close()

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()