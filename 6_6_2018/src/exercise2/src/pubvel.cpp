#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <stdlib.h>
#include <std_msgs/String.h>

#include <iostream>
using namespace std;
void CircleMovement(){
	ros::NodeHandle nh;
	ros::Publisher pubC = nh.advertise<geometry_msgs::Twist>("cmd_vel", 1000);
	geometry_msgs::Twist msgC;
	ros::Rate rate(1);
	int count = 0;

	while(count<5){
		msgC.angular.z = 1.25;
		msgC.linear.x = 3;
		pubC.publish(msgC);
		rate.sleep();
		count = count + 1;
	}
}
void SquareMovement(){
	ros::NodeHandle nh;
	ros::Publisher pubSqr = nh.advertise<geometry_msgs::Twist>("cmd_vel", 1000);
	geometry_msgs::Twist msgSqr;
	ros::Rate rate(1);
	int count = 0;
	msgSqr.angular.z = 0;
	msgSqr.linear.x = 0;
	while(count < 7){
		if (count % 2 == 0){
			msgSqr.linear.x = 3;
			msgSqr.angular.z = 0;
		}else{
			msgSqr.linear.x = 0;
			msgSqr.angular.z = 1.55;
		}
		pubSqr.publish(msgSqr);
		rate.sleep();
		count = count + 1;
	}
}
int main(int argc, char *argv[])
{
	double scale_linear, scale_angular;

	ros::init(argc, argv, "publish_velocity");
	ros::NodeHandle nh;
	ros::NodeHandle pnh("~");

	//create a publisher object.
	ros::Publisher pub = nh.advertise<geometry_msgs::Twist>("cmd_vel", 1000);
    // For the turtle simulation map the topic to /turtle1/cmd_vel
    // For the turtlebot simulation and Turtlebot map the topic to /cmd_vel_mux/input/navi

	//Seed the random number generator.
	srand(time(0));

	//Loop at 2Hz until the node is shutdown.
	ros::Rate rate(2);

	pnh.getParam("scale_linear", scale_linear);
	pnh.getParam("scale_angular", scale_angular);

	while(ros::ok()){
		geometry_msgs::Twist msg;
		//msg.linear.x = scale_linear * (double(rand())/double(RAND_MAX));
		//msg.angular.z = scale_angular * 2 * (double(rand())/double(RAND_MAX)-1);

		char c = 0;
		cout << "'w', 'a', 's', 'd' for mowement or 'q' for drawing square, or 'e' for circle: ";
		cin >> c;
		bool movement = false;
		switch((c)) {
			case 'w':
			    cout << endl << "Up" << endl;//key up
			    msg.linear.x = 1;
			    break;
			case 's':
			    cout << endl << "Down" << endl;   // key down
			    msg.linear.x = -1;
			    break;
			case 'a':
			    cout << endl << "Left" << endl;  // key left
			    msg.angular.z = 1;
			    break;
			case 'd':
			    cout << endl << "Right" << endl;  // key right
			    msg.angular.z = -1;
			    break;
			case 'q':
			    cout << endl << "SQUARE" << endl;  // key right
			    // msgShape.shape = "square";
					SquareMovement();
					movement = true;
			    break;
		  case 'e':
					cout << endl << "CIRCLE" << endl;  // key right
					// msgShape.shape = "line";
					CircleMovement();
					movement = true;
					break;
			default:
			    cout << endl << "null" << endl;  // not arrow
			    break;
		}

		//cin >> msg.linear.x;
		//cin >> msg.angular.z;
		if(movement == false){
			pub.publish(msg);
		}
		// 	pubShape.publish(msgShape);

		ROS_INFO_STREAM("Sending data");

		//Wait untilit's time for another iteration.
		rate.sleep();
	}
	return 0;
}
