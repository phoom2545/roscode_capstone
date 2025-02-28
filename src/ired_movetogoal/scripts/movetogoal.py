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

# This class will handle what the keyboard does to the robot
class KeyboardController:
    def __init__(self):
        self.should_stop = False # This will exit the program (it will run to latest position and stop)
        self.paused = False # This will just pause temporary

    # This function will "get a single key pressed without pressing Enter"
    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    # This function will do action after getting the key to 1.pause or 2.exit the program
    def keyboard_listener(self):

        # This will run forever parallely if the program is not exited!
        while not rospy.is_shutdown() and not self.should_stop:
            key = self.get_key() 
            if key == 'q':
                print("\nPausing robot movement...")
                self.paused = True # Change the paused flag to "True"
            elif key == 't':
                print("\nResuming robot movement...")
                self.paused = False
            elif key == 'x':
                print("\nExiting program...")
                self.should_stop = True # Change the should_stop flag to True to exit the program
                rospy.signal_shutdown("User requested exit")
                break 
                # Exit the while loop and shutdown


# This class will handle the goal of the robot, how it move, oriented, and stop
class moveBaseAction():
    def __init__(self, keyboard_controller):
        self.move_base_action = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
        self.move_base_action.wait_for_server(rospy.Duration(5))
        self.keyboard_controller = keyboard_controller

        rospy.wait_for_service('/move_base/clear_costmaps')
        self.clear_costmap_service = rospy.ServiceProxy('/move_base/clear_costmaps', Empty)


    # Create a goal from the input ( x, y, theta(in radian) ) to the goal robot understands
    def createGoal(self, x, y, theta):
        goal = MoveBaseGoal()

        # Set the target pose of the robot to be from the map, current time(stamp)
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()

        # Convert the target orientation of the robot from theta(in radian) to quaternion form using transformations
        quat = tf.transformations.quaternion_from_euler(0, 0, theta)

        # Then finally sum up the pose of the target goal (position and orientation)
        goal.target_pose.pose = Pose( 
            Point(x, y, 0.000),
            Quaternion(quat[0], quat[1], quat[2], quat[3])
        )
        return goal # Return everything related to target.pose from MoveBaseGoal() class


    # This function will get the goal coordinates and orientation from the main code and execute the robot to move based on goal.
    def moveToPoint(self, x, y, theta):
        target_point = self.createGoal(x, y, theta) # send the coordinates and orientation to createGoal function
        return self.moveToGoal(target_point) # Move the robot to the goal(target_point)


    # This function will actually move, pause, cancel the robot based on the goal given
    def moveToGoal(self, goal):
        print(f"\nMoving to x:{goal.target_pose.pose.position.x:.2f}, y:{goal.target_pose.pose.position.y:.2f}, orientation:{goal.target_pose.pose.orientation.z:.2f}")
        self.move_base_action.send_goal(goal) # goal in this case is the target_point from moveToPoint

        # Check goal status while considering pause state
        rate = rospy.Rate(10)  # 10Hz

        # While the program is still running, check the flag from the keyboard
        while not rospy.is_shutdown():

            # If flag should_stop is true : cancel the goal --> stop the robot
            if self.keyboard_controller.should_stop:
                self.move_base_action.cancel_goal() # Cancel goal wil move_base_action
                return False # Return and exit from class as "False"

            if self.keyboard_controller.paused:
                self.move_base_action.cancel_goal() # stop the robot 
                print("Robot paused. Press 't' to resume...")

                # Stay in the while loop forever until the user press 't' --> not 'paused' --> continue the robot

                while self.keyboard_controller.paused and not rospy.is_shutdown():
                    rate.sleep() # stop checking the keyboard for a rate of 10HZ
                if not self.keyboard_controller.paused:
                    print("Resuming movement...")
                    self.move_base_action.send_goal(goal) # the robot continue moving to the same goal


            # Check the status of the robot to the goal if it reached or failed!
            state = self.move_base_action.get_state()
            if state == GoalStatus.SUCCEEDED:
                print("Goal reached successfully!")
                self.clear_costmap() # Clear costmap everytime it reaches each goal
                return True # Return and exit from class as "True"
            
            # If the status is not in either of these --> 
            elif state in [GoalStatus.ABORTED, GoalStatus.REJECTED, GoalStatus.PREEMPTED]:
                print("Failed to reach goal!")
                return False # Return and exit from class as "False"

            rate.sleep()


    # This function will call the service to clear costmaps --> make it the most realtime costmap
    def clear_costmap(self):
        try:
            self.clear_costmap_service() # call the service
            print("Costmap Cleared!")
        # except it has an error (e)
        except rospy.ServiceException as e:
            print("Failed to clear costmap:", e)


# MAIN CODE

def main():

    # Create a node name "move_to_goal" that will be on rosnode
    rospy.init_node('move_to_goal', anonymous=True)

    # Initialize keyboard controller and start keyboard listener thread

    keyboard_controller = KeyboardController()

    # Create parallel function named "keyboard_listener" from class keyboard_controller
    keyboard_thread = threading.Thread(target=keyboard_controller.keyboard_listener)
    keyboard_thread.daemon = True # What is daemon???
    keyboard_thread.start()

    mba = moveBaseAction(keyboard_controller) # Let moveBaseAction class access to keyboard_controller class

    # List of waypoints
    waypoints = [
        (1.356, 0.957, 4.712),
        (1.852, -0.773, 0),
        (-0.040, -2.634, 3.14),
        (-0.041, -4.957, 1.57)
    ]

    # Main loop of code where it use the input waypoints and send to associated class and functions

    try:

        # If the code is still running and flag should_stop is "False"
        while not rospy.is_shutdown() and not keyboard_controller.should_stop:
            # Loop each waypoints from the array "waypoints"
            for x, y, theta in waypoints:

                # If the flag should_stop is True --> it will move the next planned goal and stop or stop if it already reaches the goal
                if keyboard_controller.should_stop:
                    break

                # Send the waypoint to the function moveToPoint and wait for its respond
                # If it 1. reached the goal --> True   2. Flag should_stop is True --> False   
                # 3. Flag paused is True --> nothing sent but will stick in the while loop until press 't'

                success = mba.moveToPoint(x, y, theta)
                if not success:
                    print("Failed to reach waypoint, moving to next...")
                rospy.sleep(1)

    # Interruption from ROS
    except rospy.ROSInterruptException:
        pass

    # In the end it should: 1. change Flag should_stop to True 2.Set the timeout for the thread
    finally:
        keyboard_controller.should_stop = True
        keyboard_thread.join(timeout=1.0)

if __name__ == '__main__':
    main()