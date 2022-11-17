from iris_robots.robot_env import RobotEnv
from iris_robots.controllers.oculus_controller import VRPolicy
from iris_robots.data_collection.data_collector import DataCollector
from iris_robots.user_interface.gui import RobotGUI
import numpy as np
import torch
import time

policy = None

# Make the robot env
env = RobotEnv('172.16.0.21')

# Test Reset Position
time.sleep(2)
pos = env._robot.get_ee_pos()
angle = env._robot.get_ee_angle()
