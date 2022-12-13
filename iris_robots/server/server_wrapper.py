import iris_robots
import robot_server
robot_model = "wx200"
# robot_model = "dummy"
hz = 5
blocking = True

from iris_robots.widowx.robot import WidowX200Robot
robot = WidowX200Robot(control_hz=hz, blocking=blocking)
robot_server.bind_server(robot)
robot_server.start_server() #(robot)
import pdb
pdb.set_trace()

if robot_model == 'franka':
    from iris_robots.franka.robot import FrankaRobot
    robot = FrankaRobot(control_hz=hz)
elif robot_model == 'wx200':
    from iris_robots.widowx.robot import WidowX200Robot
    robot = WidowX200Robot(control_hz=hz, blocking = blocking)
elif robot_model == 'wx250s':
    from iris_robots.widowx.robot import WidowX250SRobot
    robot = WidowX250SRobot(control_hz=hz, blocking=blocking)
elif robot_model == 'dummy':
    from iris_robots.dummy_robot import DummyRobot
    robot = DummyRobot()
else:
    raise Exception("invalid config!")
print("DONE INITIALIZING")


