import logging
import re
import warnings
logging.captureWarnings(True)
warnings.filterwarnings('always', category=DeprecationWarning,
                        module=r'^{0}\.'.format(re.escape(__name__)))
warnings.warn("This is a DeprecationWarning",category=DeprecationWarning)
from iris_robots.robot_env import RobotEnv
import numpy as np
import time

env = RobotEnv(control_hz=10, robot_model='wx250s', use_local_cameras=True, camera_types='cv2')
env.reset()
time.sleep(2)

angle = env._robot.get_ee_angle()
for i in range(10):
    print(i)
    state = np.zeros(3)
    state[0] = np.random.uniform(0.15, 0.30)
    state[1] = np.random.uniform(-0.15, 0.15)
    state[2] = np.random.uniform(0.03, 0.20)
    env._robot.update_pose(state, angle)
    time.sleep(3)



