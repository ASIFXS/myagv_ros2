# myagv_ros2

ROS 2 packages for the myAGV robot, including odometry, teleop, SLAM, Nav2 navigation, and camera support.

## Software environment

This repository is intended for ROS 2 Galactic on Jetson-based systems.

```bash
ros2 galactic
Jetpack 4.6
OpenCV 4.8.0 with CUDA enabled
```

## Quick start

### 1. Clone and build

```bash
mkdir -p ~/myagv_ws/src
cd ~/myagv_ws/src
git clone -b galactic-JN <your-fork-or-upstream-url> myagv_ros2
cd ~/myagv_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

### 2. Source the workspace

```bash
source ~/.bashrc
source ~/myagv_ws/install/setup.bash
```

## Basic motion test

Use these commands to verify that the robot can receive velocity commands.

```bash
ros2 topic pub /mikey/cmd_vel geometry_msgs/msg/Twist "{linear: {x: -1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

```bash
ros2 topic pub /mikey/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

If your robot uses a different command topic, replace `/mikey/cmd_vel` with the correct topic name.

## SLAM mapping workflow

### Robot terminal

```bash
source ~/.bashrc
ros2 launch myagv_odometry myagv_active.launch.py
```

### PC terminal 1: SLAM Toolbox

```bash
ros2 launch slam_toolbox online_async_launch.py
```

### PC terminal 2: RViz2

```bash
ros2 run rviz2 rviz2
```

In RViz:
- Set the fixed frame to `map`
- Add a `Map` display from `/map`
- Add a `LaserScan` display from `/scan`
- Add a `RobotModel` display from `/robot_description`
- For the Map display, set durability to `Transient Local` and reliability to `Reliable`

### PC terminal 3: Keyboard teleop

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### PC terminal 4: Save the built map

When the map looks good:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/myagv_map
```

This creates a map file and YAML file that can be reused by Nav2.

## Nav2 navigation workflow

This repository includes the Nav2 stack for mapping-based navigation on the physical robot.

### Why this new Nav2 setup

The new flow starts the hardware driver stack first, then brings up Nav2 with the saved map. This makes the robot use:
- odometry from `myagv_odometry`
- lidar data for obstacle sensing
- a prebuilt map for global planning and localization

### Robot terminal

```bash
source ~/.bashrc
ros2 launch myagv_odometry myagv_active.launch.py
```

### PC terminal 1: RViz with Nav2 default view

```bash
ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz
```

### PC terminal 2: Start Nav2

```bash
ros2 launch nav2_bringup bringup_launch.py \
  use_sim_time:=false \
  autostart:=true \
  use_rviz:=true \
  map:=$HOME/myagv_map.yaml
```

### Optional: power the lidar before startup

If the lidar was rebooted or is not publishing data, run:

```bash
echo 20 | sudo tee /sys/class/gpio/export
echo out | sudo tee /sys/class/gpio/gpio20/direction
echo 1 | sudo tee /sys/class/gpio/gpio20/value
```

## Camera usage

### Start camera

```bash
ros2 run v4l2_camera v4l2_camera_node --ros-args -p video_device:="/dev/video0" -p camera_frame_id:="camera_link"
```

### Capture/save images

```bash
ros2 run image_view image_saver --ros-args -p save_all_image:=false -r image:=/image_raw
```

## Package overview

- [apriltag_initial_localizer](apriltag_initial_localizer) – AprilTag-based initialization/localization
- [myagv_description](myagv_description) – URDF and robot description
- [myagv_navigation2](myagv_navigation2) – Nav2-related launch and config
- [myagv_odometry](myagv_odometry) – odometry and robot base driver launch
- [slam_gmapping](slam_gmapping) – GMapping package integration
- [teleop_twist_keyboard](teleop_twist_keyboard) – keyboard teleop
- [vision_opencv](vision_opencv) – OpenCV-based vision helpers
- [ydlidar_ros2_driver](ydlidar_ros2_driver) – YDLIDAR driver integration

## Notes

- If you are using your fork, replace the clone URL with your repository URL.
- After changing the workspace, rebuild with:

```bash
cd ~/myagv_ws
colcon build
source install/setup.bash
```

