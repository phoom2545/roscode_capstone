# human_detector.py
import cv2
from ultralytics import YOLO

class HumanDetector:
    def __init__(self, model_path='yolov5su.pt', conf_threshold=0.5):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.human_detected = False

    def detect_humans(self, frame):
        """
        Detect humans in a frame using YOLOv5.

        Args:
            frame: The image frame to process

        Returns:
            bool: True if a human is detected, False otherwise
            frame: The processed frame with detection boxes
        """
        results = self.model.predict(frame, conf=self.conf_threshold)

        # Check if any person is detected
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                if cls == 0:  # Class 0 is "person"
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    label = f"Person {conf:.2f}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    self.human_detected = True
                    return True, frame

        self.human_detected = False
        return False, frame

# For testing the module independently
if __name__ == "__main__":
    detector = HumanDetector()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.resize(frame, (640, 480))
        human_detected, frame = detector.detect_humans(frame)

        status = "Human Detected" if human_detected else "No Human Detected"
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Human Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()