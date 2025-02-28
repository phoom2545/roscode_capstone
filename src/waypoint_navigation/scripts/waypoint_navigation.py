#!/usr/bin/env python3

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import PoseStamped
import time

# Define your waypoints
waypoints = [
	{"x": -0.884, "y":0.453, "yaw":-0.000204},
	{"x": 2.56, "y":-0.795, "yaw":-0.00155},
	{"x": 5.13, "y":0.0984, "yaw":0.0887}
	]
	
print("Waypoint Started")
def send_goal(x,y,yaw):
	print("OLA ronaldo")
	print("Sending goal:", x, y, yaw)
	goal = MoveBaseGoal()
	goal.target_pose.header.frame_id = "map"
	goal.target_pose_header.stamp = rospy.Time.now()

	
	goal.target_pose.pose.position.x = x
	goal.target_pose.pose.position.y = y
	goal.target_pose.pose.orientation.w = 1.0   #Simplified orientation (modify for accurate yaw)

	rospy.loginfo(f"Sending goal: x={x}, y={y}, yaw={yaw}")
	client.send_goal(goal)
	client.wait_for_result()

	if __name__ == "__main__":
		rospy.init_ode("waypoint_navigation")
		client = actionlib.SimpleActionClient("move_base",MoveBaseAction)

		rospy.loginfo("Waiting for move_base action server...")
		client.wait_for_server()
		rospy.loginfo("Connected to move_base!")

		# Loop through waypoints
		for wp in waypoints:
			print("Calling send_goal now...")
			send_goal(2.0, 2.0, 0.0)  # Example coordinates
			send_goal(wp["x"],wp["y"],wp["yaw"])
			rospy.loginfo("Reached goal,waiting before next...")
			time.sleep(2) # Small delay before moving to the nextpoint

		rospy.loginfo("Finished all waypoints!!")
