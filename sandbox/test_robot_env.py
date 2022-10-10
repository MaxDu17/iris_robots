from iris_robots.robot_env import RobotEnv

env = RobotEnv(robot_model='wx250s', use_local_cameras=True, camera_types='cv2')
import pdb; pdb.set_trace()