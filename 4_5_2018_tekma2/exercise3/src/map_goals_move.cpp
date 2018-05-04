#include "ros/ros.h"
#include <nav_msgs/GetMap.h>
#include <geometry_msgs/Quaternion.h>
#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/Twist.h>
#include <actionlib/client/simple_action_client.h>
#include <tf/transform_datatypes.h>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include <move_base_msgs/MoveBaseAction.h>

#include <std_msgs/String.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <Python.h>
#include <visualization_msgs/MarkerArray.h>

using namespace std;
using namespace cv;

bool isMapReady = false;

Mat cv_map;
float map_resolution = 0;
tf::Transform map_transform;

ros::Publisher goal_pub;
ros::Subscriber map_sub;
ros::Subscriber circle_sub;
ros::Subscriber cylinder_sub;

typedef actionlib::SimpleActionClient<move_base_msgs::MoveBaseAction> MoveBaseClient;

void circleCallback(const visualization_msgs::MarkerArray& msg_marker){
  ROS_INFO("circle callback: x:%f y:%f",msg_marker.markers[0].pose.position.x,msg_marker.markers[0].pose.position.y);
}

void cylinderCallback(const visualization_msgs::Marker& msg_marker){
  ROS_INFO("cylinder callback: x:%f y:%f",msg_marker.pose.position.x,msg_marker.pose.position.y);
  MoveBaseClient ac2("move_base", true);
  move_base_msgs::MoveBaseGoal goal2;
  goal2.target_pose.header.frame_id = "map";
  goal2.target_pose.pose.orientation.w = 1;
  goal2.target_pose.pose.position.x = msg_marker.pose.position.x;//transformed.x();
  goal2.target_pose.pose.position.y = msg_marker.pose.position.y;//-transformed.y();
  goal2.target_pose.header.stamp = ros::Time::now();
  ac2.sendGoal(goal2);
  ac2.waitForResult();
}

void location();

void mapCallback(const nav_msgs::OccupancyGridConstPtr& msg_map) {
  if (isMapReady)
    return;

  int size_x = msg_map->info.width;
  int size_y = msg_map->info.height;

  if ((size_x < 3) || (size_y < 3) ) {
    ROS_INFO("Map size is only x: %d,  y: %d . Not running map to image conversion", size_x, size_y);
    return;
  }

  // resize cv image if it doesn't have the same dimensions as the map
  if ( (cv_map.rows != size_y) && (cv_map.cols != size_x)) {
    cv_map = cv::Mat(size_y, size_x, CV_8U);
  }

  map_resolution = msg_map->info.resolution;
  tf::poseMsgToTF(msg_map->info.origin, map_transform);

  const std::vector<int8_t>& map_msg_data (msg_map->data);

  unsigned char *cv_map_data = (unsigned char*) cv_map.data;

  //We have to flip around the y axis, y for image starts at the top and y for map at the bottom
  int size_y_rev = size_y-1;

  for (int y = size_y_rev; y >= 0; --y) {

    int idx_map_y = size_x * (size_y -y);
    int idx_img_y = size_x * y;

    for (int x = 0; x < size_x; ++x) {

      int idx = idx_img_y + x;

      switch (map_msg_data[idx_map_y + x])
      {
        case -1:
        cv_map_data[idx] = 127;
        break;

        case 0:
        cv_map_data[idx] = 255;
        break;

        case 100:
        cv_map_data[idx] = 0;
        break;
      }
    }
  }
  ROS_INFO("MAP_OK");
  isMapReady = true;
}

void location() {

  //cout << "123";
  MoveBaseClient ac("move_base", true);
  /*while(!ac.waitForServer(ros::Duration(5.0)))
  {
    ROS_INFO("Waiting for move_base server");
  }*/
  //ros::Rate rate(1);
  //ros::NodeHandle nh;
  //ros::Publisher pub = nh.advertise<geometry_msgs::Twist>("cmd_vel",1000);
  //geometry_msgs::Twist msgc;
  //ros::Rate rate(1);

  float rotacijeWZ[8][2] = {
    {1.0,0.0},
    {0.924,0.383},
    {0.707,0.707},
    {0.383,0.924},
    {0.0, 1.0},
    {-0.383,0.924},
    {-0.707,0.707},
    {-0.924,0.383}
  };
  //move_base_msgs::MoveBaseGoal goal;
  /*
  for(int i=0;i<6;i++) {
    ROS_INFO("rotate start");
    //float asd = 1 - (i*0.25);

    //cout << 1 - (i*0.25);

    //msgc.angular.z = i;
    //pub.publish(msgc);
    //rate.sleep();

    cout << rotacijeWZ[i][0];
    cout << '\n';
    cout << rotacijeWZ[i][1];

    goal.target_pose.header.frame_id = "map";
    goal.target_pose.pose.orientation.w = rotacijeWZ[i][0];//1 - (i*1);
    goal.target_pose.pose.orientation.z = rotacijeWZ[i][1];
    goal.target_pose.pose.position.x = -0.3;//transformed.x();
    goal.target_pose.pose.position.y = -3.2;

    //goal.target_pose.pose.position.x = 0;//transformed.x();
    //goal.target_pose.pose.position.y = 0;
    goal.target_pose.header.stamp = ros::Time::now();
    ROS_INFO("rotate start2");
    ac.sendGoal(goal);
    ROS_INFO("rotate start3");
    ac.waitForResult();
    ROS_INFO("rotate start4");
    //rate.sleep();

    ROS_INFO("rotate");
  }*/

  //now = rospy.Time.now();
  //listener.waitForTransform('map', 'base_footprint', now, rospy.Duration(10.0))


  while(!ac.waitForServer(ros::Duration(5.0)))
  {
    ROS_INFO("Waiting for move_base server");
  }

system("roslaunch pcl_demos find_cylinder.launch");
	ROS_INFO("done search!");
        ros::spinOnce();

  float points[8][2] = {
    {-0.3, -1.1},
    {-0.3, -2},
    {-1.5, -2},
    {-1.0, -3.7},
    {-1.6, -3.8},
    {-1.6, -4.5},
    {-1.0, -5},
    {-0.2, -4.7}
  };

  for(int i = 8; i<8; i++)
  {
    int point[2];
    point[0] = points[i][0];
    point[1] = points[i][1];

    /*int v = (int)cv_map.at<unsigned char>(point[1], point[0]);

    if (v != 255) {
      ROS_WARN("Unable to move to (x: %d, y: %d), not reachable, collor = %d", point[1], point[0], v);
      return;
    }

    ROS_WARN("Moving to (x: %d, y: %d), collor = %d", point[1], point[0], v);
    //ROS_INFO("Moving to (x: %d, y: %d)", point[1], point[0]);

    tf::Point pt((float)point[1] * map_resolution, (float)point[0] * map_resolution, 0.0);
    tf::Point transformed = map_transform * pt;
  */
    move_base_msgs::MoveBaseGoal goal;

    goal.target_pose.header.frame_id = "map";
    goal.target_pose.pose.orientation.w = 1;
    goal.target_pose.pose.position.x = point[0];//transformed.x();
    goal.target_pose.pose.position.y = point[1];//-transformed.y();
    goal.target_pose.header.stamp = ros::Time::now();

    /*
    geometry_msgs::PoseStamped goal;
    goal.header.frame_id = "map";
    goal.pose.orientation.w = 1;
    goal.pose.position.x = transformed.x();
    goal.pose.position.y = -transformed.y();
    goal.header.stamp = ros::Time::now();
    goal_pub.publish(goal);

  */

    ac.sendGoal(goal);
    ac.waitForResult();
    if(ac.getState() == actionlib::SimpleClientGoalState::SUCCEEDED)
    {
      ROS_INFO("WE DID IT");
	
      for(int j=8;j<8;j++) {
        ROS_INFO("rotate start");
        //float asd = 1 - (i*0.25);

        //cout << 1 - (i*0.25);

        //msgc.angular.z = i;
        //pub.publish(msgc);
        //rate.sleep();

        cout << rotacijeWZ[j][0];
        cout << '\n';
        cout << rotacijeWZ[j][1];

        goal.target_pose.header.frame_id = "map";
        goal.target_pose.pose.orientation.w = rotacijeWZ[j][0];//1 - (i*1);
        goal.target_pose.pose.orientation.z = rotacijeWZ[j][1];
        goal.target_pose.pose.position.x = point[0];//transformed.x();
        goal.target_pose.pose.position.y = point[1];

        //goal.target_pose.pose.position.x = 0;//transformed.x();
        //goal.target_pose.pose.position.y = 0;
        goal.target_pose.header.stamp = ros::Time::now();
        //ROS_INFO("rotate start2");
        ac.sendGoal(goal);
        //ROS_INFO("rotate start3");
        ac.waitForResult();
        //ROS_INFO("rotate start4");
        //rate.sleep();

        ROS_INFO("rotated");

        ROS_INFO("searching for circles");
	
	//system("python /home/team_gamma/ROS/src/exercise3/src/RingDetect_v3_2.py");
        
	system("roslaunch pcl_demos find_cylinder.launch");
	ROS_INFO("done search!");
        ros::spinOnce();

	/*
	Py_Initialize();
	char filename[] = "/home/team_gamma/ROS/src/exercise3/src/RingDetect_v3.py";
	FILE* PythonScriptFile = fopen(filename,"r");
	if(PythonScriptFile)
	{
	PyRun_SimpleFile(PythonScriptFile, filename);
	fclose(PythonScriptFile);
	ROS_INFO("aa");
	}
	Py_Finalize();
*/
/*
	PyObject *obj = Py_BuildValue("s", "RingDetect_v3.py");
	FILE *file = _Py_fopen_obj(obj, "r+");

	if(file != NULL)
	{
		PyRun_SimpleFIle(file, "RingDetect_v3.py");
	}
	*/
	//FILE *fd = fopen("RingDetect_v3.py", "r");
	//ROS_INFO("asd");
        //PyRun_SimpleFileEx(fd, "RingDetect_v3.py", 1);
	//Py_Initialize();
	//ROS_INFO("A");
        //PyObject* PyFileObject = PyFile_FromString((char *)"RingDetect_v3.py","r");
	//ROS_INFO("B");
        //PyRun_SimpleFileEx(PyFile_AsFile(PyFileObject),"RingDetect_v3.py",1);
	//ROS_INFO("C");
	//Py_Finalize();
        ROS_INFO("done searching");
	}

      /*
      for(int i=0;i<7;i++) {
        goal.target_pose.pose.orientation.w = 0.75 - (i*0.25);
        goal.target_pose.header.stamp = ros::Time::now();
        ac.sendGoal(goal);
        ac.waitForResult();
        ROS_INFO("rotate");

        //FILE *fd = fopen("RingDetect.py", "r");
        //PyRun_SimpleFileEx(fd, "RingDetect.py", 1);
        PyObject* PyFileObject = PyFile_FromString("RingDetect_v2.py","r")
        PyRun_SimpleFileEx(PyFile_AsFile(PyFileObject),"RingDetect_v2.py",1)
        /*FILE *fd = fopen("rotate.py", "r");
        PyRun_SimpleFileEx(fd, "rotate.py", 1);
      }
      */
    }
      //pokliči python file, pa si zapomni kje so krogi če so kje
      //če najde krog naj neki reče
      //rotiraj se za 45
      //ponavlaj 8x
    else
      ROS_INFO("rip");
  }
}


int main(int argc, char** argv) {
  ROS_INFO("test1");
  ros::init(argc, argv, "map_goals_move");
  ROS_INFO("test2");
  ros::NodeHandle n;
  ros::NodeHandle n2;
  ROS_INFO("test3");
  circle_sub = n.subscribe("markers",5,&circleCallback);
  cylinder_sub = n.subscribe("detected_cylinder",1,&cylinderCallback);

  map_sub = n2.subscribe("map", 10, &mapCallback);
  ROS_INFO("test4");
  goal_pub = n.advertise<geometry_msgs::PoseStamped>("goal", 10);
  ROS_INFO("test5");
  
  //namedWindow("Map");

  //while(cv_map.empty()){}

  while(!isMapReady)
  {
      ROS_INFO("Waiting for map...");
      ros::spinOnce();
      ros::Duration(0.5).sleep();
  }



  location();

  /*while(ros::ok()) {
    ROS_INFO("loop");
    //marker_sub = n.subscribe("markers",5,&markerCallback);
    //if (!cv_map.empty()) imshow("Map", cv_map);

    //waitKey(30);

    ros::spinOnce();
  }*/
  return 0;

}
