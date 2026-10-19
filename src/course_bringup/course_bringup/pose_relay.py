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

"""Relay /turtle1/pose to relative sensor_pose with best_effort QoS."""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy

try:
    from turtlesim_msgs.msg import Pose
except ImportError:  # Jazzy keeps Pose inside turtlesim
    from turtlesim.msg import Pose


class PoseRelay(Node):
    """Read absolute turtlesim pose and republish as a best_effort sensor."""

    def __init__(self) -> None:
        super().__init__('pose_relay')
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self._pub = self.create_publisher(Pose, 'sensor_pose', sensor_qos)
        self._sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self._on_pose,
            10,
        )
        self.get_logger().info(
            'pose_relay: /turtle1/pose -> sensor_pose (best_effort)'
        )

    def _on_pose(self, msg: Pose) -> None:
        self._pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = PoseRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
