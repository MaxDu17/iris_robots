'''
Local Server Environment Wrapper
Camera Specific Functions: self.render_obs()
Experiment Specific Functions: self.get_info(), self.get_reward(), self.get_observation()
'''
import numpy as np
import requests
import io

class RobotInterface:
    def __init__(self, control_hz=None, ip_address='127.0.0.1', port = 5000):
        self.url_func = lambda x: 'http://' + ip_address + f":{port}/" + x
        # self.url_func = lambda x: 'http://' + ip_address + ':5000/' + x

    def update_control_hz(self, hz):
        info_dict = {"control_hz": np.array([hz]).tolist()}
        requests.post(self.url_func('update_hz'), json=info_dict)

    def update_pose(self, pos, angle):
        info_dict = {"pose": np.concatenate([pos, angle]).tolist()}
        return_dict = requests.post(self.url_func('update_pose'), json=info_dict)
        feasible_pos = np.array(return_dict.json()['feasible_pos'])
        feasible_angle = np.array(return_dict.json()['feasible_angle'])
        return feasible_pos, feasible_angle

    def update_joints(self, joints):
        info_dict = {"joints": joints.tolist()}
        requests.post(self.url_func('update_joints'), json=info_dict)

    def update_gripper(self, close_percentage):
        info_dict = {"gripper": np.array([close_percentage]).tolist()}
        requests.post(self.url_func('update_gripper'), json=info_dict)

    def get_joy_pos(self):
        info_dict = requests.post(self.url_func('get_joy_action'))
        return np.array(info_dict.json()['joy_action'])

    def get_joy_logistics(self):
        info_dict = requests.post(self.url_func('get_logistics'))
        return np.array(info_dict.json()['joy_logistics'])

    def get_ee_pos(self):
        info_dict = requests.post(self.url_func('get_pos'))
        return np.array(info_dict.json()['ee_pos'])

    def get_ee_angle(self):
        info_dict = requests.post(self.url_func('get_angle'))
        return np.array(info_dict.json()['ee_angle'])

    def get_joint_positions(self):
        info_dict = requests.post(self.url_func('get_qpos'))
        return np.array(info_dict.json()['qpos'])

    def get_joint_velocities(self):
        info_dict = requests.post(self.url_func('get_qvel'))
        return np.array(info_dict.json()['qvel'])

    def get_gripper_state(self):
        info_dict = requests.post(self.url_func('get_gripper_state'))
        return np.array(info_dict.json()['gripper_state'])

    def kill_server(self):
        requests.post(self.url_func('kill_server'))

    def all_send_receive(self, pos, angle, close_percentage):
        info_dict = {"pose": np.concatenate([pos, angle]).tolist(),
                     "gripper": np.array([close_percentage]).tolist()}
        return_dict = requests.post(self.url_func('get_set_all'), json=info_dict)

        return np.array(return_dict.json()["joy_action"]), np.array(return_dict.json()["joy_logistics"]), \
               np.array(return_dict.json()["ee_pos"]), np.array(return_dict.json()["ee_angle"]), np.array(return_dict.json()["gripper_state"]), \
               np.array(return_dict.json()["joint_pos"]), np.array(return_dict.json()["joint_vel"]), \
               np.array(return_dict.json()["feasible_pos"]), np.array(return_dict.json()["feasible_angle"]), \
               np.array(return_dict.json()["camera"], dtype = np.uint8)


    def read_cameras(self):
        camera_feed_bytes = requests.post(self.url_func('read_cameras')).content
        camera_feed_buffer = io.BytesIO(camera_feed_bytes)
        camera_feed = list(np.load(camera_feed_buffer, allow_pickle=True)['arr_0'])
        return camera_feed
