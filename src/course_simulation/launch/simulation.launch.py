# Copyright 2026 MiheyPlayGame
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Headless Gazebo + ros_gz bridge + cmd/odom adapters + robot_state_publisher."""

from __future__ import annotations

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    GroupAction,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def _launch_setup(context, *args, **kwargs):
    sim_share = get_package_share_directory('course_simulation')
    desc_share = FindPackageShare('course_description')

    world = LaunchConfiguration('world').perform(context)
    bridge_config = LaunchConfiguration('bridge_config').perform(context)
    headless = LaunchConfiguration('headless').perform(context).lower() in (
        '1', 'true', 'yes', 'on',
    )
    namespace = LaunchConfiguration('namespace').perform(context)
    use_sim_time = LaunchConfiguration('use_sim_time')

    model = PathJoinSubstitution([desc_share, 'urdf', 'vehicle.urdf.xacro'])
    robot_description = ParameterValue(Command(['xacro ', model]), value_type=str)

    models_path = os.path.join(sim_share, 'models')
    existing = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    if existing:
        gz_resource = f'{models_path}{os.pathsep}{existing}'
    else:
        gz_resource = models_path

    gz_cmd = ['gz', 'sim', '-r']
    if headless:
        gz_cmd.extend(['-s', '--headless-rendering'])
    gz_cmd.append(world)

    actions = [
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=gz_resource),
        ExecuteProcess(cmd=gz_cmd, output='screen', name='gazebo'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
            }],
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge',
            output='screen',
            parameters=[{
                'config_file': bridge_config,
                'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
            }],
        ),
    ]

    adapter_nodes = GroupAction([
        PushRosNamespace(namespace),
        Node(
            package='course_simulation',
            executable='cmd_adapter',
            name='cmd_adapter',
            output='screen',
            parameters=[{
                'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
            }],
        ),
        Node(
            package='course_simulation',
            executable='odom_adapter',
            name='odom_adapter',
            output='screen',
            parameters=[{
                'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
            }],
        ),
    ])
    actions.append(adapter_nodes)
    return actions


def generate_launch_description() -> LaunchDescription:
    sim_share = get_package_share_directory('course_simulation')
    default_world = os.path.join(sim_share, 'worlds', 'mcity-minimal.sdf')
    default_bridge = os.path.join(sim_share, 'config', 'bridge.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=default_world,
            description='Path to mcity-minimal.sdf',
        ),
        DeclareLaunchArgument(
            'bridge_config',
            default_value=default_bridge,
            description='Path to ros_gz bridge YAML',
        ),
        DeclareLaunchArgument(
            'headless',
            default_value='true',
            description='Gazebo server-only with headless rendering',
        ),
        DeclareLaunchArgument(
            'namespace',
            default_value='sim',
            description='Namespace for adapter nodes (absolute /vehicle topics unchanged)',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use /clock from simulation',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
