#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
    serial_baudrate = LaunchConfiguration('serial_baudrate', default='460800')
    frame_id = LaunchConfiguration('frame_id', default='laser')
    topic_name = LaunchConfiguration('topic_name', default='scan')
    angle_offset_degrees = LaunchConfiguration('angle_offset_degrees', default='0.0')
    reverse_scan = LaunchConfiguration('reverse_scan', default='false')

    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value=serial_port),
        DeclareLaunchArgument('serial_baudrate', default_value=serial_baudrate),
        DeclareLaunchArgument('frame_id', default_value=frame_id),
        DeclareLaunchArgument('topic_name', default_value=topic_name),
        DeclareLaunchArgument('angle_offset_degrees', default_value=angle_offset_degrees),
        DeclareLaunchArgument('reverse_scan', default_value=reverse_scan),
        Node(
            package='lidar_tester',
            executable='pudu_lidar_node.py',
            name='pudu_lidar_node',
            parameters=[{
                'serial_port': serial_port,
                'serial_baudrate': serial_baudrate,
                'frame_id': frame_id,
                'topic_name': topic_name,
                'angle_offset_degrees': angle_offset_degrees,
                'reverse_scan': reverse_scan,
            }],
            output='screen',
        ),
    ])
