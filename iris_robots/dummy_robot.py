import numpy as np
# this is for offline testing if you don't have a robot on you
class DummyRobot:
    def update_pose(self, pos, angle, duration=1.5):
        return np.zeros_like(pos), np.zeros_like(angle)

    def update_joints(self, joints, duration=1.5):
        pass

    def update_gripper(self, close_percentage):
        pass

    def get_joint_positions(self):
        return np.zeros(shape = (6,))

    def get_joint_velocities(self):
        return np.zeros(shape = (6,))


    def get_gripper_state(self):
        return np.array([0, 0])

    def get_ee_pose(self):
        return np.zeros(shape = (3,)), np.zeros(shape = (4,))

    def get_ee_pos(self):
        '''Returns [x,y,z]'''
        return np.zeros(shape = (3,))

    def get_ee_angle(self):
        '''Returns [yaw, pitch, roll]'''
        return np.zeros(shape = (3,))

if __name__ == '__main__':
    robot = DummyRobot()
    import pdb; pdb.set_trace()
