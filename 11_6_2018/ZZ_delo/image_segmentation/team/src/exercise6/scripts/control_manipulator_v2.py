#!/usr/bin/env python

import roslib
#roslib.load_manifest('exercise6')
import rospy

from std_msgs.msg import Int8
from openservorobot.msg import MoveJoint, ManipulatorStateM, ManipulatorDescriptionM, JointStateM, JointDescriptionM

class RobotArm:
	def __init__(self):
		rospy.init_node('robot_arm')

		# A publisher for setting different joint angles of the robot arm
		self.pub_joint = rospy.Publisher("openservorobot/move_joint_to", MoveJoint, queue_size=1000)
		
		# A subscriber for the current state of the robot
		self.sub_state = rospy.Subscriber("openservorobot/manipulator_state", ManipulatorStateM, self.state_callback)
		
		# A subscriber for the current state of the robot
		#self.sub_desc = rospy.Subscriber("openservorobot/manipulator_description", ManipulatorDescriptionM, self.desc_callback)

		# A subscriber for the wanted position of the robot
		self.sub_command = rospy.Subscriber("set_manipulator_position", Int8, self.position_callback)

		# A help flag which tells us whether the manipulator needs movement
		self.update_position = False

		# A variable to hold the last configuration command
		self.position_id = None
		
		# A list of lists for robot joint configurations
		'''
		self.positions=[
			[-1, 3, -3, -1, 0, 0],
			[-2, 3, -3, -1, 0, 0],
			[-2, 1.45, -1.6, -1.3, 0, 0],
			[-2, 1.45, -1.6, -1.3, 0, 3],
			[-2, 2.5, -1.6, -1.3, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 0],
			[-1.18, 3, -1.6, -1, 0, 0],
			[-1.18, 1.45, -1.6, -1.3, 0, 0],
			[-1.18, 1.45, -1.6, -1.3, 0, 3],
			[-1.18, 2.5, -1.6, -1.3, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 0],
			[-0.5, 3, -1.6, -1.3, 0, 0],
			[-0.8, 1.45, -1.6, -1.3, 0, 0],
			[-0.8, 1.45, -1.6, -1.3, 0, 3],
			[-0.8, 2.5, -1.6, -1.3, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 0],
			[-1, 3, -3, -1, 0, 0]
		]
		'''
		
		'''
		self.positions=[
			[-1, 3, -3, -1, 0, 0],
			[-1.6, 3, -3, -1, 0, 0],
			[-1.6, 1.45, -1.6, -1.3, 0, 0],
			[-1.6, 1.45, -1.6, -1.3, 0, 3],
			[-1.6, 2.5, -1.6, -1.3, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 0],
			[-1.2, 3, -1.6, -1, 0, 0],
			[-1.2, 1.45, -1.6, -1.3, 0, 0],
			[-1.2, 1.45, -1.6, -1.3, 0, 3],
			[-1.2, 2.5, -1.6, -1.3, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 0],
			[-0.1, 3, -1.6, -1.3, 0, 0],
			[-0.78, 1.45, -1.6, -1.3, 0, 0],
			[-0.78, 1.45, -1.6, -1.3, 0, 3],
			[-0.78, 2.5, -1.6, -1.3, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 0],
			[-0.6, 3, -3, -1, 0, 0]
		]
		'''

		self.positions=[
			[-1, 3, -3, -1, 0, 0],
			[-1.6, 3, -3, -1, 0, 0],
			[-1.6, 1.45, -1.6, -1.3, 0, 0],
			[-1.6, 1.45, -1.6, -1.3, 0, 3],
			[-1.6, 2.5, -1.6, -1.3, 0, 3],
			[-0.1, 0.0, 0, -1, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 0],
			[-1.2, 3, -1.6, -1, 0, 0],
			[-1.2, 1.45, -1.6, -1.3, 0, 0],
			[-1.2, 1.45, -1.6, -1.3, 0, 3],
			[-1.2, 2.5, -1.6, -1.3, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 0],
			[-0.1, 3, -1.6, -1.3, 0, 0],
			[-0.78, 1.45, -1.6, -1.3, 0, 0],
			[-0.78, 1.45, -1.6, -1.3, 0, 3],
			[-0.78, 2.5, -1.6, -1.3, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 3],
			[-0.1, 0.5, 0, -1, 0, 0],
			[-0.6, 3, -3, -1, 0, 0]
		]

		'''
		self.positions = [[-1.256816883442209, 3.17000007629, -2.50999999046, -1.001786809114877, 0.5800000043219184, -0.2502817026040467], [-1.94000005722, 3.17000007629, -2.50999999046, -1.001786809114877, 0.5800000043219184, -0.2502817026040467], [-1.94000005722, 1.7015655685059192, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, -0.2502817026040467], [-1.94000005722, 1.7015655685059192, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, 0.9900000095369998], [-1.94000005722, 2.8522045812448464, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, 0.9900000095369998], [-0.7312913458769408, 0.6605112236468897, 0.025964411287908273, -1.001786809114877, 0.5800000043219184, 0.9900000095369998], [-0.7312913458769408, 0.6605112236468897, 0.025964411287908273, -1.001786809114877, 0.5800000043219184, -0.2502817026040467], [-1.4460060769657055, 3.17000007629, -1.6167655465251076, -1.001786809114877, 0.5800000043219184, -0.2502817026040467], [-1.4460060769657055, 1.7015655685059192, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, -0.2502817026040467], [-1.4460060769657055, 1.7015655685059192, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, 0.9900000095369998], [-1.4460060769657055, 2.8522045812448464, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, 0.9900000095369998], [-0.7312913458769408, 0.6605112236468897, 0.025964411287908273, -1.001786809114877, 0.5800000043219184, 0.9900000095369998], [-0.7312913458769408, 0.6605112236468897, 0.025964411287908273, -1.001786809114877, 0.5800000043219184, -0.2502817026040467], [-0.7312913458769408, 3.17000007629, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, -0.2502817026040467], [-1.0466066684161017, 1.7015655685059192, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, -0.2502817026040467], [-1.0466066684161017, 1.7015655685059192, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, 0.9900000095369998], [-1.0466066684161017, 2.8522045812448464, -1.6167655465251076, -1.315893389691937, 0.5800000043219184, 0.9900000095369998], [-0.7312913458769408, 0.6605112236468897, 0.025964411287908273, -1.001786809114877, 0.5800000043219184, 0.9900000095369998], [-0.7312913458769408, 0.6605112236468897, 0.025964411287908273, -1.001786809114877, 0.5800000043219184, -0.2502817026040467], [-1.256816883442209, 3.17000007629, -2.50999999046, -1.001786809114877, 0.5800000043219184, -0.2502817026040467]]
'''

		

	def state_callback(self, data):
		if self.update_position == True:
			for n,joint in enumerate(data.joints):
				print "Joint", n, "is in position", joint.position, ", goal is", joint.goal
		#print data
		
	def desc_callback(self, data):
		for n,joint in enumerate(data.joints):
			print "For joint", n, "min pos is", joint.dh_min, ", max pos is", joint.dh_max
		#print data
		
	def get_desc(self):
		try:
			desc = rospy.wait_for_message("openservorobot/manipulator_description", ManipulatorDescriptionM)
		except e:
			print e
			
		for n,joint in enumerate(desc.joints):
			print "For joint", n, "min pos is", joint.dh_min, ", max pos is", joint.dh_max
		#print data

	def position_callback(self, data):
		print "Got command to set robot position:", data.data
		self.position_id = data.data
		self.update_position = True
		
	def move_arm(self):
		# This function moves all the robot joints

		positions = self.positions[self.position_id]
		
		for n in range(len(positions)):
			self.move_joint(n, positions[n], 1)
		
		print "Movement commands sent!"
		self.update_position=False

	def move_joint(self, joint_id, angle, speed):
		""" joint_id is a number from 0 to 5
			angle is the angle expressed in radians
			speed is the wanted movement speed"""
		msg = MoveJoint()
		msg.joint = joint_id
		msg.position = angle
		msg.speed = speed

		self.pub_joint.publish(msg)

if __name__=="__main__":
	arm_mover = RobotArm()

	r = rospy.Rate(2)
	arm_mover.get_desc()
	
	while not rospy.is_shutdown():
		
		if arm_mover.update_position:
			arm_mover.move_arm()

		r.sleep()
