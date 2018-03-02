#include "ros/ros.h"
#include "exercise1/Sum.h"

#include <string>
#include <iostream>
#include <algorithm>

bool manipulate(exercise1::Sum::Request  &req,
         exercise1::Sum::Response &res)
{
  int avg = 0;
  //int intArr[] = req.intArr;

  ROS_INFO("asd");

  for(int i = 0; i<10; i++)
  {
    ROS_INFO("%d", req.intArr[0]);
    avg += req.intArr[i];
  }

  res.result = avg/10;

  //ROS_INFO("request: %s, response: %s", req.content.c_str(), res.comment.c_str());
  return true;
}

int main(int argc, char **argv)
{
  ros::init(argc, argv, "our_service_sum_node");
  ros::NodeHandle n;

  ros::ServiceServer service = n.advertiseService("our_service_sum_node/int32_arr", manipulate);
  //ROS_INFO("I am ready to mess up your string!");
ROS_INFO("asd3");
  ros::spin();
ROS_INFO("asd4");
  return 0;
}
