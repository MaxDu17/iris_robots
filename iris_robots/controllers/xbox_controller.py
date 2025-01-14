'''
Xbox Controller Class
USE DETAILS: Create an instance, call get_action() to get action, and get_info() for data collection information
QUESTIONS: If you have questions, reach out to Sasha :)
'''

import pygame
import numpy as np

pygame.init()
pygame.joystick.init()

class XboxController:

    def __init__(self, env):
        # Initialize Controller
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        # Control Parameters
        self.threshold = 0.01
        self.DoF = 6 #env.DoF

        # Save Gripper
        self.gripper_closed = False
        self.button_resetted = True

    def cut(self, value):
        EPSILON = 0.07
        if abs(value) < EPSILON:
            return 0
        return value

    def get_logistics(self): 
        # for quitting, rejecting, etc
        pygame.event.get()
        term_succ = self.joystick.get_button(3)
        term_fail = self.joystick.get_button(2)
        if term_succ or term_fail:
            self.gripper_closed = False
            self.button_resetted = True
        # reject = self.joystick.get_button(2)
        return np.array([term_succ, term_fail]) 

    def get_action(self):
        pygame.event.get()
        # scaler = 0.05
        scaler = 0.25

        # XYZ Dimensions
        x =  scaler * self.cut(self.joystick.get_axis(0))
        y = - scaler * self.cut(self.joystick.get_axis(1))
        # y = - scaler * self.cut((self.joystick.get_button(2) - self.joystick.get_button(1)))#scaler * self.joystick.get_axis(1)
        # y = - scaler * self.cut((self.joystick.get_button(2) - self.joystick.get_button(1)))#scaler * self.joystick.get_axis(1)
        # z = (self.joystick.get_axis(5) - self.joystick.get_axis(2)) / 2
        # z = self.joystick.get_axis(2)
        z = scaler * 0.5 * ((self.joystick.get_axis(2) + 1) - (self.joystick.get_axis(5) + 1))
        # z = scaler * (self.joystick.get_button(2) - self.joystick.get_button(1))
        # print(x, y, z)
        # Orientation Dimensions
        yaw = 0.1 * self.cut(self.joystick.get_axis(3))
        pitch = - 0.1 * self.cut(self.joystick.get_axis(4))
        roll = 0 #self.joystick.get_button(4) - self.joystick.get_button(5)
        # print([self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())])
        # print([self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())])
        # print([self.joystick.get_hat(i) for i in range(self.joystick.get_numhats())])

        # Process Pose Action
        pose_action = np.array([x, y, z, roll, pitch, yaw])[:self.DoF]
        # pose_action[np.abs(pose_action) < self.threshold] = 0.

        # Process Gripper Action
        self._update_gripper_state(self.joystick.get_button(1))
        # gripper_action = [self.gripper_closed * 2 - 1]
        gripper_action = [self.gripper_closed]

        #return np.array([x, y, z, pitch, roll, gripper])
        return np.concatenate([pose_action, gripper_action])

    def get_info(self):
        pygame.event.get()
        reset_episode = self.joystick.get_button(15)
        save_episode = self.joystick.get_button(11)
        delete_episode = self.joystick.get_button(16)
        
        if reset_episode:
            self.gripper_closed = False
            self.button_resetted = True

        return {'reset_episode': reset_episode, 'save_episode': save_episode, 'delete_episode': delete_episode}

    def _update_gripper_state(self, toggle_gripper):
        if toggle_gripper and self.button_resetted:
            self.gripper_closed = not self.gripper_closed
            self.button_resetted = False

        if not toggle_gripper:
            self.button_resetted = True


