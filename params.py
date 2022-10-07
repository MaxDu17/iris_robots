import numpy as np

#Robot-Specific Parameters
ROBOT_PARAMS = dict(
    {'franka': dict({
        'num_joints': 7,
        'reset_joints': np.array([0., -np.pi / 4, 0, -3 / 4 * np.pi, 0, np.pi / 2, 0.])
    }),
    'wx200': dict({
        'num_joints': 5,
        'reset_joints': np.array([0, -0.5, 0.5, np.pi / 2, 0.])
    }),
    'wx250s': dict({
        'num_joints': 6,
        'reset_joints': np.array([0, -0.3, 0.3, 0, np.pi / 2, 0])
    }),
})
