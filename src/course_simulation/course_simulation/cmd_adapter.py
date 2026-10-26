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

"""Ackermann /drive/safe → Twist /vehicle/gz_cmd_vel for Gazebo AckermannSteering."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import rclpy
from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from rclpy.time import Time

WHEEL_BASE_M = 0.8
MAX_SPEED_MPS = 1.2
MAX_STEER_RAD = 0.45
MAX_CMD_AGE_S = 0.25


@dataclass(frozen=True)
class CmdResult:
    twist: Twist
    reason: Optional[str]


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def convert_drive(
    speed: float,
    steering_angle: float,
    stamp_age_s: Optional[float],
) -> CmdResult:
    """Map Ackermann fields to Twist; zero + reason on invalid/stale input."""
    zero = Twist()
    if not math.isfinite(speed) or not math.isfinite(steering_angle):
        return CmdResult(zero, 'non_finite')
    if stamp_age_s is not None and stamp_age_s > MAX_CMD_AGE_S:
        return CmdResult(zero, 'stale')

    v = clamp(speed, 0.0, MAX_SPEED_MPS)
    delta = clamp(steering_angle, -MAX_STEER_RAD, MAX_STEER_RAD)
    twist = Twist()
    twist.linear.x = v
    twist.angular.z = v * math.tan(delta) / WHEEL_BASE_M
    return CmdResult(twist, None)


class CmdAdapter(Node):
    def __init__(self) -> None:
        super().__init__('cmd_adapter')
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self._pub = self.create_publisher(Twist, '/vehicle/gz_cmd_vel', qos)
        self._sub = self.create_subscription(
            AckermannDriveStamped,
            '/drive/safe',
            self._on_drive,
            qos,
        )
        self.get_logger().info('cmd_adapter ready: /drive/safe → /vehicle/gz_cmd_vel')

    def _age_s(self, stamp) -> Optional[float]:
        if stamp.sec == 0 and stamp.nanosec == 0:
            return None
        now = self.get_clock().now()
        msg_time = Time.from_msg(stamp)
        return (now - msg_time).nanoseconds * 1e-9

    def _on_drive(self, msg: AckermannDriveStamped) -> None:
        age = self._age_s(msg.header.stamp)
        result = convert_drive(
            msg.drive.speed,
            msg.drive.steering_angle,
            age,
        )
        if result.reason is not None:
            self.get_logger().warn(
                f'reject command ({result.reason}); publishing zero Twist',
                throttle_duration_sec=1.0,
            )
        self._pub.publish(result.twist)


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = CmdAdapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
