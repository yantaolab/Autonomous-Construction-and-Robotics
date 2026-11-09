FROM osrf/ros:noetic-desktop-full

ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1000 user && \
    useradd -m -u 1000 -g 1000 -s /bin/bash user && \
    echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /home/user



#base
RUN apt-get update && apt-get install -y lsb-release curl wget ca-certificates git gnupg gdb
RUN apt-get update && apt-get install -y python3-pip python-is-python3 python3-catkin-tools
RUN git clone https://github.com/osrf/gazebo_models.git gazebo_models

#develop
RUN apt-get update && apt-get install -y ros-noetic-ros-control ros-noetic-ros-controllers \
                                        ros-noetic-hector-trajectory-server \
                                        ros-noetic-tf2-sensor-msgs ros-noetic-geographic-msgs \
                                        ros-noetic-hector-gazebo-plugins \
                                        ros-noetic-pointcloud-to-laserscan ros-noetic-point-cloud2-filters \
                                        ros-noetic-navigation ros-noetic-teb-local-planner \
                                        ros-noetic-octomap*

#autonomous_exploration_development_environment
RUN apt-get update && apt-get install -y libusb-dev
#RTABMAP
RUN apt-get update && apt-get install -y ros-noetic-rtabmap* ros-noetic-libpointmatcher ros-noetic-libg2o ros-noetic-gtsam






USER user
# RUN mkdir -p /home/user/dependencies_catkin_ws/src && \
#     cd /home/user/dependencies_catkin_ws && \
#     git clone https://bitbucket.org/DataspeedInc/velodyne_simulator.git --depth 1 -b master /home/user/dependencies_catkin_ws/src/velodyne_simulator && \
#     git clone https://github.com/agilexrobotics/ugv_gazebo_sim.git --depth 1 -b master /home/user/dependencies_catkin_ws/src/ugv_gazebo_sim && \
#     git clone https://github.com/WenyuLWY/autonomous_exploration_development_environment.git --depth 1 -b main /home/user/dependencies_catkin_ws/src/autonomous_exploration_development_environment && \
#     bash -c "source /opt/ros/noetic/setup.bash && catkin build"

RUN mkdir -p /home/user/catkin_ws/src && \
    cd /home/user/catkin_ws && \
    git clone https://bitbucket.org/DataspeedInc/velodyne_simulator.git --depth 1 -b master /home/user/catkin_ws/src/velodyne_simulator && \
    git clone https://github.com/agilexrobotics/ugv_gazebo_sim.git --depth 1 -b master /home/user/catkin_ws/src/ugv_gazebo_sim && \
    git clone https://github.com/WenyuLWY/autonomous_exploration_development_environment.git --depth 1 -b main /home/user/catkin_ws/src/autonomous_exploration_development_environment && \
    git clone https://github.com/WenyuLWY/robot_simulation.git --depth 1 -b agilex_scout /home/user/catkin_ws/src/robot_simulation && \
    bash -c "source /opt/ros/noetic/setup.bash && catkin build"

# RUN apt-get update && apt-get install -y ros-noetic-husky*
    # echo "CORES=\$(nproc)" >> /home/user/start.sh && \s
    # echo "JOBS=\$((CORES>1 ? CORES-1 : 1))" >> /home/user/start.sh && \
    # echo "catkin build -j\$JOBS" >> /home/user/start.sh && \

RUN echo "export GAZEBO_MODEL_PATH=/home/user/gazebo_models:$GAZEBO_MODEL_PATH" >> /home/user/.bashrc
RUN echo "export DISABLE_ROS1_EOL_WARNINGS=1" >> /home/user/.bashrc
RUN echo "source /opt/ros/noetic/setup.bash" >> /home/user/.bashrc   
# RUN echo "source /home/user/dependencies_catkin_ws/devel/setup.bash" >> /home/user/.bashrc
RUN echo "source /home/user/catkin_ws/devel/setup.bash" >> /home/user/.bashrc

RUN mkdir -p /tmp/runtime-root && chmod 700 /tmp/runtime-root

RUN echo "#!/bin/bash" > /home/user/start.sh && \
    echo "source /opt/ros/noetic/setup.bash" >> /home/user/start.sh && \
    echo "cd /home/user/catkin_ws" >> /home/user/start.sh && \
    echo "catkin build" >> /home/user/start.sh && \
    echo "source /home/user/catkin_ws/devel/setup.bash" >> /home/user/start.sh && \
    echo "export DISABLE_ROS1_EOL_WARNINGS=1" >> /home/user/start.sh && \
    # echo "roslaunch robot_simulation simulation2.launch" >> /home/user/start.sh && \
    echo "exec \"\$@\"" >> /home/user/start.sh && \
    chmod +x /home/user/start.sh

    

ENTRYPOINT ["/home/user/start.sh"]

CMD ["/bin/bash"]
