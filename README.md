# myagv_ros2
ROS2 packages for myAGV

# Checklist

- [ ] myagv_description
- [ ] myagv_navigation2
- [ ] myagv_teleop
- [ ] myagv_odometry
- [ ] myagv_cartographer
- [ ] navigation2
- [ ] ydlidar_ros2_driver
- [ ] Gazebo simulation

# Installation

You need to have previously installed ROS2.

Create workspace and clone the repository.

```bash
git clone -b galactic-JN https://github.com/elephantrobotics/myagv_ros2.git myagv_ros2/src
```

Install dependencies and build workspace
```
cd ~/myagv_ros2
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y
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

