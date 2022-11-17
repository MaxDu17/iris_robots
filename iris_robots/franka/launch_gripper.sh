source ~/anaconda3/etc/profile.d/conda.sh
conda activate polymetis-local
#echo robot | sudo -S chmod a+rw /dev/ttyUSB0
launch_gripper.py gripper=franka_hand gripper.executable_cfg.robot_ip=172.16.0.11 
