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

"""Patrol node: pose subscription, parameterized Twist timer."""

from __future__ import annotations

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from patrol.command import (
    DEFAULT_LINEAR_SPEED,
    DEFAULT_PUBLISH_HZ,
    DEFAULT_TURN_RATE,
    command_from_pose,
    timer_period_from_hz,
    validate_linear_speed,
    validate_publish_hz,
    validate_turn_rate,
)
from rclpy.node import Node
from rclpy.parameter import Parameter

try:
    from turtlesim_msgs.msg import Pose
except ImportError:  # Jazzy keeps Pose inside turtlesim
    from turtlesim.msg import Pose


class Patrol(Node):
    """Store the latest pose and publish a Twist at publish_hz."""

    def __init__(self) -> None:
        super().__init__('patrol')
        self._last_pose: Pose | None = None
        self._linear_speed = self.declare_parameter(
            'linear_speed', DEFAULT_LINEAR_SPEED
        ).value
        self._turn_rate = self.declare_parameter(
            'turn_rate', DEFAULT_TURN_RATE
        ).value
        self._publish_hz = self.declare_parameter(
            'publish_hz', DEFAULT_PUBLISH_HZ
        ).value

        self._pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self._on_pose,
            10,
        )
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self._timer = self.create_timer(
            timer_period_from_hz(self._publish_hz),
            self._on_timer,
        )

        self._on_set_handle = self.add_on_set_parameters_callback(
            self._validate_parameters
        )
        self._post_set_handle = self.add_post_set_parameters_callback(
            self._apply_parameters
        )

    def _on_pose(self, msg: Pose) -> None:
        self._last_pose = msg

    def _on_timer(self) -> None:
        self._cmd_pub.publish(
            command_from_pose(
                self._last_pose,
                linear_speed=self._linear_speed,
                turn_rate=self._turn_rate,
            )
        )

    def _validate_parameters(
        self, parameters: list[Parameter]
    ) -> SetParametersResult:
        result = SetParametersResult()
        result.successful = True
        for parameter in parameters:
            name = parameter.name
            value = parameter.value
            if name == 'linear_speed':
                reason = validate_linear_speed(value)
            elif name == 'turn_rate':
                reason = validate_turn_rate(value)
            elif name == 'publish_hz':
                reason = validate_publish_hz(value)
            else:
                continue
            if reason is not None:
                result.successful = False
                result.reason = reason
                return result
        return result

    def _apply_parameters(self, parameters: list[Parameter]) -> None:
        recreate_timer = False
        for parameter in parameters:
            if parameter.name == 'linear_speed':
                self._linear_speed = float(parameter.value)
            elif parameter.name == 'turn_rate':
                self._turn_rate = float(parameter.value)
            elif parameter.name == 'publish_hz':
                self._publish_hz = float(parameter.value)
                recreate_timer = True
        if recreate_timer:
            self._recreate_timer(self._publish_hz)

    def _recreate_timer(self, publish_hz: float) -> None:
        if self._timer is not None:
            self.destroy_timer(self._timer)
        self._timer = self.create_timer(
            timer_period_from_hz(publish_hz),
            self._on_timer,
        )


def main() -> None:
    rclpy.init()
    node = Patrol()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
