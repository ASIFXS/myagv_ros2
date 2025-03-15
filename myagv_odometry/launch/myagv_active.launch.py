import os
from launch import LaunchDescription
from launch_ros.actions import Node
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
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_laser_link',
            arguments=['0.065', '0.0', '0.08', '3.14159265', '0.0', '0.0', '/base_footprint', '/laser_frame']
        ),

        Node(
            package='robot_pose_ekf',
            executable='robot_pose_ekf',
            name='robot_pose_ekf',
            output='screen',
            parameters=[
                {'output_frame': 'odom'},
                {'base_footprint_frame': 'base_footprint'},
                {'freq': 30.0},
                {'sensor_timeout': 2.0},
                {'odom_used': True},
                {'odom_data': 'odom'},
                {'imu_used': True},
                {'vo_used': False}
            ],
            remappings=[('imu_data', 'imu')]
        ),

        Node(
            package='ydlidar_ros_driver',
            executable='X2',
            name='X2_launch'
        )

    ])
