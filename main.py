import cv2
from hand_tracker import HandTracker


def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access webcam.")
        return

    tracker = None

    try:

        # Initialize the hand tracking model once
        tracker = HandTracker()

        while True:

            success, frame = cap.read()

            if not success:
                print("Error: Unable to capture frame.")
                break

            # Mirror the frame
            frame = cv2.flip(frame, 1)

            # Perform hand tracking and gesture recognition
            result = tracker.process_frame(frame)

            # Draw hand landmarks
            tracker.draw_landmarks(frame, result)

            # Default display text
            gesture_text = "No hand detected"

            if result.hand_landmarks:
                gesture_text = "No recognized gesture"

            # Get the predicted gesture
            if result.gestures and result.gestures[0]:

                gesture = result.gestures[0][0]

                gesture_name = gesture.category_name
                confidence = gesture.score

                gesture_text = (
                    f"{gesture_name}: {confidence:.1%}"
                )

            # Display gesture and confidence
            cv2.putText(
                frame,
                gesture_text,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            # Display the processed frame
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