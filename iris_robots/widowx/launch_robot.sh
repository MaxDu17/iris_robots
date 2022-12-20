source "$(dirname "$(realpath $0)")"/devel/setup.bash

if [ $# -eq 0 ];
  then
    echo "Please input robot model (wx200, wx250s)"
    exit 0
elif [ "$1" = "wx200" ];
  then
    echo "Starting WidowX200"
elif [ "$1" = "wx250s" ]; 
  then
    echo "Staring WidowX250s"
else
  echo "Invalid Robot Model. Currently supporting wx200 and wx250s"
  exit 0
fi

#roslaunch interbotix_xsarm_control /home/iris/iris_robots/iris_robots/widowx/src/interbotix_ros_manipulators/interbotix_ros_xsarms/interbotix_xsarm_control/launch/xsarm_control.launch  robot_model:=$1
roslaunch interbotix_xsarm_control xsarm_control.launch robot_model:=$1

#/home/iris/iris_robots/iris_robots/widowx/src/interbotix_ros_manipulators/interbotix_ros_xsarms/interbotix_xsarm_control/launch
