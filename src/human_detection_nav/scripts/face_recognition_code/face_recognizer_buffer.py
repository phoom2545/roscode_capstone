import cv2
import numpy as np
from deepface import DeepFace
import pickle

class FaceRecognizer:
    def __init__(self, classifier_path="/home/rai/ired_ws/src/human_detection_nav/scripts/svm_classifier_windows.pkl", 
                 confidence_threshold=30.0, 
                 buffer_size=10,  # Number of frames to buffer
                 recognition_threshold=0.7):  # Percentage of frames needed for confirmation
        # Load the trained classifier
        with open(classifier_path, "rb") as f:
            self.svm = pickle.load(f)

        # Load the pre-trained face detection model (Haar Cascade)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.confidence_threshold = confidence_threshold
        self.recognized_name = None
        
        # Recognition buffer parameters
        self.buffer_size = buffer_size
        self.recognition_threshold = recognition_threshold
        self.recognition_buffer = []
        self.confirmed_name = None
        self.processing_buffer = False
        
        print(f"FaceRecognizer initialized with buffer_size={buffer_size}, threshold={recognition_threshold}")

    def recognize_face(self, frame):
        """
        Recognize faces in the given frame with buffering for improved accuracy.

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
            # No face detected, clear buffer
            if len(self.recognition_buffer) > 0:
                print("No face detected, clearing buffer")
            self.recognition_buffer = []
            self.processing_buffer = False
            return frame, None

        print(f"Detected {len(faces)} faces")
        current_recognition = None
        max_confidence_score = 0

        for (x, y, w, h) in faces:
            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Extract the face region
            face = frame[y:y + h, x:x + w]

            try:
                # Use DeepFace to recognize the face
                print("Attempting DeepFace recognition...")
                face_embedding = DeepFace.represent(img_path=face, model_name="Facenet", enforce_detection=False)
                embedding = face_embedding[0]["embedding"]

                # Get probability estimates (confidence scores)
                confidence_scores = self.svm.predict_proba([embedding])[0]
                max_confidence = np.max(confidence_scores) * 100  # Convert to percentage
                predicted_person = self.svm.predict([embedding])[0]
                
                print(f"DeepFace prediction: {predicted_person} with confidence {max_confidence:.2f}%")

                # Track the highest confidence recognition in this frame
                if max_confidence > max_confidence_score:
                    max_confidence_score = max_confidence
                    
                    # Only consider as a valid recognition if confidence exceeds threshold
                    if max_confidence >= self.confidence_threshold:
                        current_recognition = predicted_person
                        label = f"{predicted_person} ({max_confidence:.2f}%)"
                        label_color = (0, 255, 0)  # Green for high confidence
                    else:
                        current_recognition = "Unknown"
                        label = f"Unknown ({max_confidence:.2f}%)"
                        label_color = (0, 165, 255)  # Orange for low confidence

                # Display the label above the rectangle
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, label_color, 2)

            except Exception as e:
                print(f"Error recognizing face: {e}")
                # Label as unknown if there's an error
                cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                current_recognition = "Unknown"

        # Update recognition buffer
        if current_recognition:
            print(f"Adding '{current_recognition}' to buffer")
            self.recognition_buffer.append(current_recognition)
            
            # Keep buffer at specified size
            if len(self.recognition_buffer) > self.buffer_size:
                self.recognition_buffer.pop(0)
            
            # Start processing buffer when it's full
            if len(self.recognition_buffer) == self.buffer_size and not self.processing_buffer:
                print("Buffer full, starting processing")
                self.processing_buffer = True
            
            # Process buffer to determine confirmed name
            if self.processing_buffer:
                # Count occurrences of each name in buffer
                name_counts = {}
                for name in self.recognition_buffer:
                    if name in name_counts:
                        name_counts[name] += 1
                    else:
                        name_counts[name] = 1
                
                print(f"Buffer contents: {name_counts}")
                
                # Find the most frequent name
                most_frequent_name = max(name_counts, key=name_counts.get)
                most_frequent_count = name_counts[most_frequent_name]
                
                # Calculate percentage of frames with this name
                percentage = most_frequent_count / len(self.recognition_buffer)
                
                # Display buffer status on frame
                buffer_status = f"Buffer: {len(self.recognition_buffer)}/{self.buffer_size}"
                cv2.putText(frame, buffer_status, (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                if most_frequent_name != "Unknown":
                    confidence_text = f"Confidence: {percentage*100:.1f}% {most_frequent_name}"
                    cv2.putText(frame, confidence_text, (10, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                # If percentage exceeds threshold and not Unknown, confirm the name
                if percentage >= self.recognition_threshold and most_frequent_name != "Unknown":
                    self.confirmed_name = most_frequent_name
                    print(f"CONFIRMED: {self.confirmed_name} with {percentage*100:.1f}% confidence")
                    # Add confirmation text to frame
                    cv2.putText(frame, f"CONFIRMED: {self.confirmed_name}", (10, 90), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    return frame, self.confirmed_name
                else:
                    print(f"Not yet confirmed: {most_frequent_name} with {percentage*100:.1f}% confidence (threshold: {self.recognition_threshold*100}%)")
        
        # Return frame with no confirmed name yet
        return frame, None

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

    