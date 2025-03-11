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
from ultralytics import YOLO

class HumanDetector:
    def __init__(self):

        # Initialize necessary variables
        self.model = YOLO('yolov5su.pt')
        self.human_detected = False
        self.detection_thread = None
        self.stop_detection = False
        self.cap = None

    # Start the human detection on thread (parallely)
    def start_detection(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            return

        self.detection_thread = threading.Thread(target=self.detection_loop)  # Create a thread for human detection (use detection_loop function)
        self.detection_thread.daemon = True
        self.detection_thread.start()

    # Use the model to predict human and draw bounding box (class 0 is for human detection)
    def detection_loop(self):
        while not self.stop_detection and not rospy.is_shutdown():
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.resize(frame, (640, 480))
            results = self.model.predict(frame,
                                      conf=0.5,
                                      verbose=False,  # This disables the progress bar
                                      stream=False)    # This makes it more efficient

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

            cv2.imshow('Human Detection', frame)
            cv2.waitKey(1)

    # Call this function to stop the human detection
    def stop(self):
        self.stop_detection = True
        if self.cap is not None:
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
    def __init__(self, keyboard_controller, human_detector):
        self.move_base_action = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
        self.move_base_action.wait_for_server(rospy.Duration(5))
        self.keyboard_controller = keyboard_controller
        self.human_detector = human_detector

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
        print(f"\nMoving to x:{goal.target_pose.pose.position.x:.2f}, y:{goal.target_pose.pose.position.y:.2f}, orientation:{goal.target_pose.pose.orientation.z:.2f}")
        self.move_base_action.send_goal(goal)

        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            if self.keyboard_controller.should_stop:
                self.move_base_action.cancel_goal()
                return False

            # Check for human detection
            if self.human_detector.human_detected:
                print("Human detected! Stopping robot...")
                self.move_base_action.cancel_goal()
                while self.human_detector.human_detected and not rospy.is_shutdown():
                    rate.sleep()
                print("No humans detected. Resuming movement...")
                self.move_base_action.send_goal(goal)

            if self.keyboard_controller.paused:
                self.move_base_action.cancel_goal()
                print("Robot paused. Press 't' to resume...")
                while self.keyboard_controller.paused and not rospy.is_shutdown():
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


def main():

    # Init ROS node for move_to_goal
    rospy.init_node('move_to_goal', anonymous=True)

    # Initialize controllers
    keyboard_controller = KeyboardController()
    human_detector = HumanDetector()

    # Start the human detection
    human_detector.start_detection()

    # Start keyboard listener parallelly using thread
    keyboard_thread = threading.Thread(target=keyboard_controller.keyboard_listener)
    keyboard_thread.daemon = True
    keyboard_thread.start()

    mba = moveBaseAction(keyboard_controller, human_detector) #### WHAT IS MOVEBASEACTION

    waypoints = [
        (1.356, 0.957, 4.712),
        (1.852, -0.773, 0),
        (-0.040, -2.634, 3.14),
        (-0.041, -4.957, 1.57)
    ]

    try:
        while not rospy.is_shutdown() and not keyboard_controller.should_stop:
            for x, y, theta in waypoints:
                if keyboard_controller.should_stop:
                    break
                
                # if keyboard doesn't stop, move to the next waypoint
                success = mba.moveToPoint(x, y, theta)

                if not success:
                    print("Failed to reach waypoint, moving to next...")
                rospy.sleep(1)

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