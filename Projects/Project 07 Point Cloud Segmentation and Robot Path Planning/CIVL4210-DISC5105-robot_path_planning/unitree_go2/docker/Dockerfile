FROM osrf/ros:humble-desktop-full

ARG DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1000 user && \
    useradd -m -u 1000 -g 1000 -s /bin/bash user && \
    echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers


WORKDIR /home/user
# WORKDIR /root

#gazebo

RUN git clone https://github.com/osrf/gazebo_models.git gazebo_models
RUN apt-get update && apt-get install -y python-is-python3 python3-pip unzip xterm
RUN pip install gdown

#go2_nav_ros2
RUN apt-get update && apt-get install -y ros-humble-gazebo-ros \
                                        ros-humble-gazebo-ros-pkgs \
                                        ros-humble-gazebo-dev \
                                        ros-humble-gazebo-plugins \
                                        ros-humble-gazebo-ros2-control \
                                        ros-humble-ros2-control \
                                        ros-humble-ros2-controllers \
                                        ros-humble-robot-localization \
                                        ros-humble-navigation2 \
                                        ros-humble-nav2-bringup \
                                        ros-humble-xacro \
                                        ros-humble-velodyne \
                                        ros-humble-velodyne-gazebo-plugins \
                                        ros-humble-velodyne-description

# autonomy_stack_go2
RUN apt-get update && apt-get install -y libusb-dev ros-humble-perception-pcl ros-humble-sensor-msgs-py ros-humble-tf-transformations ros-humble-joy ros-humble-rmw-cyclonedds-cpp ros-humble-rosidl-generator-dds-idl python3-colcon-common-extensions python-is-python3 
RUN pip install transforms3d pyyaml
RUN apt-get update && apt-get install -y ros-humble-rqt* ros-humble-tf2-ros ros-humble-tf2-sensor-msgs ros-humble-pointcloud-to-laserscan ros-humble-tf-transformations ros-humble-tf2-sensor-msgs

RUN apt-get update && apt-get install -y ros-humble-rtabmap*

USER user
RUN mkdir -p /home/user/ros2_ws/src && \
    git clone https://github.com/WenyuLWY/unitree-go2-ros2.git --depth 1 -b humble /home/user/ros2_ws/src/unitree-go2-ros2 && \
    git clone https://github.com/WenyuLWY/autonomy_stack_go2.git --depth 1 -b foxy-humble /home/user/ros2_ws/src/autonomy_stack_go2 && \
    git clone https://github.com/MOGI-ROS/mogi_trajectory_server.git --depth 1 -b main /home/user/ros2_ws/src/mogi_trajectory_server && \
    git clone https://github.com/WenyuLWY/robot_simulation.git --depth 1 -b unitree_go2 /home/user/ros2_ws/src/robot_simulation && \
    cd /home/user/ros2_ws && \
    bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release" && \
    echo "source /home/user/ros2_ws/install/setup.bash" >> /home/user/.bashrc

# RUN mkdir -p /home/user/ros2_ws/src && \
#     cd /home/user/ros2_ws && \
#     bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release" && \
#     echo "source /home/user/ros2_ws/install/setup.bash" >> /home/user/.bashrc

RUN echo "source /opt/ros/humble/setup.bash" >> /home/user/.bashrc   
RUN echo "export GAZEBO_MODEL_PATH=/home/user/gazebo_models:$GAZEBO_MODEL_PATH" >> /home/user/.bashrc


RUN echo "#!/bin/bash" > /home/user/start.sh && \
    echo "cd /home/user/ros2_ws" >> /home/user/start.sh && \
    echo "source /opt/ros/humble/setup.bash" >> /home/user/start.sh && \
    # echo "colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release" >> /home/user/start.sh && \
    echo "source /home/user/ros2_ws/install/setup.bash" >> /home/user/start.sh && \
    # echo "ros2 launch robot_simulation simulation.launch.py" >> /root/start.sh && \
    echo "exec \"\$@\"" >> /home/user/start.sh && \
    chmod +x /home/user/start.sh

ENTRYPOINT ["/home/user/start.sh"]

CMD ["/bin/bash"]