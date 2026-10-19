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

"""Subscribe to sensor_pose with configurable reliability for QoS demos."""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy

try:
    from turtlesim_msgs.msg import Pose
except ImportError:  # Jazzy keeps Pose inside turtlesim
    from turtlesim.msg import Pose


def reliability_from_name(name: str) -> ReliabilityPolicy:
    """Map launch/param string to a ReliabilityPolicy."""
    normalized = name.strip().lower().replace('-', '_')
    if normalized in {'best_effort', 'besteffort'}:
        return ReliabilityPolicy.BEST_EFFORT
    if normalized == 'reliable':
        return ReliabilityPolicy.RELIABLE
    raise ValueError(f'unsupported reliability: {name!r}')


class QosProbe(Node):
    """Count arrivals on relative sensor_pose under the requested QoS."""

    def __init__(self) -> None:
        super().__init__('qos_probe')
        reliability_name = str(
            self.declare_parameter('reliability', 'reliable').value
        )
        policy = reliability_from_name(reliability_name)
        qos = QoSProfile(
            reliability=policy,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self._count = 0
        self._sub = self.create_subscription(
            Pose,
            'sensor_pose',
            self._on_pose,
            qos,
        )
        self.get_logger().info(
            f'qos_probe: sensor_pose reliability={reliability_name}'
        )

    def _on_pose(self, _msg: Pose) -> None:
        self._count += 1
        if self._count == 1 or self._count % 50 == 0:
            self.get_logger().info(f'received sensor_pose #{self._count}')


def main() -> None:
    rclpy.init()
    node = QosProbe()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
