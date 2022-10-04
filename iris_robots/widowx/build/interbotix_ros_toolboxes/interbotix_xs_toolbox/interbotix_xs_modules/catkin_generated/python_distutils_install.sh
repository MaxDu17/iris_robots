#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/src/interbotix_ros_toolboxes/interbotix_xs_toolbox/interbotix_xs_modules"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/install/lib/python3/dist-packages:/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/build/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/build" \
    "/usr/bin/python3" \
    "/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/src/interbotix_ros_toolboxes/interbotix_xs_toolbox/interbotix_xs_modules/setup.py" \
     \
    build --build-base "/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/build/interbotix_ros_toolboxes/interbotix_xs_toolbox/interbotix_xs_modules" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/install" --install-scripts="/iris/u/jyang27/dev/iris_robots/iris_robots/widowx/install/bin"
