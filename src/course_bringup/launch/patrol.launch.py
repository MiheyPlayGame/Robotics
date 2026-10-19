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

"""Bring up turtlesim + namespaced patrol/pose_relay/qos_probe (+ optional bag)."""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    LogInfo,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')
    use_turtlesim = LaunchConfiguration('use_turtlesim')

    sensor_topic = PythonExpression(
        ["'/' + '", namespace, "' + '/sensor_pose'"]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='robot_a',
            description='Namespace for patrol, pose_relay, and qos_probe',
        ),
        DeclareLaunchArgument(
            'record',
            default_value='false',
            description='If true, record /<namespace>/sensor_pose to MCAP',
        ),
        DeclareLaunchArgument(
            'bag_dir',
            default_value='evidence/pr05/bag',
            description='Output directory for ros2 bag record -o',
        ),
        DeclareLaunchArgument(
            'subscriber_reliability',
            default_value='reliable',
            description='QoS reliability for qos_probe (reliable|best_effort)',
        ),
        DeclareLaunchArgument(
            'use_turtlesim',
            default_value='true',
            description='If true, start global turtlesim_node',
        ),
        LogInfo(msg=['PR05 launch namespace=', namespace]),
        LogInfo(msg=['PR05 launch record=', record, ' bag_dir=', bag_dir]),
        LogInfo(
            msg=[
                'PR05 launch subscriber_reliability=',
                subscriber_reliability,
            ]
        ),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
            condition=IfCondition(use_turtlesim),
        ),
        Node(
            package='patrol',
            executable='patrol',
            name='patrol',
            namespace=namespace,
            output='screen',
            remappings=[('cmd_vel', '/turtle1/cmd_vel')],
        ),
        Node(
            package='course_bringup',
            executable='pose_relay',
            name='pose_relay',
            namespace=namespace,
            output='screen',
        ),
        Node(
            package='course_bringup',
            executable='qos_probe',
            name='qos_probe',
            namespace=namespace,
            output='screen',
            parameters=[{
                'reliability': ParameterValue(
                    subscriber_reliability,
                    value_type=str,
                ),
            }],
        ),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '-s', 'mcap',
                '-o', bag_dir,
                '--topics', sensor_topic,
            ],
            output='screen',
            condition=IfCondition(record),
        ),
    ])
