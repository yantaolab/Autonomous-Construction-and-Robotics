# Simulation Environment for Robot Path Planning

ARM version is built and tested on Apple M1. It should work for all popular arm based computers. This version is just provided for the students who only has mac laptop.

AMD version (the default version) should work for most computers.

To build or modify the image your self, `cd` to docker folder and use `bash build.sh`(unless you want to study the code and modify it). Check the`Dockerfile` for more information.

Currently, the arm version only supports simulation with ROS Noetic, which is related to Gazebo on arm platforms. That means only agilex scout simulation is available.

**You can also follow the video demo demonstration on youtube**: [video](https://youtu.be/SpfFHGnlRy0?si=nz6raTS59nSYDXwe)

## Step1

1. install docker desktop (docker pull command download the image from cloud. You can use the command in any folder in windows/mac/wsl to download the image)

## Step2

**For windows user**

2. go the the corresponding docker folder, and start a terminal (or cd to the folder)
3. windows use can pull the agilex scout image

```
docker pull joriswenyuli/ros_agilex_scout_sim:latest
```

or unitree go2 image

```
docker pull joriswenyuli/ros_unitree_go2_sim:latest
```

**For macos user**

2. go the the corresponding docker folder, and start a terminal (or cd to the folder)
3. macos user can only use agilex scout image.Please pull the arm version,ros_agilex_scout_sim_arm, by

```
docker pull joriswenyuli/ros_agilex_scout_sim_arm:latest
```

## Step3

4. use

```
bash run.sh
```

to create a container and open a terminal, then you can enter the command.

5. use

```
bash exec.sh
```

to open a terminal in an existing container, then you can paste the command (you should have used `bash run.s` to make sure that you have created and started a container, then `bash exec.sh` can help you open other terminal to enter the container).

Alternatively, you can install the `container tools` or `dev containers` vscode extension to start container and open a terminal (you need to use the run.sh file at least once to have a container on your computer, make sure the container is created. If you use `bash run.sh` again, it will delete previous container and create a new one).

## Step4

6. If you have entered the container, you can use the following ros commands. Identify which version you're using, agilex scout or unitree go2, ros1 or ros2. Obviously, simulation will start the environment(like the robot platform and the environment), localization will provide localiztion(like SLAM, the location and map will be provided by SLAM), planning schedule a path.

* Agilex Scout -- ROS1 -- 2d planning -- ros nav stack (most classical navigation and planning framework)

```
roslaunch robot_simulation simulation1.launch
```

```
roslaunch robot_simulation localization1.launch
```

```
roslaunch robot_simulation planning1.launch
```

* Agilex Scout -- ROS1 -- 3d planning -- cmu aede (the version you test on the real scout robot)

```
roslaunch robot_simulation simulation2.launch
```

```
roslaunch robot_simulation localization2.launch
```

```
roslaunch robot_simulation planning2.launch```
```

* Unitree Go2 -- ROS2 -- 3d planning -- cmu aede (the version I demonstrate on the robot dog)

```
ros2 launch robot_simulation simulation.launch.py
```

```
ros2 launch robot_simulation localization.launch.py
```

```
ros2 launch robot_simulation planning.launch.py
```
