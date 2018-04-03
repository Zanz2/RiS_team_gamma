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

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

using namespace std;
using namespace cv;

Mat cv_map;
float map_resolution = 0;
tf::Transform map_transform;

ros::Publisher goal_pub;
ros::Subscriber map_sub;

typedef actionlib::SimpleActionClient<move_base_msgs::MoveBaseAction> MoveBaseClient;

void location();

void mapCallback(const nav_msgs::OccupancyGridConstPtr& msg_map) {
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
  location();
}

void location() {

  MoveBaseClient ac("move_base", true);



  //now = rospy.Time.now();
  //listener.waitForTransform('map', 'base_footprint', now, rospy.Duration(10.0))


  while(!ac.waitForServer(ros::Duration(5.0)))
  {
    ROS_INFO("Waiting for move_base server");
  }

  int points[8][2] = {
    {-0.3, -1.1},
    {-0.3, -2},
    {-1.5, -2},
    {-0.4, -3.4},
    {-1.5, -3.7},
    {-1.65, -4.8},
    {-0.9, -5},
    {-0.2, -4.7}
  };

  for(int i = 0; i<8; i++)
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
      ROS_INFO("WE DID IT");

      for(int i=0;i<8;i++) {
        FILE *fd = fopen("RingDetect.py", "r");
        PyRun_SimpleFileEx(fd, "RingDetect.py", 1);

        FILE *fd = fopen("rotate.py", "r");
        PyRun_SimpleFileEx(fd, "rotate.py", 1);
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
  map_sub = n.subscribe("map", 10, &mapCallback);
  ROS_INFO("test4");
  goal_pub = n.advertise<geometry_msgs::PoseStamped>("goal", 10);
  ROS_INFO("test5");
  //namedWindow("Map");

  //while(cv_map.empty()){}

  //location();

  while(ros::ok()) {

    if (!cv_map.empty()) imshow("Map", cv_map);

    waitKey(30);

    ros::spinOnce();
  }
  return 0;

}
