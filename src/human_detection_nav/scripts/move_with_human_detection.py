#!/usr/bin/python3
import rospy
import tf.transformations
import time
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Twist, Pose, Point, PoseStamped, PoseWithCovarianceStamped, Quaternion
from actionlib_msgs.msg import GoalStatusArray, GoalStatus
import actionlib
from std_srvs.srv import Empty
import threading
import sys
import tty
import termios
import cv2
import requests
from ultralytics import YOLO
from face_recognizer import FaceRecognizer  # Add this import
from interactive_code import SpeechAssistant

navigate_waypoint_flag = 0
api_url_navigation_state = "http://172.16.0.200:5000/navigation_status"

class HumanDetector:
    def __init__(self):
        # Initialize necessary variables
        self.model = YOLO('yolov5su.pt')
        self.human_detected = False
        self.detection_thread = None
        self.stop_detection = False
        self.cap = None
        self.face_recognizer = FaceRecognizer()  # Initialize face recognizer
        self.speech_assistant = SpeechAssistant()  # Initialize speech assistant
        self.api_url = "http://172.16.0.200:5000"  # Flask API URL

    def start_detection(self):
        self.cap = cv2.VideoCapture(6)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            return

        self.detection_thread = threading.Thread(target=self.detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()

    def check_button_state(self, button_type):
        """
        Check the state of a button from the Flask API.
        """
        try:
            response = requests.get(f"{self.api_url}/button")
            button_states = response.json()
            return button_states.get(button_type, False)
        except requests.exceptions.RequestException as e:
            print(f"Error checking button state: {e}")
            return False
        
    def notify_face_recognized(self):
        """
        Notify the Flask API that a face has been recognized.
        """
        try:
            response = requests.post(f"{self.api_url}/face_recognized")
            if response.status_code == 200:
                print("Face recognition status updated on the server.")
        except requests.exceptions.RequestException as e:
            print(f"Error notifying face recognition: {e}")

    def detection_loop(self):
        global navigate_waypoint_flag
        
        while not self.stop_detection and not rospy.is_shutdown():
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.resize(frame, (640, 480))
            
            # CHANGE: Skip human detection if in navigation mode
            if navigate_waypoint_flag == 1:
                cv2.putText(frame, "Navigation Mode - Human Detection Disabled", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow('Human Detection', frame)
                cv2.waitKey(1)
                continue
                
            results = self.model.predict(frame, conf=0.5, verbose=False, stream=False)

            self.human_detected = False
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    if cls == 0:  # Class 0 is "person"
                        self.human_detected = True
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = box.conf[0]
                        label = f"Person {conf:.2f}"
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            if self.human_detected:
                # Perform face recognition when human is detected
                frame, recognized_name = self.face_recognizer.recognize_face(frame)

                if recognized_name:
                    print(f"\nRecognized person: {recognized_name}")
                    print("Face Recognized! Waiting for button press...")
                    self.notify_face_recognized()

                    # Face Recognized screen when the face is recognized and wait for button to press
                    while not (self.check_button_state("interactive") or self.check_button_state("navigation")):
                        
                        cv2.putText(frame, f"'{recognized_name}' is recognized. Press 'Interactive' button", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.imshow('Human Detection', frame)
                        cv2.waitKey(1)

                    # Check if the 'interactive' button is pressed
                    if self.check_button_state("interactive"):
                        
                        print("\nInteractive mode activated!")
                        
                        # Loop in the interactive mode until the 'interactive' state in the API is false
                        while self.check_button_state("interactive"):

                            cv2.putText(frame, f"'{recognized_name}' is recognized. Press 'Interactive' button to exit", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.imshow('Human Detection', frame)
                            cv2.waitKey(1)

                            # Start Speech Assistant (interactive mode)
                            self.speech_assistant.run()
                            print("Exiting interactive mode...")

                    # Check if the 'navigation' button is pressed
                    elif self.check_button_state("navigation"):
                        
                        navigate_waypoint_flag = 1
                        print("Change waypoint to 1")
                        print("Navigation mode activated")

                    # Flush the frame buffer by skipping a few frames
                    for _ in range(5):  # Skip 5 frames
                        self.cap.read()

            cv2.imshow('Human Detection', frame)
            cv2.waitKey(1)

        
    def stop(self):
        """
        Stop the detection thread and release resources
        """
        self.stop_detection = True
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()


# Keyboard controller to listen to keyboard inputs
class KeyboardController:
    def __init__(self):
        self.should_stop = False
        self.paused = False

    # Grab the key pressed by the user
    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    # Check if the key is pressed and perform the corresponding action
    def keyboard_listener(self):
        while not rospy.is_shutdown() and not self.should_stop:
            key = self.get_key()
            if key == 'q':
                print("\nPausing robot movement...")
                self.paused = True
            elif key == 't':
                print("\nResuming robot movement...")
                self.paused = False
            elif key == 'x':
                print("\nExiting program...")
                self.should_stop = True
                rospy.signal_shutdown("User requested exit")
                break


class moveBaseAction():
    def __init__(self, keyboard_controller, human_detector,face_recognizer):
        self.move_base_action = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
        self.move_base_action.wait_for_server(rospy.Duration(5))
        self.keyboard_controller = keyboard_controller
        self.human_detector = human_detector
        self.face_recognizer = face_recognizer

        # Clear costmap service
        rospy.wait_for_service('/move_base/clear_costmaps')
        self.clear_costmap_service = rospy.ServiceProxy('/move_base/clear_costmaps', Empty)


    def createGoal(self, x, y, theta):
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        quat = tf.transformations.quaternion_from_euler(0, 0, theta)
        goal.target_pose.pose = Pose(
            Point(x, y, 0.000),
            Quaternion(quat[0], quat[1], quat[2], quat[3])
        )
        return goal

    def moveToPoint(self, x, y, theta):
        target_point = self.createGoal(x, y, theta)
        return self.moveToGoal(target_point)

    def moveToGoal(self, goal):
        global navigate_waypoint_flag
        # CHANGED: Added tracking of initial flag value to detect changes
        initial_flag_value = navigate_waypoint_flag
        # CHANGED: Added descriptive waypoint type for better logging
        initial_waypoint_type = "default" if navigate_waypoint_flag == 0 else "navigation"

        print(f"\nMoving to x:{goal.target_pose.pose.position.x:.2f}, y:{goal.target_pose.pose.position.y:.2f}, orientation:{goal.target_pose.pose.orientation.z:.2f}")
        self.move_base_action.send_goal(goal)

        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            current_waypoint_type = "default" if navigate_waypoint_flag == 0 else "navigation"

            if current_waypoint_type != initial_waypoint_type:
                print(f"Navigation mode changed from {initial_waypoint_type} to {current_waypoint_type}! Canceling current goal.")
                self.move_base_action.cancel_goal()
                return False
            
            if self.keyboard_controller.should_stop:
                self.move_base_action.cancel_goal()
                return False

            # CHANGE: Only check for human detection if NOT in navigation mode
            if self.human_detector.human_detected and navigate_waypoint_flag == 0:
                print("Human detected! Stopping robot...")
                self.move_base_action.cancel_goal()

                # Wait until human is no longer detected
                while self.human_detector.human_detected and not rospy.is_shutdown():
                    rate.sleep() # sleep for 0.1 seconds while in the loop
                    current_waypoint_type = "default" if navigate_waypoint_flag == 0 else "navigation"

                    if current_waypoint_type != initial_waypoint_type:
                        print(f"Navigation mode changed during human detection! Canceling current goal.")
                        return False
                    rate.sleep()

                # Continue moving after the human is no longer detected
                print("No humans detected. Resuming movement...")
                self.move_base_action.send_goal(goal)

            if self.keyboard_controller.paused:
                self.move_base_action.cancel_goal()
                print("Robot paused. Press 't' to resume...")
                while self.keyboard_controller.paused and not rospy.is_shutdown():
                    # CHANGED: Added check for navigation mode changes during pause
                    current_waypoint_type = "default" if navigate_waypoint_flag == 0 else "navigation"
                    if current_waypoint_type != initial_waypoint_type:
                        print(f"Navigation mode changed during pause! Canceling current goal.")
                        return False
                    rate.sleep()

                if not self.keyboard_controller.paused:
                    print("Resuming movement...")
                    self.move_base_action.send_goal(goal)

            state = self.move_base_action.get_state()
            if state == GoalStatus.SUCCEEDED:
                print("Goal reached successfully!")
                # Call the function to clear the costmap
                self.clear_costmap()
                return True
            elif state in [GoalStatus.ABORTED, GoalStatus.REJECTED, GoalStatus.PREEMPTED]:
                print("Failed to reach goal!")
                return False

            rate.sleep()

    # Function to clear the costmap
    def clear_costmap(self):
        try:
            # Call the service to clear the costmap
            self.clear_costmap_service()
            print("Costmap Cleared!")
        except rospy.ServiceException as e:
            print("Failed to clear costmap:", e)

# MAIN CODE
def main():

    # Init ROS node for move_to_goal
    rospy.init_node('move_to_goal', anonymous=True)

    # Initialize controllers
    keyboard_controller = KeyboardController()
    human_detector = HumanDetector()
    face_recognizer = FaceRecognizer() # initialize FaceRecognizer

    # Start the human detection
    human_detector.start_detection()

    # Start keyboard listener parallelly using thread
    keyboard_thread = threading.Thread(target=keyboard_controller.keyboard_listener)
    keyboard_thread.daemon = True
    keyboard_thread.start()

    mba = moveBaseAction(keyboard_controller, human_detector,face_recognizer) 

    global navigate_waypoint_flag   

    # waypoints at Home
    default_waypoints = [
        (1.356, 0.957, 4.712),
        (1.852, -0.773, 0),
        (-0.040, -2.634, 3.14),
        (-0.041, -4.957, 1.57)
    ]
    navigate_waypoints = [
        (0.653, -0.725, 0.034),
        (1.732, 0.627, -1.553),
        (-0.382, -1.936, -0.020)
    ]

    # inside lab waypoints
    # default_waypoints = [
    #     (1.831, 1.137, -1.631),
    #     (2.852, 0.206, 3.044),
    #     (0.167, 0.044, 0.064)
    # ]
    # navigate_waypoints = [
    #     (0.653, -0.725, 0.034),
    #     (1.732, 0.627, -1.553),
    #     (-0.382, -1.936, -0.020)
    # ]




    # waypoints at lab (two)
    # waypoints = [
    # (1.498, -2.150, 1.495),
    # (1.369, -0.537, 0),
    # (1.692, 1.092, 0),
    # (0.032, -0.011, -1.555)
    # ]

    # waypoints = [
    #     (0.307, -1.146, 1.529),
    #     (0.269, -0.557, 3.073),
    #     (0.029, -0.250, 0.018),
    # ]


    # # for robotlab
    # waypoints = [
    #     (2.391, 0.243, 1.596),
    #     (3.431, 2.005, -1.520),
    #     (1.675, -0.156, 3.112),
    #     (-0.061,0.119,0.060)
    # ]


    try:
        while not rospy.is_shutdown() and not keyboard_controller.should_stop:
             
            if navigate_waypoint_flag == 0:
                waypoints = default_waypoints
                print("Default waypoints selected!")
            elif navigate_waypoint_flag == 1:
                waypoints = navigate_waypoints
                print("Navigation waypoints selected!")

            for x, y, theta in waypoints:
                # navigate_waypoint_flag_current = navigate_waypoint_flag
                if keyboard_controller.should_stop:
                    break

                if navigate_waypoint_flag != (0 if waypoints == default_waypoints else 1):
                    print("Navigation mode changed, restarting with new waypoints")
                    break
                
                # if keyboard doesn't stop, move to the next waypoint
                success = mba.moveToPoint(x, y, theta)

               

                if not success:
                    print("Failed to reach waypoint, moving to next...")
                rospy.sleep(1)

            # After completing all waypoints in navigation mode, reset to default
            if navigate_waypoint_flag == 1 and waypoints == navigate_waypoints:
                print("Navigation completed. Returning to default waypoints.")

                # Send the state that the navigation is completed
                global api_url_navigation_state
                try:
                    response = requests.post(api_url_navigation_state)
                    if response.status_code == 200:
                        print("Navigation status updated on the server.")
                except requests.exceptions.RequestException as e:
                    print(f"Error notifying Navigation status to server: {e}")

                # Reset the navigate_waypoint_flag to 0. Returns to default waypoints
                navigate_waypoint_flag = 0

    # Handle the exception
    except rospy.ROSInterruptException:
        pass

    # Finally, stop the keyboard controller and human detection
    finally:
        keyboard_controller.should_stop = True
        human_detector.stop()
        keyboard_thread.join(timeout=1.0)

if __name__ == '__main__':
    main()


