#!/usr/bin/env python3
"""Publish a fresh /drive/safe command for a fixed wall-clock duration."""

from __future__ import annotations

import time

import rclpy
from ackermann_msgs.msg import AckermannDriveStamped
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy


def main() -> None:
    rclpy.init()
    node = Node('drive_src')
    node.set_parameters([Parameter('use_sim_time', Parameter.Type.BOOL, True)])
    pub = node.create_publisher(
        AckermannDriveStamped,
        '/drive/safe',
        QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        ),
    )
    end = time.time() + 55.0
    while time.time() < end:
        msg = AckermannDriveStamped()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.drive.speed = 0.6
        msg.drive.steering_angle = 0.1
        pub.publish(msg)
        rclpy.spin_once(node, timeout_sec=0.05)
        time.sleep(0.1)
    stop = AckermannDriveStamped()
    stop.header.stamp = node.get_clock().now().to_msg()
    pub.publish(stop)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
