# myagv_ros2
ROS2 packages for myAGV

# Checklist

- [ ] myagv_description
- [ ] myagv_navigation2
- [x] myagv_teleop
- [x] myagv_odometry
- [ ] myagv_cartographer
- [ ] navigation2
- [x] ydlidar_ros2_driver
- [ ] Gazebo simulation

# Installation

You need to have previously installed ROS2.

Create workspace and clone the repository.

```bash
git clone -b galactic-JN https://github.com/elephantrobotics/myagv_ros2.git myagv_ros2/src
```

Install dependencies
```
cd ~/myagv_ros2

rosdep install --from-paths src --ignore-src -r -y
```
```
sudo apt install ros-galactic-bondcpp \
    ros-galactic-test-msgs* \
    ros-galactic-behaviortree-cpp-v3* \
    ros-galactic-ompl \
    ros-galactic-joint-state-publisher \
    ros-galactic-rqt-tf-tree \
    ros-galactic-diagnostic-updater \
    ros-galactic-camera-info-manager -y
```

Build workspace

```
cd ~/myagv_ros2

colcon build --symlink-install
```

Setup the workspace
```
source ~/myagv_ros2/install/local_setup.bash
```

# Update to new version
```
cd ~/myagv_ros2/src

git pull

cd ..

colcon build --symlink-install
```

