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

import pyzbar.pyzbar as pyzbar

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

        print("marker " + str(pose.position.x) + ";" + str(pose.position.y) + " shranjen")

    def image_callback(self,data):
    #def image_callback(self,data):
        print('Iam here!')

        sizeX = 640
        sizeY = 480

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        #cv_image = cv2.imread('Img.jpg')
        except CvBridgeError as e:
            print(e)

        # Set the dimensions of the image
        self.dims = cv_image.shape
        #print(cv_image.shape)

        cv_image = cv_image[sizeY/5: sizeY/5*4, 0:sizeX/5*4]
        #cv_image = cv2.resize(cv_image, (sizeX, sizeY), interpolation=cv2.INTER_CUBIC)

        cv2.imshow("Image window", cv_image)
        cv2.waitKey(0)

        # Tranform image to gayscale
        cv_image_hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
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
            print("CIRCLE FOUND!")
            #print(c)
            e1 = c[0]
            e2 = c[1]

            if(e1[1][1]*e1[1][0]<e2[1][1]*e2[1][0]):
				temp = e1
				e1 = e2
				e2 = temp


            # size = (e1[1][0]+e1[1][1])/2
			sizex = (e1[1][0])/2
			sizey = (e1[1][1])/2
			sizex2 = (e2[1][0])/2
			sizey2 = (e2[1][1])/2
			#center = (e1[0][1], e1[0][0])
			center = (e1[0][0], e1[0][1])
			center2 = (e2[0][0], e2[0][1])

			dist = np.sqrt(((e1[0][0] - e2[0][0]) ** 2 + (e1[0][1] - e2[0][1]) ** 2))
			print("sizex: "+str(sizex))
			print("center: "+str(center))

			# elipse 1
			# x1 = center[0] - sizex / 2
			x1 = center[0] - sizex
			print("x1: "+str(x1))
			x2 = center[0] + sizex
			print("x2: "+str(x2))
			x_min = x1 if x1<x2 else x2
			x_max = x2 if x2>x1 else x1
			print("xmin: "+str(x_min))
			print("xmax: "+str(x_max))
			y1 = center[1] - sizey
			y2 = center[1] + sizey
			print("y1: "+str(y1))
			print("y2: "+str(y2))
			y_min = y1 if y1 < y2 else y2
			y_max = y2 if y2 > y1 else y1
			print("ymin: "+str(y_min))
			print("ymax: "+str(y_max))

			#elipse 2
			x1_2 = center2[0] - sizex2
			x2_2 = center2[0] + sizex2
			x_min2 = x1_2 if x1_2 < x2_2 else x2_2
			x_max2 = x2_2 if x2_2 > x1_2 else x1_2
			print("xmin2: "+str(x_min2))
			print("xmax2: "+str(x_max2))
			y1_2 = center2[1] - sizey2
			y2_2 = center2[1] + sizey2
			y_min2 = y1_2 if y1_2 < y2_2 else y2_2
			y_max2 = y2_2 if y2_2 > y1_2 else y1_2
			print("ymin2: "+str(y_min2))
			print("ymax2: "+str(y_max2))

			x_max = x_max if x_max<cv_image.shape[0] else cv_image.shape[0]
			y_max = y_max if y_max < cv_image.shape[1] else cv_image.shape[1]
			x_max2 = x_max2 if x_max2<cv_image.shape[0] else cv_image.shape[0]
			y_max2 = y_max2 if y_max2< cv_image.shape[1] else cv_image.shape[1]

			x_min = x_min if x_min>0 else 0
			y_min = y_min if y_min>0 else 0
			x_min2 = x_min2 if x_min2>0 else 0
			y_min2 = y_min2 if y_min2>0 else 0

			# ne dela ker se prva pa druga elipsa zamenjata kakdaj

			size_diffx = abs(sizex-sizex2)
			size_diffy = abs(sizey-sizey2)
			thick_x_right = (x_max2+x_max)/2
			thick_x_left = (x_min2+x_min)/2
			thick_y_bot = (y_max2+y_max)/2
			thick_y_top = (y_min2+y_min)/2


			left = [thick_x_left,center[1]]
			right = [thick_x_right,center[1]]
			top = [center[0],thick_y_top]
			bot = [center[0],thick_y_bot]
			bgr_point_left = cv_image[int(left[1]),int(left[0])]
			hsv_point_left = cv_image_hsv[int(left[1]),int(left[0])]

			bgr_point_right = cv_image[int(right[1]),int(right[0])]
			hsv_point_right = cv_image_hsv[int(right[1]),int(right[0])]

			bgr_point_top = cv_image[int(top[1]),int(top[0])]
			hsv_point_top = cv_image_hsv[int(top[1]),int(top[0])]

			bgr_point_bot = cv_image[int(bot[1]),int(bot[0])]
			hsv_point_bot = cv_image_hsv[int(bot[1]),int(bot[0])]


			# Opencv hsv to normal HSV conversion
			hsv_point_left[0] = hsv_point_left[0] * 2
			hsv_point_left[1] = (hsv_point_left[1] / 255)*100
			hsv_point_left[2] = (hsv_point_left[2] / 255)*100

			hsv_point_right[0] = hsv_point_right[0] * 2
			hsv_point_right[1] = (hsv_point_right[1] / 255)*100
			hsv_point_right[2] = (hsv_point_right[2] / 255)*100

			hsv_point_top[0] = hsv_point_top[0] * 2
			hsv_point_top[1] = (hsv_point_top[1] / 255)*100
			hsv_point_top[2] = (hsv_point_top[2] / 255)*100

			hsv_point_bot[0] = hsv_point_bot[0] * 2
			hsv_point_bot[1] = (hsv_point_bot[1] / 255)*100
			hsv_point_bot[2] = (hsv_point_bot[2] / 255)*100

			pink = (255,20,147)
			print(left[0])
			print(left[1])
			cv2.circle(cv_image, (int(left[0]),int(left[1])), 3,pink)
			cv2.circle(cv_image, (int(right[0]),int(right[1])), 3,pink)
			cv2.circle(cv_image, (int(top[0]),int(top[1])), 3,pink)
			cv2.circle(cv_image, (int(bot[0]),int(bot[1])), 3,pink)
			#points_coords = []
			#points_coords.append([bgr_point_left,hsv_point_left,[left[0],left[1]],filename,target_color])
			#points_coords.append([bgr_point_right,hsv_point_right,[right[0],right[1]],filename,target_color])
			#points_coords.append([bgr_point_top,hsv_point_top,[top[0],top[1]],filename,target_color])
			#points_coords.append([bgr_point_bot,hsv_point_bot,[bot[0],bot[1]],filename,target_color])
			points_coords_real = []
			points_coords_real.append([bgr_point_left[2],bgr_point_left[1],bgr_point_left[0],hsv_point_left[0],hsv_point_left[1],hsv_point_left[2],target_color])
			points_coords_real.append([bgr_point_right[2],bgr_point_right[1],bgr_point_right[0],hsv_point_right[0],hsv_point_right[1],hsv_point_right[2],target_color])
			points_coords_real.append([bgr_point_top[2],bgr_point_top[1],bgr_point_top[0],hsv_point_top[0],hsv_point_top[1],hsv_point_top[2],target_color])
			points_coords_real.append([bgr_point_bot[2],bgr_point_bot[1],bgr_point_bot[0],hsv_point_bot[0],hsv_point_bot[1],hsv_point_bot[2],target_color])
			#with open("results/results.csv", "a") as csvfile:
			#	pointswriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
			#	for point in points_coords:
			#		pointswriter.writerow(point)

			#with open("results/results_real.csv", "a") as csvfile:
			#	pointswriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
				#pointswriter.writerow(["R","G","B","H","S","V","barva"])
			#	for point in points_coords_real:
			#		pointswriter.writerow(point)
			cv2.ellipse(cv_image, e1, (0, 255, 0), 2)  #zunanji (elipsa)
			cv2.ellipse(cv_image, e2, (0, 255, 0), 2) #notranji (elipsa)
			for point in points_coords_real:
				color_name = predictColor(point)
				cv2.putText(cv_image, color_name, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)
			# depth_image = self.bridge.imgmsg_to_cv2(depth_img, "16UC1")
			#print(x_min)
			#print(x_max)
			#print(y_min)
			#print(y_max)

			#depth_image = depth_image[0: sizeY/5*4, 0:sizeX/5*4]
			only_ring_img = cv_image[int(y_min):int(y_max),int(x_min):int(x_max)]
			qrDetector(only_ring_img)


			cv2.imshow("Image window",only_ring_img)
			cv2.waitKey(4000)
			cv2.destroyAllWindows()
			#cv2.startWindowThread()
			cv2.imshow("Image window",cv_image)
			cv2.waitKey(4000)
			cv2.destroyAllWindows()
			#print(depth_image)
			#print(float(np.mean(depth_image[0:1, 0:1]))/1000.0)

			#print(float(np.mean(depth_image[x_min:x_max,y_min:y_max]))/1000.0)

			#self.get_pose(e1, float(np.mean(depth_image[x_min:x_max,y_min:y_max]))/1000.0)

			print("boom")

            #cv2.imshow("Image window",cv_image)
            #cv2.waitKey(0)

            #rospy.signal_shutdown("lol")
            #sys.exit(0)
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
def predictColor(point_val):
	#[bgr_point_top[2],bgr_point_top[1],bgr_point_top[0],
	#hsv_point_top[0],hsv_point_top[1],hsv_point_top[2],]
	# stuff
	ret_text = ""
	if(point_val[0]<57):
		if(point_val[3]>=181.5):
			ret_text="blue"
		else:
			ret_text="green"
	else:
		if(point_val[1]<75.5):
			ret_text="red"
		else:
			ret_text="yellow"
	return ret_text

def qrDetector(cv_image):
	###########################################
    #### This is relevant for exercise 8
    ###########################################
    print('Ring detected! (hopefully)')

    # Find a QR code in the image
    decodedObjects = pyzbar.decode(cv_image)

    #print(decodedObjects)

    if len(decodedObjects) == 1:
        dObject = decodedObjects[0]
        print("Found 1 QR code in the image!")
        print("Data: ", dObject.data,'\n')

        # Visualize the detected QR code in the image
        points  = dObject.polygon
        if len(points) > 4 :
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else :
            hull = points;

        ## Number of points in the convex hull
        n = len(hull)

        ## Draw the convext hull
        for j in range(0,n):
            cv2.line(cv_image, hull[j], hull[ (j+1) % n], (0,255,0), 2)

        # cv2.imshow('Warped image',cv_image)
        # cv2.waitKey(1)
        cv2.imwrite( "qr/output_qr.bmp", cv_image );

    elif len(decodedObjects)==0:
        print("No QR code in the image")
    else:
        print("Found more than 1 QR code")

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
