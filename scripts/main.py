from iris_robots.robot_env import RobotEnv
from iris_robots.controllers.oculus_controller import VRPolicy
from iris_robots.data_collection.data_collector import DataCollector
from iris_robots.user_interface.gui import RobotGUI
import numpy as np
import torch

policy = None

# Make the robot env
env = RobotEnv('172.16.0.1')
controller = VRPolicy()

# Make the data collector
data_collector = DataCollector(env=env, controller=controller, policy=policy)

# Make the GUI
user_interface = RobotGUI(robot=data_collector)

