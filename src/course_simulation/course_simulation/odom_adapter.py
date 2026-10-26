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

"""Normalize Gazebo odometry frames and publish odom→base_link tf."""

from __future__ import annotations

import math
from typing import Optional

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from tf2_ros import TransformBroadcaster

SRC_ODOM_FRAME = 'course_ackermann/odom'
SRC_BASE_FRAME = 'course_ackermann/base_link'
DST_ODOM_FRAME = 'odom'
DST_BASE_FRAME = 'base_link'


def _finite_pose_twist(msg: Odometry) -> bool:
    p = msg.pose.pose.position
    o = msg.pose.pose.orientation
    t = msg.twist.twist
    values = (
        p.x, p.y, p.z,
        o.x, o.y, o.z, o.w,
        t.linear.x, t.linear.y, t.linear.z,
        t.angular.x, t.angular.y, t.angular.z,
    )
    return all(math.isfinite(v) for v in values)


def normalize_odometry(msg: Odometry) -> Optional[Odometry]:
    """Rename course_ackermann/* frames; reject other prefixes or non-finite values."""
    if msg.header.frame_id != SRC_ODOM_FRAME:
        return None
    if msg.child_frame_id != SRC_BASE_FRAME:
        return None
    if not _finite_pose_twist(msg):
        return None

    out = Odometry()
    out.header = msg.header
    out.header.frame_id = DST_ODOM_FRAME
    out.child_frame_id = DST_BASE_FRAME
    out.pose = msg.pose
    out.twist = msg.twist
    return out


class OdomAdapter(Node):
    def __init__(self) -> None:
        super().__init__('odom_adapter')
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self._pub = self.create_publisher(Odometry, '/vehicle/odom', qos)
        self._tf = TransformBroadcaster(self)
        self._sub = self.create_subscription(
            Odometry,
            '/vehicle/odom_gz',
            self._on_odom,
            qos,
        )
        self.get_logger().info(
            'odom_adapter ready: /vehicle/odom_gz → /vehicle/odom + tf odom→base_link'
        )

    def _on_odom(self, msg: Odometry) -> None:
        out = normalize_odometry(msg)
        if out is None:
            self.get_logger().warn(
                f'reject odom frames={msg.header.frame_id!r}/{msg.child_frame_id!r}',
                throttle_duration_sec=1.0,
            )
            return
        self._pub.publish(out)
        tf = TransformStamped()
        tf.header = out.header
        tf.child_frame_id = out.child_frame_id
        tf.transform.translation.x = out.pose.pose.position.x
        tf.transform.translation.y = out.pose.pose.position.y
        tf.transform.translation.z = out.pose.pose.position.z
        tf.transform.rotation = out.pose.pose.orientation
        self._tf.sendTransform(tf)


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = OdomAdapter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
