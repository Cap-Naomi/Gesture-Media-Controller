import cv2


def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)

    # Verify webcam connection
    if not cap.isOpened():
        print("Error: Unable to access webcam.")
        return

    try:
        while True:
            # Capture current frame
            success, frame = cap.read()

            if not success:
                print("Error: Unable to capture frame.")
                break

            # Mirror the frame horizontally
            frame = cv2.flip(frame, 1)

            # Display the frame
            cv2.imshow("Gesture Media Controller", frame)

            # Exit when Q is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()