# main.py
import cv2
import time
import threading
from human_detector import HumanDetector
from face_recognizer import FaceRecognizer
from wakeword_detector import WakewordDetector

def main():
    # Initialize the components
    human_detector = HumanDetector()
    face_recognizer = FaceRecognizer()
    wakeword_detector = WakewordDetector(listen_timeout=10, process_timeout=5)

    # Open the webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # State variables
    human_detected = False
    face_recognized = False
    wakeword_status = None  # None = not started, 0 = no speech, -1 = error, 1 = detected
    recognized_name = None
    wakeword_thread = None
    process_completed = False

    print("Starting the system. Press 'q' to quit.")

    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Resize the frame to a smaller size
        frame = cv2.resize(frame, (640, 480))

        # Step 1: Always looking for humans
        if not human_detected:
            human_detected, frame = human_detector.detect_humans(frame)
            status_text = "Looking for humans..."

            if human_detected:
                print("Human detected! Starting face recognition...")
                status_text = "Human detected! Starting face recognition..."

        # Step 2: If human detected, start face recognition
        elif human_detected and not face_recognized:
            frame, name = face_recognizer.recognize_face(frame)
            if name:
                recognized_name = name
                face_recognized = True
                print(f"Face recognized: {recognized_name}")
                status_text = f"Face recognized: {recognized_name}. Listening for wakeword..."

                # Start wakeword detection in a separate thread
                def wakeword_thread_func():
                    nonlocal wakeword_status
                    wakeword_status = wakeword_detector.detect_wakeword()

                wakeword_thread = threading.Thread(target=wakeword_thread_func)
                wakeword_thread.daemon = True
                wakeword_thread.start()

        # Step 3: After face recognition, check for wakeword
        elif face_recognized and wakeword_status is None:
            status_text = f"Face recognized: {recognized_name}. Listening for wakeword 'hey lisa'..."

        # Step 4: Process wakeword detection results
        elif face_recognized and wakeword_status is not None and not process_completed:
            if wakeword_status == 1:
                print("Wakeword detected!")
                status_text = "Wakeword detected! Process Completed."
                print("Process Completed")
                process_completed = True
            elif wakeword_status == -1:
                print("Error: Wakeword could not be processed")
                status_text = "Error: Wakeword could not be processed. Press 'q' to exit."
                process_completed = True
            elif wakeword_status == 0:
                print("No speech detected during wakeword detection")
                status_text = "No speech detected. Press 'q' to exit."
                process_completed = True

        # Step 5: All steps completed
        elif process_completed:
            if wakeword_status == 1:
                status_text = "Process Completed. Press 'q' to exit."
            else:
                status_text = "Process Failed. Press 'q' to exit."

        # Display status on the frame
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow('Integrated System', frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Add a small delay to reduce CPU usage
        time.sleep(0.01)

    # Release the webcam and close the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()