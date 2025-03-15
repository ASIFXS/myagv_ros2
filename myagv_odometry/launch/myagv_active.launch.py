import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.substitutions import ThisLaunchFileDir
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    return LaunchDescription([

        Node(
            package='myagv_odometry',
            executable='myagv_odometry_node',
            name='myagv_odometry_node',
            output='screen'
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher'
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            arguments=[os.path.join(get_package_share_directory('myagv_description'),'urdf','myAGV.urdf')]
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base2camera_link',
            arguments=['0.13', '0', '0.131', '0', '0', '0', '/base_footprint', '/camera_link']
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base2imu_link',
            arguments=['0', '0', '0', '0', '3.14159', '3.14159', '/base_footprint', '/imu_link']
        ),

        Node(
            package='ydlidar_ros_driver',
            executable='X2',
            name='X2_launch'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('ydlidar_ros2_driver'),'launch'),
                'ydlidar_launch.py'])
        )
    ])
