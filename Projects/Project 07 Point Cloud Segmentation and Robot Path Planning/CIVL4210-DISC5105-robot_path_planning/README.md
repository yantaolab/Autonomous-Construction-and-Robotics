1. Agilex Scout -- ROS1 -- 2d planning -- ros nav stack

roslaunch robot_simulation simulation1.launch

roslaunch robot_simulation localization1.launch

roslaunch robot_simulation planning1.launch

2. Agilex Scout -- ROS1 -- 3d planning -- cmu aede

roslaunch robot_simulation simulation2.launch

roslaunch robot_simulation localization2.launch

roslaunch robot_simulation planning2.launch

3. Unitree Go2 -- ROS2 -- 3d planning -- cmu aede

ros2 launch robot_simulation simulation.launch.py

ros2 launch robot_simulation localization.launch.py

ros2 launch robot_simulation planning.launch.py
