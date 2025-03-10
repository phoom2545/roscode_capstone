# face_recognizer.py
import cv2
import numpy as np
from deepface import DeepFace
import pickle

class FaceRecognizer:
    def __init__(self, classifier_path="svm_classifier_windows.pkl", confidence_threshold=50.0):
        # Load the trained classifier
        with open(classifier_path, "rb") as f:
            self.svm = pickle.load(f)

        # Load the pre-trained face detection model (Haar Cascade)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.confidence_threshold = confidence_threshold
        self.recognized_name = None

    def recognize_face(self, frame):
        """
        Recognize faces in the given frame.

        Args:
            frame: The image frame to process

        Returns:
            tuple: (processed_frame, recognized_name)
        """
        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            return frame, None

        for (x, y, w, h) in faces:
            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Extract the face region
            face = frame[y:y + h, x:x + w]

            try:
                # Use DeepFace to recognize the face
                face_embedding = DeepFace.represent(img_path=face, model_name="Facenet", enforce_detection=False)
                embedding = face_embedding[0]["embedding"]

                # Get probability estimates (confidence scores)
                confidence_scores = self.svm.predict_proba([embedding])[0]
                max_confidence = np.max(confidence_scores) * 100  # Convert to percentage
                predicted_person = self.svm.predict([embedding])[0]

                # Only label as the predicted person if confidence exceeds threshold
                if max_confidence >= self.confidence_threshold:
                    label = f"{predicted_person} ({max_confidence:.2f}%)"
                    label_color = (0, 255, 0)  # Green for high confidence
                    self.recognized_name = predicted_person
                else:
                    label = f"Unknown ({max_confidence:.2f}%)"
                    label_color = (0, 165, 255)  # Orange for low confidence
                    self.recognized_name = "Unknown"

                # Display the label above the rectangle
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, label_color, 2)

            except Exception as e:
                print(f"Error recognizing face: {e}")
                # Label as unknown if there's an error
                cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                self.recognized_name = "Unknown"

        return frame, self.recognized_name

# For testing the module independently
if __name__ == "__main__":
    recognizer = FaceRecognizer()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame, name = recognizer.recognize_face(frame)

        if name:
            print(f"Recognized: {name}")

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()