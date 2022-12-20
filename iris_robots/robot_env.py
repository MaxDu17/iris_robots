'''
Basic Robot Environment Wrapper
Robot Specific Functions: self._update_pose(), self.get_ee_pos(), self.get_ee_angle()
Camera Specific Functions: self.render_obs()
Experiment Specific Functions: self.get_info(), self.get_reward(), self.get_observation()
'''
import numpy as np
import time
import gym
from gym import spaces
from params import ROBOT_PARAMS

from iris_robots.transformations import add_angles, angle_diff
from iris_robots.camera_utils.multi_camera_wrapper import MultiCameraWrapper
from iris_robots.server.robot_interface import RobotInterface
from iris_robots.controllers.xbox_controller import XboxController

class RobotEnv(gym.Env):
    def __init__(self, ip_address=None, robot_model='dummy', control_hz=20, use_local_cameras=False, use_robot_cameras=False,
            camera_types=['cv2'], blocking=True, reset_pos = None, control_mode = "POSORIENT",
            xlims = None, ylims = None, zlims = None):
        # Initialize Gym Environment
        super().__init__()
        #TODO: allow for custom reset location

        # Physics
        self.use_desired_pose = True
        self.max_lin_vel = 1.0
        self.max_rot_vel = 1.0

        self.hz = control_hz
        self.blocking=blocking
        self.xlims = xlims 
        self.ylims = ylims 
        self.zlims = zlims

        if control_mode == "POSORIENT":
            self.DoF = 6
        elif control_mode == "POS":
            self.DoF = 3
        else:
            raise Exception("control mode not implemented!")

        self.action_space = spaces.Box(np.array([-1,-1,-1,-1,-1,-1,-1]),np.array([1,1,1,1,1,1,1]),dtype=np.float32)
        self.observation_space = spaces.Box(-10, 10,dtype=np.float32) # TODO figure out what is going on with this
        #self.action_space = np.ones(shape = ((self.DoF + 1), 2))

        # Robot Configuration
        self.robot_model = robot_model
        if ip_address is None:
            if robot_model == 'franka':
                from iris_robots.franka.robot import FrankaRobot
                self._robot = FrankaRobot(control_hz=self.hz)
            elif robot_model == 'wx200':
                from iris_robots.widowx.robot import WidowX200Robot
                self._robot = WidowX200Robot(control_hz=self.hz, blocking=blocking)
            elif robot_model == 'wx250s':
                from iris_robots.widowx.robot import WidowX250SRobot
                self._robot = WidowX250SRobot(control_hz=self.hz, blocking=blocking)
            elif robot_model == 'dummy':
                from iris_robots.dummy_robot import DummyRobot
                self._robot = DummyRobot()
            else:
                raise NotImplementedError

        else:
            self._robot = RobotInterface(ip_address=ip_address)

        # Reset joints
        self.reset_joints = ROBOT_PARAMS[robot_model]['reset_joints']

        # Create Cameras
        self._use_local_cameras = use_local_cameras
        self._use_robot_cameras = use_robot_cameras

        if self._use_local_cameras:
            self._camera_reader = MultiCameraWrapper(camera_types=camera_types)

        self.reset()

    def step(self, action):
        start_time = time.time()

        # Process Action
        assert len(action) == (self.DoF + 1)
        assert (action.max() <= 1) and (action.min() >= -1)

        pos_action, angle_action, gripper = self._format_action(action)
        lin_vel, rot_vel = self._limit_velocity(pos_action, angle_action)
        desired_pos = self._curr_pos + lin_vel
        desired_angle = add_angles(rot_vel, self._curr_angle)
        print(desired_pos, desired_angle)
        # safeguard
        if self.xlims is not None and (desired_pos[0] > self.xlims[1] or desired_pos[0] < self.xlims[0]):
            print("xlim")
            desired_pos[0] = self._curr_pos[0]
        if self.ylims is not None and (desired_pos[1] > self.ylims[1] or desired_pos[1] < self.ylims[0]):
            print("ylim")
            desired_pos[1] = self._curr_pos[1]
        if self.zlims is not None and (desired_pos[2] > self.zlims[1] or desired_pos[2] < self.zlims[0]):
            print("zlim")
            desired_pos[2] = self._curr_pos[2]

        self._update_robot(desired_pos, desired_angle, gripper)

        comp_time = time.time() - start_time
        sleep_left = max(0, (1 / self.hz) - comp_time)
        time.sleep(sleep_left)
        return self.get_observation(), self.get_reward(), self.get_done(), self.get_info()

    def get_joy_info(self):
        action = self._robot.get_joy_pos()
        logistics = self._robot.get_joy_logistics()
        return action, logistics
    
    def get_reward(self):
        return 0

    def get_done(self):
        return 0

    def get_info(self):
        return {}


    def step_direct(self, action):
        start_time = time.time()
        assert len(action) == 7 #position, angle, gripper
        desired_pos = self._curr_pos + action[:3]
        desired_angle = add_angles(action[3:6], self._curr_angle)

        self._update_robot(desired_pos, desired_angle, action[6])
        # print(desired_pos)
        comp_time = time.time() - start_time
        sleep_left = max(0, (1 / self.hz) - comp_time)
        time.sleep(sleep_left)
        return self.get_observation(), self.get_reward(), self.get_done(), self.get_info()

    def update_robot(self, desired_pos, desired_angle, gripper):
        self._update_robot(desired_pos, desired_angle, gripper)

    def reset_to(self, state):
        raise Exception("not implemented yet!")

    def reset(self):
        print("resetting!")
        self._robot.update_gripper(0)
        self._robot.update_joints(self.reset_joints)
        self._desired_pose = {'position': self._robot.get_ee_pos(),
                              'angle': self._robot.get_ee_angle(),
                              'gripper': 0}
        self._default_angle = self._desired_pose['angle']
        time.sleep(2.5)
        return self.get_observation()

    def _format_action(self, action):
        '''Returns [x,y,z], [yaw, pitch, roll], close_gripper'''
        default_delta_angle = angle_diff(self._default_angle, self._curr_angle)
        if self.DoF == 3:
            delta_pos, delta_angle, gripper = action[:-1], default_delta_angle, action[-1]
        # elif self.DoF == 4:
        #     delta_pos, delta_angle, gripper = action[:3], action[3], action[-1]
        #     delta_angle = delta_angle.extend([0,0])
        # elif self.DoF == 5:
        #     delta_pos, delta_angle, gripper = action[:3], action[3:5], action[-1]
        #     delta_angle = delta_angle.append(0)
        elif self.DoF == 6:
            delta_pos, delta_angle, gripper = action[:3], action[3:6], action[-1]
        return np.array(delta_pos), np.array(delta_angle), gripper

    def _limit_velocity(self, lin_vel, rot_vel):
        """Scales down the linear and angular magnitudes of the action"""
        lin_vel_norm = np.linalg.norm(lin_vel)
        rot_vel_norm = np.linalg.norm(rot_vel)
        if lin_vel_norm > self.max_lin_vel:
            lin_vel = lin_vel * self.max_lin_vel / lin_vel_norm
        if rot_vel_norm > self.max_rot_vel:
            rot_vel = rot_vel * self.max_rot_vel / rot_vel_norm
        lin_vel, rot_vel = lin_vel / self.hz, rot_vel / self.hz
        return lin_vel, rot_vel

    def _update_robot(self, pos, angle, gripper):
        
        # feasible_pos, feasible_angle = self._robot.update_pose_3DOF_zangle(pos, angle[0])
        # LEGAL
        # [[0 0  1.]
        # [ 0 1 0]
        # [-1  0  0]]

        feasible_pos, feasible_angle = self._robot.update_pose(pos, angle)
        # Illegal
        # [[-5.21278218e-02 -6.14422767e-03  9.98621519e-01]
        # [-6.39736750e-04  9.99981073e-01  6.11919849e-03]
        # [-9.98640216e-01 -3.19874396e-04 -5.21307659e-02]]

        self._robot.update_gripper(gripper)
        self._desired_pose = {'position': feasible_pos,
                              'angle': feasible_angle,
                              'gripper': gripper}

    @property
    def _curr_pos(self):
        if self.use_desired_pose: return self._desired_pose['position'].copy()
        return self._robot.get_ee_pos()

    @property
    def _curr_angle(self):
        if self.use_desired_pose: return self._desired_pose['angle'].copy()
        return self._robot.get_ee_angle()

    def get_images(self):
        camera_feed = []
        if self._use_local_cameras:
            camera_feed.extend(self._camera_reader.read_cameras())
        if self._use_robot_cameras:
            camera_feed.extend(self._robot.read_cameras())
        return camera_feed

    def get_state(self):
        state_dict = {}
        gripper_state = self._robot.get_gripper_state()

        state_dict['control_key'] = 'desired_pose' if \
            self.use_desired_pose else 'current_pose'

        state_dict['desired_pose'] = np.concatenate(
            [self._desired_pose['position'],
            self._desired_pose['angle'],
            [self._desired_pose['gripper']]])

        state_dict['current_pose'] = np.concatenate(
            [self._robot.get_ee_pos(),
            self._robot.get_ee_angle(),
            [gripper_state[0]]])

        state_dict['joint_positions'] = self._robot.get_joint_positions()
        state_dict['joint_velocities'] = self._robot.get_joint_velocities()
        state_dict['gripper_velocity'] = gripper_state[1]

        return state_dict

    def get_observation(self, include_images=True, include_robot_state=True):
        obs_dict = {}
        if include_images:
            obs_dict['images'] = self.get_images()
        if include_robot_state:
            state_dict = self.get_state()
            obs_dict.update(state_dict)
        return obs_dict

    def render(self, height, width, mode):
        #TODO: full sized image renderings!
        return self.get_images()

    def is_robot_reset(self, epsilon=0.1):
        curr_joints = self._robot.get_joint_positions()
        joint_dist = np.linalg.norm(curr_joints - self.reset_joints)
        return joint_dist < epsilon

    @property
    def num_cameras(self):
        return len(self.get_images())

if __name__ == "__main__":
    robot = RobotEnv( ip_address=None, robot_model='wx200', control_hz=20, use_local_cameras=False,
                 use_robot_cameras=False,
                 camera_types=['cv2'], blocking=False, reset_pos=None, control_mode="POSORIENT",
                 xlims = [0.12, 0.33], ylims = [-0.23, 0.23], zlims = [0.032, 0.3])
    
    controller = XboxController(robot)
    robot.reset()
    for i in range(2000):
        # time.sleep(0.5)
        action = controller.get_action()
        if controller.get_logistics():
            quit()
        # print(action)
        # print(robot.get_observation()["current_pose"][2])
        robot.step(action)