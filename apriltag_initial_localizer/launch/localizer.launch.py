import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('apriltag_initial_localizer')
    config_file = os.path.join(pkg_dir, 'config', 'tag_config.yaml')

    # 1. AprilTag Detector Node
    apriltag_node = Node(
        package='apriltag_ros',
        executable='apriltag_node',
        name='apriltag_node',
        parameters=[{
            'image_transport': 'raw',
            'family': '36h11',
            'size': 0.100,  # 10cm
        }],
        remappings=[
            ('image_rect', '/image_raw'),
            ('camera_info', '/camera_info'),
            ('detections', '/apriltag_detections')
        ]
    )

    # 2. Our custom Initial Localizer calculation node
    localizer_node = Node(
        package='apriltag_initial_localizer',
        executable='initial_localizer_node',
        name='initial_localizer',
        output='screen',
        parameters=[config_file]
    )

    return LaunchDescription([
        apriltag_node,
        localizer_node
    ])