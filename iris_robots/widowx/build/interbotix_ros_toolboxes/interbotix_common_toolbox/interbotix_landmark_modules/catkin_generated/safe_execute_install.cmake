execute_process(COMMAND "/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/build/interbotix_ros_toolboxes/interbotix_common_toolbox/interbotix_landmark_modules/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/build/interbotix_ros_toolboxes/interbotix_common_toolbox/interbotix_landmark_modules/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
