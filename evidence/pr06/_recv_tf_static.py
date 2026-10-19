"""Receive one /tf_static message with given durability. Exit 0 on success."""

from __future__ import annotations

import argparse
import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from tf2_msgs.msg import TFMessage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--durability',
        required=True,
        choices=('transient_local', 'volatile'),
    )
    parser.add_argument('--timeout', type=float, default=4.0)
    args = parser.parse_args()

    durability = (
        DurabilityPolicy.TRANSIENT_LOCAL
        if args.durability == 'transient_local'
        else DurabilityPolicy.VOLATILE
    )
    qos = QoSProfile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=durability,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
    )

    rclpy.init()
    node = Node('pr06_recv_tf_static')
    got: list[TFMessage] = []

    def on_msg(msg: TFMessage) -> None:
        got.append(msg)

    node.create_subscription(TFMessage, '/tf_static', on_msg, qos)
    deadline = time.time() + args.timeout
    while time.time() < deadline and not got:
        rclpy.spin_once(node, timeout_sec=0.1)

    if got:
        msg = got[0]
        print(f'transforms: {len(msg.transforms)}')
        for tf in msg.transforms[:8]:
            t = tf.transform.translation
            print(
                f'- {tf.header.frame_id} -> {tf.child_frame_id} '
                f't=({t.x:.3f},{t.y:.3f},{t.z:.3f})'
            )
        node.destroy_node()
        rclpy.shutdown()
        return 0

    print(
        f'[timeout/no message] durability={args.durability} '
        f'after {args.timeout}s',
        file=sys.stderr,
    )
    node.destroy_node()
    rclpy.shutdown()
    return 124


if __name__ == '__main__':
    raise SystemExit(main())
