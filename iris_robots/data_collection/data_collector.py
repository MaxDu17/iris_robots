from datetime import date
from copy import deepcopy
import numpy as np
import time
import os

from PIL import Image
import numpy as np
import time


class DataCollector:

	def __init__(self, env, controller, policy=None, log_dir=None):
		self.env = env
		self.num_cameras = self.env.num_cameras
		self.traj_running = False
		self.action_noise = None
		self.controller = controller
		self.policy = policy
		self.traj_num = 0
		self.log_dir = log_dir
		if log_dir is None:
			import iris_robots
			self.log_dir=os.path.join(os.path.dirname(iris_robots.__file__), 'training_data')

		# self.log_dir = '/home/sasha/Desktop/irisnet/{0}/'.format(date.today())

		# Data Variables #
		self.traj_name = None
		self.traj_info = None
		self.traj_data = None
		self.traj_saved = None

		return None

	def reset_robot(self):
		self.env.reset()
		self.controller.reset_state()

	# def is_robot_reset(self):
	# 	return self.env.is_robot_reset()

	def get_user_feedback(self):
		info = self.controller.get_info()
		return deepcopy(info)

	def save_trajectory(self):
		if self.traj_saved: return
		print('Saving Trajectory #{0}'.format(self.traj_num))

		filepath = os.path.join(self.log_dir, self.traj_name + '.npy')
		os.makedirs(self.log_dir, exist_ok=True)
		np.save(filepath, self.traj_data)

		self.traj_saved = True
		self.traj_num += 1

	def delete_trajectory(self):
		if not self.traj_saved: return
		print('Deleting Trajectory #{0}'.format(self.traj_num - 1))

		filepath = os.path.join(self.log_dir + self.traj_name + '.npy')
		os.remove(filepath)

		self.traj_saved = False
		self.traj_num -= 1		

	def collect_trajectory(self, info={}, practice=False):
		"""
		Collect trajectory until we end

		Notes: Save last trajectory, and whether or not we kept it
		"""
		self.reset_robot()
		self.traj_running = True
		self.traj_name = time.asctime().replace(" ", "_")
		self.traj_data = dict(observations=[], actions=[], state=[], info=info)
		self.traj_saved = False
		delays = []

		while True:

			# Determine If User Ended Episode #
			feedback = self.get_user_feedback()
			end_traj = feedback['save_episode'] or feedback['delete_episode']
			save = feedback['save_episode'] and (not practice) and (self.policy is None)

			# if feedback['movement_enabled']: self.traj_running = True
			#else: continue

			# End Episode Appropriately #
			if end_traj:
				self.traj_running = False
				if save: self.save_trajectory()
				return

			# Get Latest Observation And Action #
			#act = np.random.normal(loc=act, scale=self.action_noise)
			obs = self.env.get_observation()
			if self.policy is None:
				act = self.controller.get_action(obs)
			else:
				act = self.policy(process_observation(obs), None).flatten().detach().numpy()
				print(act)
			self._last_obs = obs.copy()

			##print(obs['joint_positions'])
			# obs['images'] = [feed['images'] for feed in obs['images'] if feed['images']['type'] == 'rgb']
			# import pdb; pdb.set_trace()

			# Add Relevant Info To Obs #
			obs['movement_enabled'] = feedback['movement_enabled']
			obs['step_time'] = time.time()

			for feed_dict in obs['images']:
				delays.append(obs['step_time'] - feed_dict['read_time'])

			# Save Data #
			if obs['movement_enabled']:
				self.traj_data['observations'].append(obs)
				self.traj_data['actions'].append(act)

			# Step Environment #
			self.env.step(act)

	def get_camera_feed(self):
		if self.traj_running and len(self.traj_data['observations']) > 0: camera_feed = self._last_obs['images']
		else: camera_feed = self.env.get_images()
		#camera_feed = self.env.get_images()
		return [feed['array'] for feed in camera_feed]

	def set_action_noise(self, noise_percentage, low=0, high=0.1):
		self.action_noise = noise_percentage * (high - low) + low
