#!/usr/bin/env python
from __future__ import print_function

import roslib
roslib.load_manifest('exercise4')
import sys
import cv2
import numpy as np
import os
import rospy

import tf

import tf2_geometry_msgs
import tf2_ros
from sensor_msgs.msg import Image
from geometry_msgs.msg import PointStamped, Vector3, Pose
from cv_bridge import CvBridge, CvBridgeError
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import ColorRGBA
from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient

class The_Ring:
    def __init__(self):
        rospy.init_node('image_converter', anonymous=True)
        # An object we use for converting images between ROS format and OpenCV format
        self.bridge = CvBridge()

        # A help variable for holding the dimensions of the image
        self.dims = (0, 0, 0)

        # Marker array object used for visualizations
        self.marker_array = MarkerArray()
        self.marker_num = 1

        # Subscribe to the image and/or depth topic
        self.image_sub = rospy.Subscriber("/camera/rgb/image_color", Image, self.image_callback)
        self.depth_sub = rospy.Subscriber("/camera/depth_registered/image_raw", Image, self.depth_callback)
	

        # Publiser for the visualization markers
        self.markers_pub = rospy.Publisher('markers', MarkerArray, queue_size=1000)

        # Object we use for transforming between coordinate frames
        self.tf_buf = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buf)
	print("between fuck 1")

    def get_pose(self,e,dist):
        # Calculate the position of the detected ellipse

        k_f = 525 # kinect focal length in pixels

        elipse_x = self.dims[1] / 2 - e[0][0]
        elipse_y = self.dims[0] / 2 - e[0][1]

        angle_to_target = np.arctan2(elipse_x,k_f)

        # Get the angles in the base_link relative coordinate system
        x,y = dist*np.cos(angle_to_target), dist*np.sin(angle_to_target)

        # Define a stamped message for transformation
        point_s = PointStamped()
        point_s.point.x = x
        point_s.point.y = y
        point_s.point.z = 0.3
        point_s.header.frame_id = "base_link"
        point_s.header.stamp = rospy.Time(0)

        # Get the point in the "map" coordinate system
        point_world = self.tf_buf.transform(point_s,"map")

        # Create a Pose object with the same position
        pose = Pose()
        pose.position.x = point_world.point.x
        pose.position.y = point_world.point.y
        pose.position.z = point_world.point.z

	koordinate = []
	#with open("/home/team_gamma/ROS/src/exercise3/src/rings.txt", "r") as the_file:
	#    for line in the_file:
	#	linija = line.strip("\n").split(";")
	#	koordinate.append((linija[0], linija[1]))

	for koor in koordinate:

	    print(koor)
	    razdaljaX = abs(float(koor[0])-pose.position.x)
	    razdaljaY = abs(float(koor[1])-pose.position.y)
	    
            if razdaljaX < 0.4 and razdaljaY < 0.4:
		return

	    

	

        # Create a marker used for visualization
        self.marker_num += 1
        marker = Marker()
        marker.header.stamp = point_world.header.stamp
        marker.header.frame_id = point_world.header.frame_id
        marker.pose = pose
        marker.type = Marker.CYLINDER
        marker.action = Marker.ADD
        marker.frame_locked = False
        marker.lifetime = rospy.Duration.from_sec(600)
        marker.id = self.marker_num
        marker.scale = Vector3(0.1, 0.1, 0.1)
        marker.color = ColorRGBA(0, 1, 0, 1)
        self.marker_array.markers.append(marker)

        self.markers_pub.publish(self.marker_array)
        print("sem poslal info za marker")

	#with open("/home/team_gamma/ROS/src/exercise3/src/rings.txt", "a") as the_file:
	#    the_file.write(str(pose.position.x) + ";" + str(pose.position.y) + "\n")
	
	circle_detected_sound()
	print("marker " + str(pose.position.x) + ";" + str(pose.position.y) + " shranjen")

#KODA!!!!!
    def image_callback(self,data):
	#def image_callback(self,data):
        print('Iam here!')

        sizeX = 640
        sizeY = 360

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
	    #cv_image = cv2.imread('Img.jpg')
        except CvBridgeError as e:
            print(e)

        # Set the dimensions of the image
        self.dims = cv_image.shape

        #cv_image = cv_image[0: sizeY / 5 * 4, 0:sizeX/5*4]
        #cv_image = cv2.resize(cv_image, (sizeX, sizeY), interpolation=cv2.INTER_CUBIC)

        # Tranform image to gayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # Do histogram equlization
        img = cv2.equalizeHist(gray)
	print('Iam here!2')
        # Binarize the image
        #ret, thresh = cv2.threshold(img, 50, 255, 0)
        thresholds = []
        # Binarize the image

        for tr in range(20, 180, 15):
            ret, thresh = cv2.threshold(img, tr, 255, 0)
            thresholds.append(thresh)
            #cv2.imshow("Image window", thresh)
            #cv2.waitKey(0)

        # Extract contours
        # Extract contours
        allContours = [[], [], [], [], [], [], [], [], [], [], [], [], [], []]
        for i, thresh in enumerate(thresholds):
            _,contours, hierarchy = cv2.findContours(thresh, 2, 2)
            for contoure in contours:
                allContours[i].append(contoure)
	print('Iam here!3')
        # Example how to draw the contours
        # cv2.drawContours(img, contours, -1, (255, 0, 0), 3)

        # Fit elipses to all extracted contours
        elpses = [[], [], [], [], [], [], [], [], [], [], [], [], [], []]
        for i, contoure in enumerate(allContours):
            for cnt in contoure:
                #     print cnt
                #     print cnt.shape
                if cnt.shape[0] >= 20:
                    ellipse = cv2.fitEllipse(cnt)
                    elpses[i].append(ellipse)


        candidates = []

        # Find two elipses with same centers
        for elps in elpses:
            # print("---")
            for n in range(len(elps)):
                # i = 0
                for m in range(n + 1, len(elps)):

                    e1 = elps[n]
                    e2 = elps[m]
                    dist = np.sqrt(((e1[0][0] - e2[0][0]) ** 2 + (e1[0][1] - e2[0][1]) ** 2))
                    pos = (((e1[0][0] + e2[0][0]) / 2), ((e1[0][1] + e2[0][1]) / 2))

                    try:
                        razmerje = e1[1][0] / e2[1][0]
                        razmerje2 = e1[1][1] / e2[1][1]
                    except:
                        break
                    #print(pos[1])
                    if dist < 5 and ((razmerje < 1.5 and razmerje > 1.1) or (razmerje < 0.9 and razmerje > 0.6)) and (
                        (razmerje2 < 1.5 and razmerje2 > 1.1) or (razmerje2 < 0.9 and razmerje2 > 0.6)) and pos[1] < sizeY/3*2:# and pos[
                        #1] > 0 and pos[1] < (sizeY / 2 / 4) * 3:
                        # i += 1
                        # if i==2:
                        #print (e1)
                        candidates.append((e1, e2, pos))
	print('Iam here!4')
        realCandidates = []
        used = []
        for n in range(len(candidates)):
            for m in range(n + 1, len(candidates)):

                e1 = candidates[n]
                e2 = candidates[m]

                if abs(e1[2][0] - e2[2][0]) < 5 and abs(e1[2][1] - e2[2][1]) < 5:
                    if n not in used and m not in used:
                        realCandidates.append(e1)

                    used.append(n)
                    used.append(m)
                    # candidates[m] = False
                    # print(n, " ", m)
                    break

	print('Iam here!4.5')        
	try:
       	    depth_img = rospy.wait_for_message('/camera/depth_registered/image_raw', Image)
        except Exception as e:
            print(e)
	print('Iam here!5')
        # Extract the depth from the depth image
        for c in realCandidates:
            #print("real")
            #print(c)
            e1 = c[0]
            e2 = c[1]

            cv2.ellipse(cv_image, e1, (0, 255, 0), 2)
            cv2.ellipse(cv_image, e2, (0, 255, 0), 2)

            size = (e1[1][0]+e1[1][1])/2
            center = (e1[0][1], e1[0][0])

            x1 = int(center[0] - size / 2)
            x2 = int(center[0] + size / 2)
            x_min = x1 if x1>0 else 0
            x_max = x2 if x2<cv_image.shape[0] else cv_image.shape[0]

            y1 = int(center[1] - size / 2)
            y2 = int(center[1] + size / 2)
            y_min = y1 if y1 > 0 else 0
            y_max = y2 if y2 < cv_image.shape[1] else cv_image.shape[1]

            depth_image = self.bridge.imgmsg_to_cv2(depth_img, "16UC1")
            #print(x_min)
            #print(x_max)
            #print(y_min)
            #print(y_max)
            
            #depth_image = depth_image[0: sizeY/5*4, 0:sizeX/5*4]
            #cv2.imshow("Image window",depth_image)
            #cv2.waitKey(0)
            #print(depth_image)
            #print(float(np.mean(depth_image[0:1, 0:1]))/1000.0)
            
            #print(float(np.mean(depth_image[x_min:x_max,y_min:y_max]))/1000.0)

            self.get_pose(e1, float(np.mean(depth_image[x_min:x_max,y_min:y_max]))/1000.0)
            
	print("boom")
        #cv2.imshow("Image window",cv_image)
        #cv2.waitKey(0)

	rospy.signal_shutdown("lol")
	sys.exit(0)
# KODA!!!!!
    def depth_callback(self,data):

        try:
            depth_image = self.bridge.imgmsg_to_cv2(data, "16UC1")
        except CvBridgeError as e:
            print(e)

        # Do the necessairy conversion so we can visuzalize it in OpenCV
        image_1 = depth_image / 65536.0 * 255
        image_1 =image_1/np.max(image_1)*255


        image_viz = np.array(image_1, dtype= np.uint8)

        #cv2.imshow("Depth window", image_viz)
        #cv2.waitKey(1)

def circle_detected_sound():
    soundhandle = SoundClient()
    rospy.sleep(1)
    soundhandle.stopAll()
    
    s3 = soundhandle.voiceSound("Marker found" ,5)
    s3.play()
    rospy.sleep(3)
    s3.stop()

def main(args):
    print("fuck")
    ring_finder = The_Ring()
    #circle_detected_sound()
    print("after fuck")
    try:
        rospy.spin()
	print("way after fuck")

    except KeyboardInterrupt:
        print("Shutting down")

    #cv2.destroyAllWindows()


if __name__ == '__main__':
    main(sys.argv)
