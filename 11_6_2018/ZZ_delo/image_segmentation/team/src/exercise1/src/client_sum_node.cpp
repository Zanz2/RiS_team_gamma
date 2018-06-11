#include "ros/ros.h"
#include "exercise1/Sum.h"

//#include <cstdlib>
//#include <sstream>

#include <stdlib.h>
#include <time.h>

int main(int argc, char **argv)
{
  ros::init(argc, argv, "our_client_sum_node");
  ros::NodeHandle n;

  //ROS_INFO("i am here");

  ros::ServiceClient client = n.serviceClient<exercise1::Sum>("our_service_sum_node/int32_arr");

  exercise1::Sum srv;

  //ROS_INFO("i am here 2");

  srand(time(NULL));
  int sendInt[10];

  for(int i=0; i<10; i++)
  {
    srv.request.intArr[i] = rand()%100+1;
    //srv.request.intArr[i] = 1;
    ROS_INFO("Sending: %d", srv.request.intArr[i]);
  }

  ros::service::waitForService("our_service_sum_node/int32_arr", 1000);


  if (client.call(srv))
  {
    ROS_INFO("The service returned: %d", srv.response.result);
  }
  else
  {
    ROS_ERROR("Failed to call service");
    return 1;
  }

  return 0;
}
