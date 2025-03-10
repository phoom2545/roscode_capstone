#!/usr/bin/env python3
# main_ros.py
import rospy
import cv2
import time
from human_detector import HumanDetector
from face_recognizer import FaceRecognizer
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class RobotController:
    def __init__(self):
        rospy.init_node('robot_controller', anonymous=True)

        # Initialize components
        self.human_detector = HumanDetector()
        self.face_recognizer = FaceRecognizer()
        self.bridge = CvBridge()

        # ROS Publishers
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.human_detected_pub = rospy.Publisher('/human_detected', Bool, queue_size=10)

        # State variables
        self.human_detected = False
        self.face_recognized = False
        self.key_pressed = False
        self.recognized_name = None
        self.process_completed = False
        self.face_detection_start_time = None
        self.min_detection_time = 2.0
        self.robot_paused = False

        # Camera setup
        self.cap = cv2.VideoCapture(0)  # Change to your camera index
        if not self.cap.isOpened():
            rospy.logerr("Error: Could not open webcam.")
            return

        rospy.loginfo("Robot controller initialized. Press 's' to trigger interaction when face is recognized.")

    def pause_robot(self):
        """Send zero velocity command to stop the robot"""
        stop_cmd = Twist()
        self.cmd_vel_pub.publish(stop_cmd)
        self.robot_paused = True
        self.human_detected_pub.publish(Bool(True))

    def resume_robot(self):
        """Resume robot movement"""
        self.robot_paused = False
        self.human_detected_pub.publish(Bool(False))

    def run(self):
        rate = rospy.Rate(10)  # 10Hz

        while not rospy.is_shutdown():
            ret, frame = self.cap.read()
            if not ret:
                rospy.logerr("Error: Could not read frame.")
                break

            frame = cv2.resize(frame, (640, 480))

            # Step 1: Human Detection
            if not self.human_detected:
                self.human_detected, frame = self.human_detector.detect_humans(frame)
                status_text = "Looking for humans..."

                if self.human_detected:
                    rospy.loginfo("Human detected! Starting face recognition...")
                    status_text = "Human detected! Starting face recognition..."
                    self.pause_robot()

            # Step 2: Face Recognition
            elif self.human_detected and not self.face_recognized:
                current_time = time.time()

                if self.face_detection_start_time is None:
                    self.face_detection_start_time = current_time

                if current_time - self.face_detection_start_time >= self.min_detection_time:
                    status_text = "Face Recognition started.."
                    frame, name = self.face_recognizer.recognize_face(frame)
                    if name:
                        self.recognized_name = name
                        self.face_recognized = True
                        rospy.loginfo(f"Face recognized: {self.recognized_name}")
                        status_text = f"Face recognized: {self.recognized_name}. Press 's' to start interaction."
                else:
                    status_text = "Starting Face Recognition in progress..."

            # Step 3: Wait for Key Press
            elif self.face_recognized and not self.key_pressed:
                status_text = f"Face recognized: {self.recognized_name}. Press 's' to start interaction."

            # Step 4: Process Completion
            elif self.face_recognized and self.key_pressed and not self.process_completed:
                status_text = "Interaction triggered! Process Completed."
                rospy.loginfo("Process Completed")
                self.process_completed = True
                self.resume_robot()

            # Step 5: Completed State
            elif self.process_completed:
                status_text = "Process Completed. Press 'q' to exit."

            # Display status on frame
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('Robot Vision', frame)

            # Key handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and self.face_recognized and not self.key_pressed:
                self.key_pressed = True
                rospy.loginfo("Interaction triggered by key press!")

            rate.sleep()

        self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        self.resume_robot()  # Ensure robot can move again
        rospy.loginfo("Robot controller shutdown complete.")

if __name__ == '__main__':
    try:
        controller = RobotController()
        controller.run()
    except rospy.ROSInterruptException:
        pass