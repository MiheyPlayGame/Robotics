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

"""Patrol node: subscribe to pose, publish Twist on a relative cmd_vel."""

from __future__ import annotations

from geometry_msgs.msg import Twist
import rclpy
from patrol.command import command_from_pose
from rclpy.node import Node

try:
    from turtlesim_msgs.msg import Pose
except ImportError:  # Jazzy keeps Pose inside turtlesim
    from turtlesim.msg import Pose


class Patrol(Node):
    """Store the latest pose and publish a Twist every 0.1 s."""

    def __init__(self) -> None:
        super().__init__('patrol')
        self._last_pose: Pose | None = None
        self._pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self._on_pose,
            10,
        )
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self._timer = self.create_timer(0.1, self._on_timer)

    def _on_pose(self, msg: Pose) -> None:
        self._last_pose = msg

    def _on_timer(self) -> None:
        self._cmd_pub.publish(command_from_pose(self._last_pose))


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
