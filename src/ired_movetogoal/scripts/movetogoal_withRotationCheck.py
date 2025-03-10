#!/usr/bin/python3
"""
http://wiki.ros.org/move_base
http://wiki.ros.org/actionlib
"""
import rospy
import tf.transformations
import time
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal, MoveBaseActionGoal, MoveBaseActionResult
from geometry_msgs.msg import Twist, Pose, Point, PoseStamped, PoseWithCovarianceStamped, Quaternion
from actionlib_msgs.msg import GoalStatusArray, GoalStatus
import actionlib
from std_srvs.srv import Empty # import the service type for clearing costmaps


# Getting the Robot's Current Position and Orientation

def pose_callback(pose_with_covariance):
    # print(pose_with_covariance)
    pose = pose_with_covariance.pose.pose
    print("amcl_pose = {x: %f, y:%f, orientation.z:%f" % (pose.position.x, pose.position.y, pose.orientation.z))


def move_base_status_callback(status):
    pass


def move_base_result_callback(result):
    pass


class moveBaseAction():
    def __init__(self):
        self.move_base_action = actionlib.SimpleActionClient('/move_base', MoveBaseAction)
        self.move_base_action.wait_for_server(rospy.Duration(5))
        
        # Initialize the clear costmap service
        rospy.wait_for_service('/move_base/clear_costmaps')
        self.clear_costmap_service = rospy.ServiceProxy('/move_base/clear_costmaps',Empty)

    def createGoal(self, x, y, theta):
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()

        # Convert theta to quaternion
        quat = tf.transformations.quaternion_from_euler(0, 0, theta)

        # Print expected vs actual orientation for debugging
        print(f"Requested theta: {theta}")
        print(f"Quaternion values: x:{quat[0]}, y:{quat[1]}, z:{quat[2]}, w:{quat[3]}")

        goal.target_pose.pose = Pose(
            Point(x, y, 0.000),
            Quaternion(quat[0], quat[1], quat[2], quat[3])
        )
        return goal

    def moveToPoint(self, x, y, theta):
        target_point = self.createGoal(x, y, theta)
        self.moveToGoal(target_point)

    def moveToGoal(self, goal):
        self.move_base_action.send_goal(goal) # start moving to the goal
        success = self.move_base_action.wait_for_result() # check for the result of the action
        state = self.move_base_action.get_state()
        print ("Move to %f, %f, %f ->" % (
            goal.target_pose.pose.position.x,
            goal.target_pose.pose.position.y,
            goal.target_pose.pose.orientation.z
        ))
        if success and state == GoalStatus.SUCCEEDED:
            print(" Complete")
            self.clear_costmap() # call the function to clear the costmap
            return True
        else:
            print(" Fail")
            self.move_base_action.cancel_goal() # cancel the operation to move to the goal
            return False
            
    def clear_costmap(self):
    	try:
    		self.clear_costmap_service() # Call the service to clear costmaps
    		print("Costmap Cleared!!")
    	except rospy.ServiceException as e: 
    		# e is the error message that is the exception from the service!!
    		print("Failed to clear costmap because:",e)


# Main program
def main():
    rospy.init_node('move_to_goal', anonymous=True)
    publisher_goal = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=1)
    rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, pose_callback)
    rospy.Subscriber('/move_base/status', GoalStatusArray, move_base_status_callback)
    rospy.Subscriber('/move_base/result', MoveBaseActionResult, move_base_result_callback)

    # TODO
    mba = moveBaseAction()
    while not rospy.is_shutdown():
	    mba.moveToPoint(1.356, 0.957, 4.712)
	    rospy.sleep(1)
	    mba.moveToPoint(1.852, -0.773, 0)
	    rospy.sleep(1)
	    mba.moveToPoint(-0.040, -2.634, 3.14)
	    rospy.sleep(1)
	    mba.moveToPoint(-0.041, -4.957, 1.57)
	    rospy.sleep(1)

if __name__ == '__main__':

    try:
        main()
    except rospy.ROSInterruptException:
        pass
