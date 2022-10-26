import numpy as np

DATA_PATH='iris_robots/training_data/'

with open(DATA_PATH, 'rb') as f:
    trajectories = np.load(DATA_PATH, allow_pickle=True)

actions = []
commanded_delta_pose = []        #next desired pose - current pose
achieved_delta_pose = []         #next achieved pose - current pose

for path in trajectories:
    for t in range(len(path['observations']) - 1):
        action = path['actions'][t]
        current_pose = path['observations'][t]['current_pose']
        next_desired_pose = path['observations'][t + 1]['desired_pose']
        next_achieved_pose = path['observations'][t]['achieved_pose']

        action.append(action)
        commanded_delta_pose.append(next_desired_pose - current_pose)
        achieved_delta_pose.append(next_achieved_pose - current_pose)

