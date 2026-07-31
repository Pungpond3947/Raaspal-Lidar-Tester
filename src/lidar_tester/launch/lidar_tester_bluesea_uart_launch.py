#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    bluesea_uart_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('bluesea2'),
                'launch',
                'view_uart_lidar.launch.py',
            )
        )
    )

    lidar_tester_node = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='lidar_tester',
                executable='bluesea_uart_range_tester.py',
                name='bluesea_uart_range_tester',
                output='screen',
            )
        ],
    )

    return LaunchDescription([
        bluesea_uart_launch,
        lidar_tester_node,
    ])
