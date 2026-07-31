#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from ament_index_python.packages import PackageNotFoundError
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode
from launch_ros.actions import Node


def _default_rviz_config(share_dir):
    candidates = [
        _rplidar_rviz_config(),
        os.path.join(share_dir, 'rviz', 'demo.rviz'),
        os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'rviz', 'demo.rviz'),
    ]

    for config_file in candidates:
        if config_file and os.path.exists(config_file):
            return config_file

    return ''


def _rplidar_rviz_config():
    try:
        rplidar_share_dir = get_package_share_directory('rplidar_ros')
    except PackageNotFoundError:
        return ''

    return os.path.join(rplidar_share_dir, 'rviz', 'rplidar_ros.rviz')


def _rviz_node(context, *args, **kwargs):
    rviz_config = LaunchConfiguration('rviz_config').perform(context)
    rviz_arguments = ['-d', rviz_config] if rviz_config else []

    return [
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=rviz_arguments,
            output='screen',
        )
    ]


def _bluesea_driver(parameter_file):
    ros_distro = os.getenv('ROS_DISTRO', '')

    if ros_distro and ros_distro[0] <= 'e':
        return LifecycleNode(
            node_name='bluesea_node',
            node_namespace='/',
            package='bluesea2',
            node_executable='bluesea2_node',
            output='screen',
            parameters=[parameter_file],
        )

    return LifecycleNode(
        name='bluesea_node',
        namespace='/',
        package='bluesea2',
        executable='bluesea2_node',
        output='screen',
        emulate_tty=True,
        parameters=[parameter_file],
    )


def generate_launch_description():
    share_dir = get_package_share_directory('bluesea2')

    parameter_file = LaunchConfiguration('params_file')

    params_declare = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(share_dir, 'params', 'uart_lidar.yaml'),
        description='Path to the ROS 2 parameters file to use.',
    )

    rviz_config_declare = DeclareLaunchArgument(
        'rviz_config',
        default_value=_default_rviz_config(share_dir),
        description='Path to the RViz config file. Leave empty to open RViz without a config.',
    )

    return LaunchDescription([
        params_declare,
        rviz_config_declare,
        _bluesea_driver(parameter_file),
        OpaqueFunction(function=_rviz_node),
    ])
