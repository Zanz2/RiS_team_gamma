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
#include <std_msgs/UInt8.h>
#include <std_msgs/Int8.h>
#include <time.h>
#include <Python.h>
#include <visualization_msgs/MarkerArray.h>

#include <visualization_msgs/Marker.h>

#include <math.h>

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
ros::Publisher arm_publisher;
ros::Publisher pubm;

void CoinPicker(int position_index);
void ArmPositions(int position_index);
void PrintAllMarkers();

float cylinder_marker_array_x [10]={-666,-666,-666,-666,-666,-666,-666,-666,-666,-666};
float cylinder_marker_array_y [10]={-666,-666,-666,-666,-666,-666,-666,-666,-666,-666};

float circle_marker_array_x [10]={-666,-666,-666,-666,-666,-666,-666,-666,-666,-666};
float circle_marker_array_y [10]={-666,-666,-666,-666,-666,-666,-666,-666,-666,-666};

float cur_pos_x = 0;
float cur_pos_y = 0;

int cur_cilin = 0;

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
int currRotation = 0;


int numberCounter = 0;
float redDataNum[2][2];
float redResultNum = 0;

float greenResultQr = 0;

float blueDataGraph_m = 0;
float blueDataGraph_b = 0;
float blueDataStart[2];
float blueResultGraph = 0;

int circleCounter = 5;
int cylinderCounter = 3;


float izracunajVrednost(float x1, float y1, float x2, float y2)
{
	return y1 + ((y2-y1)/(x2-x1))*(7-x1);
}

float izracunajVrednostGraph(float x, float y, float m, float b)	//NI ŠE OK
{
	return m*7 + b;
}


void PrintAllMarkers(){

  visualization_msgs::Marker marker;
  ros::NodeHandle nh;
  pubm = nh.advertise<visualization_msgs::Marker>("detected_cylinder",1);


  for(int i = 0;i<10;i++){
    if(cylinder_marker_array_x[i]==-666){
      break;
    }
    marker.header.frame_id = "map";
    marker.header.stamp = ros::Time::now();

    marker.ns = "cylinder";
    marker.id = 0;

    marker.type = visualization_msgs::Marker::CYLINDER;
    marker.action = visualization_msgs::Marker::ADD;

    marker.pose.position.x = cylinder_marker_array_x[i];
    marker.pose.position.y = cylinder_marker_array_y[i];
    marker.pose.position.z = 0;
    marker.pose.orientation.x = 0.0;
    marker.pose.orientation.y = 0.0;
    marker.pose.orientation.z = 0.0;
    marker.pose.orientation.w = 1.0;

    marker.scale.x = 0.1;
    marker.scale.y = 0.1;
    marker.scale.z = 0.1;

    marker.color.r=0.0f;
    marker.color.g=1.0f;
    marker.color.b=0.0f;
    marker.color.a=1.0f;

    marker.lifetime = ros::Duration();

    pubm.publish (marker);
  }
}


typedef actionlib::SimpleActionClient<move_base_msgs::MoveBaseAction> MoveBaseClient;

void cylinderAddToArray(float x_point,float y_point){
  for(int i=0;i<10;i++){
    if(cylinder_marker_array_x[i] == -666){
      if(cylinder_marker_array_y[i] == -666){
        cylinder_marker_array_x[i] = x_point;
        cylinder_marker_array_y[i] = y_point;
      }
    }
  }
}
int cylinderMarkerCount(){
  for(int i=0;i<10;i++){
    if(cylinder_marker_array_x[i] == -666){
      return i;
    }
  }
}
bool cylinderMarkerExists(float x_point,float y_point){
  float deviation = 0.5; // can deviate for 5 coordinates or whatever unit

  for(int i=0;i<10;i++){
    if(x_point >= cylinder_marker_array_x[i]-deviation && x_point <= cylinder_marker_array_x[i]+deviation){
      if(y_point >= cylinder_marker_array_y[i]-deviation && y_point <= cylinder_marker_array_y[i]+deviation){
        return true;
      }
    }
    if(cylinder_marker_array_x[i] == -666){
      if(cylinder_marker_array_y[i] == -666){
        return false;
      }
    }
  }
  return false;
}
void circleAddToArray(float x_point,float y_point){
  for(int i=0;i<10;i++){
    if(circle_marker_array_x[i] == -666){
      if(circle_marker_array_y[i] == -666){
        circle_marker_array_x[i] = x_point;
        circle_marker_array_y[i] = y_point;
      }
    }
  }
}
int circleMarkerCount(){
  for(int i=0;i<10;i++){
    if(circle_marker_array_x[i] == -666){
      return i;
    }
  }
}
bool circleMarkerExists(float x_point,float y_point){
  float deviation = 5; // can deviate for 5 coordinates or whatever unit

  for(int i=0;i<10;i++){
    if(x_point >= circle_marker_array_x[i]-deviation && x_point <= circle_marker_array_x[i]+deviation){
      if(y_point >= circle_marker_array_y[i]-deviation && y_point <= circle_marker_array_y[i]+deviation){
        return true;
      }
    }
    if(circle_marker_array_x[i] == -666){
      if(circle_marker_array_y[i] == -666){
        return false;
      }
    }
  }
  return false;
}

void circleCallback(const visualization_msgs::MarkerArray& msg_marker){
  ROS_INFO("circle callback: x:%f y:%f",msg_marker.markers[0].pose.position.x,msg_marker.markers[0].pose.position.y);
  if(circleMarkerExists(msg_marker.markers[0].pose.position.x,msg_marker.markers[0].pose.position.y)){
    return;
  }
  circleAddToArray(msg_marker.markers[0].pose.position.x,msg_marker.markers[0].pose.position.y);
  circleCounter++;

  system("python /home/team_gamma/ROS/src/exercise3/src/cylinder_found.py");


  float move_to_x = 0;
  float move_to_y = 0;
  
  float razdalja = 0.4;
  
  float distance_x = msg_marker.markers[0].pose.position.x - cur_pos_x;
  float distance_y = msg_marker.markers[0].pose.position.y - cur_pos_y;

  float leng = sqrt(pow(distance_x, 2) + pow(distance_y, 2));
  
  float angle = atan(abs(distance_y) / abs(distance_x));
  
  move_to_x = cos(angle) * (leng-razdalja);
  move_to_y = sin(angle) * (leng-razdalja);
  
  if(distance_x < 0)
	move_to_x *= -1;
	
  if(distance_y < 0)
	move_to_y *= -1;
  
  move_to_x += cur_pos_x;
  move_to_y += cur_pos_y;


  MoveBaseClient ac("move_base", true);
  move_base_msgs::MoveBaseGoal goal;
  goal.target_pose.header.frame_id = "map";

  goal.target_pose.pose.orientation.w = rotacijeWZ[(currRotation)][0];
  goal.target_pose.pose.orientation.z = rotacijeWZ[(currRotation)][1];
  goal.target_pose.pose.position.x = move_to_x;
  goal.target_pose.pose.position.y = move_to_y;
  goal.target_pose.header.stamp = ros::Time::now();
  ac.sendGoal(goal);
  ac.waitForResult();

  if(ac.getState() == actionlib::SimpleClientGoalState::SUCCEEDED)
  {
    ROS_INFO("Circle succesfully approached!");

    //GET COLLOR

    int color = 1; //1-red, 2-green, 3-blue

    //GET DATA FROM IMG

    switch(color)
    {
	case 1:	//stevilke
	{
		//GET NUBERS

		redDataNum[numberCounter][0] = 1;
		redDataNum[numberCounter][1] = 1;
		numberCounter++;

		break;
	}


	case 2:	//qr koda
	{
		//GET QR CODE 

		float x1 = 0.1;
		float y1 = 0.8;
				
		float x2 = 2.2;
		float y2 = 2.5;

		//izracunaj vrednost za 7. dan

		greenResultQr = izracunajVrednost(x1, y1, x2, y2);
		
		break;
	}

		
	case 3:	//
	{	
		//js bi najprej probo dobit številke, potem pa če faila je v krogu verjetno graf
		
		//GET NUMBER
		blueDataStart[0] = 1;
		blueDataStart[1] = 1;

		//GET GRAPH
		blueDataGraph_m = 1;
		blueDataGraph_b = 1;
	}
    }

  }
}

void cylinderCallback(const visualization_msgs::Marker& msg_marker){
  ROS_INFO("cylinder callback: x:%f y:%f",msg_marker.pose.position.x,msg_marker.pose.position.y);
  if(cylinderMarkerExists(msg_marker.pose.position.x,msg_marker.pose.position.y)){
    return;
  }
  cylinderAddToArray(msg_marker.pose.position.x,msg_marker.pose.position.y);
  cylinderCounter++;

  PrintAllMarkers();
 /*
  float move_to_x = 0;
  float move_to_y = 0;
  
  float razdalja = 0.2;
  
  float distance_x = msg_marker.pose.position.x - cur_pos_x;
  float distance_y = msg_marker.pose.position.y - cur_pos_y;

  float leng = sqrt(pow(distance_x, 2) + pow(distance_y, 2));
  
  float angle = atan(abs(distance_y) / abs(distance_x));
  
  move_to_x = cos(angle) * (leng-razdalja);
  move_to_y = sin(angle) * (leng-razdalja);
  
  if(distance_x < 0)
	move_to_x *= -1;
	
  if(distance_y < 0)
	move_to_y *= -1;
  
  move_to_x += cur_pos_x;
  move_to_y += cur_pos_y;  
  
  ROS_INFO("marker x:%f y:%f",msg_marker.pose.position.x, msg_marker.pose.position.y);
  ROS_INFO("cur x:%f y:%f",cur_pos_x, cur_pos_y);
  ROS_INFO("dist x:%f y:%f",distance_x, distance_y);
  ROS_INFO("len:%f ang:%f",leng, angle);
  ROS_INFO("move to: x:%f y:%f",move_to_x, move_to_y);
	

  system("python /home/team_gamma/ROS/src/exercise3/src/cylinder_found.py");
  MoveBaseClient ac("move_base", true);
  move_base_msgs::MoveBaseGoal goal;
  goal.target_pose.header.frame_id = "map";
  goal.target_pose.pose.orientation.w = 1;

  goal.target_pose.pose.orientation.w = rotacijeWZ[(currRotation+2)%8][0];//1 - (i*1);
  goal.target_pose.pose.orientation.z = rotacijeWZ[(currRotation+2)%8][1];
  goal.target_pose.pose.position.x = move_to_x; //msg_marker.pose.position.x;//transformed.x();
  goal.target_pose.pose.position.y = move_to_y;  //msg_marker.pose.position.y;//-transformed.y();
  goal.target_pose.header.stamp = ros::Time::now();

  ROS_INFO("move to: x:%f y:%f",move_to_x, move_to_y);
  ac.sendGoal(goal);
  ac.waitForResult();
  
  if(ac.getState() == actionlib::SimpleClientGoalState::SUCCEEDED)
  {
    ROS_INFO("Coin in");
    //CoinPicker(cylinderMarkerCount());
      CoinPicker(cur_cilin);
      cur_cilin += 1;
  }
*/
}
void CoinPicker(int position_index){
  int i;
  ROS_INFO("Coin in: %d", position_index);
  switch(position_index){
    case 0:
      ArmPositions(0);
      for(i = 0;i<7;i++){
        ArmPositions(i);
      }
      ArmPositions(13);
      ArmPositions(0);
    break;

    case 1:
      ArmPositions(0);
      for(i = 7;i<14;i++){
        ArmPositions(i);
      }
      ArmPositions(13);
      ArmPositions(0);
    break;

    case 2:
      ArmPositions(0);
      for(i = 14;i<19;i++){
        ArmPositions(i);
      }
      ArmPositions(13);
      ArmPositions(0);
    break;

    case 100:
      for(i = 0;i<3;i++){
        CoinPicker(i);
      }
    break;
  }

}
void ArmPositions(int position_index){
  std_msgs::Int8 msg;
  msg.data = position_index;
  ROS_INFO("info, initiating arm movement %d",msg.data);
  ros::NodeHandle n2;
  arm_publisher = n2.advertise<std_msgs::Int8>("set_manipulator_position", 10);
  arm_publisher.publish(msg);
  ros::Duration(1).sleep();
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
/*
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
*/
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

//system("roslaunch pcl_demos find_cylinder.launch");
//	ROS_INFO("done search!");
//        ros::spinOnce();

  /*float points[8][2] = {
    {-0.3, -1.1},
    {-0.3, -2},
    {-1.5, -2},
    {-1.0, -3.7},
    {-1.6, -3.8},
    {-1.6, -4.5},
    {-1.0, -5},
    {-0.2, -4.7}
  };*/

  float points[7][2] = {
    {0.0, 1.1},
    {0.5, 1.5},
    {0.7, 2.5},
    {1.0, 3.4},
    {1.6, 4.1},
    {-0.25, 3.5},
    {0.0, 2.6}
  };

  for(int i = 0; i<7; i++)
  {
    float point[2];
    point[0] = points[i][0];
    point[1] = points[i][1];

    cur_pos_x = point[0];
    cur_pos_y = point[1];

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

      for(int j=0;j<8;j++) {
        ROS_INFO("rotate start");

	currRotation = j;
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

	if(circleCounter > 0)
	{
		ROS_INFO("searching for circles");
		system("python /home/team_gamma/ROS/src/exercise3/src/RingDetect_v3_2.py");
	}
	
	if(cylinderCounter > 0)
	{
		ROS_INFO("searching for cylinders");
		system("roslaunch pcl_demos find_cylinder.launch");
	}

	if(circleCounter == 0 && cylinderCounter == 0)
	{
		redResultNum = izracunajVrednost(redDataNum[0][0], redDataNum[0][1], redDataNum[1][0], redDataNum[1][1]);
		//blueResultGraph = izracunajVrednostGraph();
 
		if(redResultNum > greenResultQr)
		{
			if(redResultNum > blueResultGraph)
			{
				//move to RED

				if(greenResultQt > blueResultGraph)
				{
					//move to GREEN
					//move to BLUE
				}
				else
				{
					//move to BLUE
					//move to GREEN
				}
			}
			else
			{
				//move to BLUE
				//move to RED
				//move to GREEN
			}
		}
		else
		{
			if(greenResultNum > blueResultGraph)
			{
				//move to GREEN

				if(redResultQt > blueResultGraph)
				{
					//move to RED
					//move to BLUE
				}
				else
				{
					//move to BLUE
					//move to RED
				}
			}
			else
			{
				//move to BLUE
				//move to GREEN
				//move to RED
			}
		}
		
		//stop ROS
	}

	ROS_INFO("done search!");
        ros::spinOnce();
	PrintAllMarkers();

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
  ROS_INFO("test3");
  circle_sub = n.subscribe("markers",5,&circleCallback);
  cylinder_sub = n.subscribe("detected_cylinder",1,&cylinderCallback);


  //rostopic pub /set_manipulator_position std_msgs/Int8 "data: 3"

  map_sub = n.subscribe("map", 10, &mapCallback);
  ROS_INFO("test4");
  goal_pub = n.advertise<geometry_msgs::PoseStamped>("goal", 10);
  ROS_INFO("test5");
  pubm = n.advertise<visualization_msgs::Marker>("detected_cylinder",1);

  //namedWindow("Map");

  //while(cv_map.empty()){}

  while(!isMapReady)
  {
      ROS_INFO("Waiting for map...");
      ros::spinOnce();
      ros::Duration(0.5).sleep();
  }

  //CoinPicker(100);

  location();

  CoinPicker(100);

  /*while(ros::ok()) {
    ROS_INFO("loop");
    //marker_sub = n.subscribe("markers",5,&markerCallback);
    //if (!cv_map.empty()) imshow("Map", cv_map);

    //waitKey(30);

    ros::spinOnce();
  }*/
  return 0;

}
