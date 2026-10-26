#!/usr/bin/env python3
"""Probe sensor rates and publish a short /drive/safe command."""

from __future__ import annotations

import time

import rclpy
from ackermann_msgs.msg import AckermannDriveStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import (
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
    qos_profile_sensor_data,
)
from sensor_msgs.msg import Image, Imu, LaserScan


def main() -> None:
    rclpy.init()
    node = Node('pr07_probe')
    node.set_parameters([Parameter('use_sim_time', Parameter.Type.BOOL, True)])
    counts = {'cam': 0, 'scan': 0, 'imu': 0, 'odom': 0}
    frames: dict[str, str] = {}
    qos_rel = QoSProfile(
        reliability=ReliabilityPolicy.RELIABLE,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
    )

    def make_cb(key: str):
        def cb(msg) -> None:
            counts[key] += 1
            if key not in frames:
                frames[key] = msg.header.frame_id
                if hasattr(msg, 'child_frame_id'):
                    frames[f'{key}_child'] = msg.child_frame_id
        return cb

    node.create_subscription(
        Image, '/vehicle/camera/image_raw', make_cb('cam'), qos_profile_sensor_data
    )
    node.create_subscription(
        LaserScan, '/vehicle/scan', make_cb('scan'), qos_profile_sensor_data
    )
    node.create_subscription(
        Imu, '/vehicle/imu', make_cb('imu'), qos_profile_sensor_data
    )
    node.create_subscription(
        Odometry, '/vehicle/odom', make_cb('odom'), qos_rel
    )

    end = time.time() + 3.0
    while time.time() < end:
        rclpy.spin_once(node, timeout_sec=0.1)

    pub = node.create_publisher(AckermannDriveStamped, '/drive/safe', qos_rel)
    for _ in range(40):
        msg = AckermannDriveStamped()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.drive.speed = 0.8
        msg.drive.steering_angle = 0.0
        pub.publish(msg)
        rclpy.spin_once(node, timeout_sec=0.05)
        time.sleep(0.05)

    for key in counts:
        counts[key] = 0
    t0 = time.time()
    while time.time() - t0 < 5.0:
        rclpy.spin_once(node, timeout_sec=0.05)
    dt = max(time.time() - t0, 1e-6)
    hz = {k: round(counts[k] / dt, 2) for k in counts}
    print('HZ', hz)
    print('FRAMES', frames)

    stop = AckermannDriveStamped()
    stop.header.stamp = node.get_clock().now().to_msg()
    pub.publish(stop)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
