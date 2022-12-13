from gym.envs.registration import register

register(
    id='wx200',
    entry_point='iris_robots.robot_env:RobotEnv',
    kwargs = {"robot_model" : "wx200"}
)

register(
    id='iris_dummy',
    entry_point='iris_robots.robot_env:RobotEnv',
    kwargs = {"robot_model" : "dummy"}
)

register(
    id='online',
    entry_point='iris_robots.robot_env:RobotEnv',
)
