"""Receive one /robot_a/sensor_pose with the given reliability. Exit 0 on success."""

from __future__ import annotations

import argparse
import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy

try:
    from turtlesim_msgs.msg import Pose
except ImportError:
    from turtlesim.msg import Pose


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--reliability', required=True, choices=('reliable', 'best_effort'))
    parser.add_argument('--timeout', type=float, default=5.0)
    args = parser.parse_args()

    policy = (
        ReliabilityPolicy.BEST_EFFORT
        if args.reliability == 'best_effort'
        else ReliabilityPolicy.RELIABLE
    )
    qos = QoSProfile(
        reliability=policy,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
    )

    rclpy.init()
    node = Node('pr05_recv_once')
    got: list[Pose] = []

    def on_msg(msg: Pose) -> None:
        got.append(msg)

    node.create_subscription(Pose, '/robot_a/sensor_pose', on_msg, qos)
    deadline = time.time() + args.timeout
    while time.time() < deadline and not got:
        rclpy.spin_once(node, timeout_sec=0.1)

    if got:
        msg = got[0]
        print(f'x: {msg.x}')
        print(f'y: {msg.y}')
        print(f'theta: {msg.theta}')
        print('---')
        node.destroy_node()
        rclpy.shutdown()
        return 0

    print(
        f'[timeout/no message] reliability={args.reliability} '
        f'after {args.timeout}s',
        file=sys.stderr,
    )
    node.destroy_node()
    rclpy.shutdown()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
