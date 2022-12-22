from flask import Flask, jsonify, request, send_file, make_response
from PIL import Image
import numpy as np
import io
from iris_robots.controllers.xbox_controller import XboxController
from iris_robots.camera_utils.multi_camera_wrapper import MultiCameraWrapper


app = Flask(__name__)

# def start_server():
#     app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

### SERVER LAUNCHER ###
def start_server(robot, camera=None):
    global robot_controller
    global camera_reader
    global xbox_controller 
    xbox_controller = XboxController(robot)

    robot_controller = robot
    camera_reader = camera
    #app.run(host='0.0.0.0', debug = True)
    # app.run(host='0.0.0.0', port = 5000, debug = True)
    app.run(host='0.0.0.0', port = 9136)
    #app.run(host="172.0.0.0")



### KILL SEREVER ###
@app.route('/kill_server', methods=['POST'])
def kill_robot_request():
    robot_controller.kill_server()
    return 'Killed Server'

### ROBOT POSE UPDATES ###
@app.route('/update_pose', methods=['POST'])
def update_pose_request():
    # print("POSE")
    pose = np.array(request.json['pose'])
    pos, angle = pose[:3], pose[3:]
    feasible_pos, feasbile_angle = robot_controller.update_pose(pos, angle)
    return jsonify({"feasible_pos": np.array(feasible_pos).tolist(),
                    "feasible_angle": np.array(feasbile_angle).tolist()})

@app.route('/update_joints', methods=['POST'])
def update_joints_request():
    # print("JOINTS")
    joints = np.array(request.json['joints'])
    robot_controller.update_joints(joints)
    return 'Pose Updated'

@app.route('/update_gripper', methods=['POST'])
def update_gripper_request():
    # print("GRIPPER")
    close_percentage = np.array(request.json['gripper'])
    robot_controller.update_gripper(close_percentage)
    return 'Pose Updated'

### ROBOT STATE REQUESTS ###
@app.route('/get_pos', methods=['POST'])
def get_ee_pos_request():
    # print("EEPOSE")
    robot_pos = robot_controller.get_ee_pos()
    return jsonify({"ee_pos": np.array(robot_pos).tolist()})

### XBOX CONTROLLER REQUESTS ###
@app.route('/get_joy_action', methods=['POST'])
def get_action_request():
    # print("EEPOSE")
    action = xbox_controller.get_action()
    print(action)
    return jsonify({"joy_action": np.array(action).tolist()})


@app.route('/get_set_all', methods=['POST'])
def get_set_all():
    pose = np.array(request.json['pose'])
    pos, angle = pose[:3], pose[3:]
    feasible_pos, feasbile_angle = robot_controller.update_pose(pos, angle)
    close_percentage = np.array(request.json['gripper'])
    robot_controller.update_gripper(close_percentage)

    # print("EEPOSE")
    action = xbox_controller.get_action()
    logistics = xbox_controller.get_logistics()
    robot_pos = robot_controller.get_ee_pos()
    robot_angle = robot_controller.get_ee_angle()
    robot_gripper_state = robot_controller.get_gripper_state()
    joint_angle = robot_controller.get_ee_angle()
    joint_vel = robot_controller.get_joint_velocities()

    camera_feed = camera_reader.read_cameras()
    this_camera = camera_feed[0]["array"] #TEMP SOLUTION

    return jsonify({"joy_action": np.array(action).tolist(),
    "joy_logistics" : np.array(logistics).tolist(),
    "ee_pos" : np.array(robot_pos).tolist(),
    "ee_angle" : np.array(robot_angle).tolist(), 
    "gripper_state" : np.array(robot_gripper_state).tolist(),
    "joint_pos" : np.array(joint_angle).tolist(), 
    "joint_vel" : np.array(joint_vel).tolist(),
    "feasible_pos": np.array(feasible_pos).tolist(),
    "feasible_angle": np.array(feasbile_angle).tolist(),
    "camera": np.array(this_camera, dtype = np.uint8).tolist()})

### ROBOT STATE REQUESTS ###
@app.route('/get_logistics', methods=['POST'])
def get_feedback_request():
    # print("EEPOSE")
    logistics = xbox_controller.get_logistics()
    return jsonify({"joy_logistics": np.array(logistics).tolist()})

@app.route('/get_angle', methods=['POST'])
def get_ee_angle_request():
    robot_angle = robot_controller.get_ee_angle()
    return jsonify({"ee_angle": np.array(robot_angle).tolist()})

@app.route('/get_qpos', methods=['POST'])
def get_qpos_request():
    robot_qpos = robot_controller.get_joint_positions()
    return jsonify({"qpos": np.array(robot_qpos).tolist()})

@app.route('/get_qvel', methods=['POST'])
def get_qvel_request():
    robot_qvel = robot_controller.get_joint_velocities()
    return jsonify({"qvel": np.array(robot_qvel).tolist()})

@app.route('/get_gripper_state', methods=['POST'])
def get_gripper_state_request():
    # print("GRIPPERSTATE")
    robot_gripper_state = robot_controller.get_gripper_state()
    return jsonify({"gripper_state": np.array(robot_gripper_state).tolist()})

# ### IMAGE REQUESTS ###
@app.route('/read_cameras', methods=['POST'])
def read_cameras():
    camera_feed = camera_reader.read_cameras()
    buffer = io.BytesIO()

    np.savez_compressed(buffer, camera_feed)
    buffer.seek(0)

    return send_file(buffer, 'camera_feed.npz')

if __name__ == "__main__":
    robot_model = "wx200"
    # robot_model = "dummy"
    hz = 5
    blocking = False
    
    camera_reader = MultiCameraWrapper(camera_types=['cv2'])


    if robot_model == 'franka':
        from iris_robots.franka.robot import FrankaRobot
        robot = FrankaRobot(control_hz=hz)
    elif robot_model == 'wx200':
        from iris_robots.widowx.robot import WidowX200Robot
        robot = WidowX200Robot(control_hz=hz, blocking=blocking)
    elif robot_model == 'wx250s':
        from iris_robots.widowx.robot import WidowX250SRobot
        robot = WidowX250SRobot(control_hz=hz, blocking=blocking)
    elif robot_model == 'dummy':
        from iris_robots.dummy_robot import DummyRobot
        robot = DummyRobot()
    else:
        raise Exception("invalid config!")
    start_server(robot, camera = camera_reader)
    print("DONE INITIALIZING")