#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    rplidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rplidar_ros'),
                'launch',
                'custom_a2m7_launch.py',
            )
        )
    )

    lidar_tester_node = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='lidar_tester',
                executable='lidar_a2m7_range_tester.py',
                name='lidar_a2m7_range_tester',
                output='screen',
            )
        ],
    )

    return LaunchDescription([
        rplidar_launch,
        lidar_tester_node,
    ])
