cmake_minimum_required(VERSION 2.8.3)
project(exercise3)

find_package(catkin REQUIRED COMPONENTS
	roscpp
	cv_bridge
	sensor_msgs
	nav_msgs
	std_msgs
	geometry_msgs
	tf
)

find_package( OpenCV REQUIRED )

catkin_package()

include_directories(include ${catkin_INCLUDE_DIRS} ${OpenCV_INCLUDE_DIRS})
add_executable(map_goals src/map_goals.cpp)
target_link_libraries(map_goals ${catkin_LIBRARIES} ${OpenCV_LIBRARIES})

add_executable(map_goals_dn src/map_goals_dn.cpp)
target_link_libraries(map_goals_dn ${catkin_LIBRARIES} ${OpenCV_LIBRARIES})



add_executable(map_goals_move src/map_goals_move.cpp)
target_link_libraries(map_goals_move ${catkin_LIBRARIES} ${OpenCV_LIBRARIES})

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(map_goals_move ${PYTHON_LIBRARIES})




add_executable(competitionRun src/competitionRun.cpp)
target_link_libraries(competitionRun ${catkin_LIBRARIES} ${OpenCV_LIBRARIES})

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})
target_link_libraries(competitionRun ${PYTHON_LIBRARIES})
