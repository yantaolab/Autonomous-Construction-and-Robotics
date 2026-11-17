FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y lsb-release curl wget ca-certificates git gnupg gdb

RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc \
      | gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros/ubuntu focal main" \
      > /etc/apt/sources.list.d/ros-latest.list

# Gazebo 11 源：这个 .gpg 本身就是二进制，直接下载不用 dearmor
RUN curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
      -o /usr/share/keyrings/gazebo.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/gazebo.gpg] \
http://packages.osrfoundation.org/gazebo/ubuntu-stable focal main" \
      > /etc/apt/sources.list.d/gazebo.list

RUN apt-get update && apt-get install -y ros-noetic-desktop-full

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

RUN apt-get update && apt-get install -y python3-pip python-is-python3 python3-catkin-tools

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    xfce4 \
    xfce4-terminal \
    dbus-x11 \
    x11-utils \
    mesa-utils \
    libgl1-mesa-dri

# RUN groupadd -g 1000 user && \
#     useradd -m -u 1000 -g 1000 -s /bin/bash user && \
#     echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# WORKDIR /home/user



#base
# RUN git clone https://github.com/osrf/gazebo_models.git gazebo_models






# USER user
# RUN mkdir -p /home/user/dependencies_catkin_ws/src && \
#     cd /home/user/dependencies_catkin_ws && \
#     git clone https://bitbucket.org/DataspeedInc/velodyne_simulator.git --depth 1 -b master /home/user/dependencies_catkin_ws/src/velodyne_simulator && \
#     git clone https://github.com/agilexrobotics/ugv_gazebo_sim.git --depth 1 -b master /home/user/dependencies_catkin_ws/src/ugv_gazebo_sim && \
#     git clone https://github.com/WenyuLWY/autonomous_exploration_development_environment.git --depth 1 -b main /home/user/dependencies_catkin_ws/src/autonomous_exploration_development_environment && \
#     bash -c "source /opt/ros/noetic/setup.bash && catkin build"

RUN mkdir -p /root/catkin_ws/src && \
    cd /root/catkin_ws && \
    git clone https://bitbucket.org/DataspeedInc/velodyne_simulator.git --depth 1 -b master /root/catkin_ws/src/velodyne_simulator && \
    git clone https://github.com/agilexrobotics/ugv_gazebo_sim.git --depth 1 -b master /root/catkin_ws/src/ugv_gazebo_sim && \
    git clone https://github.com/WenyuLWY/autonomous_exploration_development_environment.git --depth 1 -b main /root/catkin_ws/src/autonomous_exploration_development_environment && \
    git clone https://github.com/WenyuLWY/robot_simulation.git --depth 1 -b agilex_scout /root/catkin_ws/src/robot_simulation && \
    bash -c "source /opt/ros/noetic/setup.bash && catkin build"

# RUN apt-get update && apt-get install -y ros-noetic-husky*
    # echo "CORES=\$(nproc)" >> /home/user/start.sh && \s
    # echo "JOBS=\$((CORES>1 ? CORES-1 : 1))" >> /home/user/start.sh && \
    # echo "catkin build -j\$JOBS" >> /home/user/start.sh && \

RUN echo "export GAZEBO_MODEL_PATH=/root/gazebo_models:$GAZEBO_MODEL_PATH" >> /root/.bashrc
RUN echo "export DISABLE_ROS1_EOL_WARNINGS=1" >> /root/.bashrc
RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc   
# RUN echo "source /root/dependencies_catkin_ws/devel/setup.bash" >> /root/.bashrc
RUN echo "source /root/catkin_ws/devel/setup.bash" >> /root/.bashrc

RUN mkdir -p /tmp/runtime-root && chmod 700 /tmp/runtime-root

# RUN echo "#!/bin/bash" > /root/start.sh && \
#     echo "source /opt/ros/noetic/setup.bash" >> /root/start.sh && \
#     echo "cd /root/catkin_ws" >> /root/start.sh && \
#     echo "catkin build" >> /root/start.sh && \
#     echo "source /root/catkin_ws/devel/setup.bash" >> /root/start.sh && \
#     echo "export DISABLE_ROS1_EOL_WARNINGS=1" >> /root/start.sh && \
#     # echo "roslaunch robot_simulation simulation2.launch" >> /root/start.sh && \
#     echo "exec \"\$@\"" >> /root/start.sh && \
#     chmod +x /root/start.sh

    

# ENTRYPOINT ["/root/start.sh"]

# CMD ["/bin/bash"]

# Display settings
ENV DISPLAY=:1
ENV QT_X11_NO_MITSHM=1
ENV LIBGL_ALWAYS_SOFTWARE=1

USER root
# Add VNC startup script
COPY start-vnc.sh /root/start-vnc.sh
RUN chmod +x /root/start-vnc.sh
# Initialize ROS for interactive Bash sessions
# noVNC
EXPOSE 6080
ENTRYPOINT ["/root/start-vnc.sh"]
CMD ["sleep", "infinity"]