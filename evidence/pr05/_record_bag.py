"""Record /robot_a/sensor_pose (best_effort) to MCAP via rosbag2_py."""

from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from rclpy.serialization import serialize_message
from rosbag2_py import (
    ConverterOptions,
    SequentialWriter,
    StorageOptions,
    TopicMetadata,
)

try:
    from turtlesim_msgs.msg import Pose
except ImportError:
    from turtlesim.msg import Pose


class BagRecorder(Node):
    def __init__(self, writer: SequentialWriter, topic: str) -> None:
        super().__init__('pr05_bag_recorder')
        self._writer = writer
        self._topic = topic
        self._count = 0
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.create_subscription(Pose, topic, self._on_msg, qos)

    def _on_msg(self, msg: Pose) -> None:
        self._writer.write(
            self._topic,
            serialize_message(msg),
            self.get_clock().now().nanoseconds,
        )
        self._count += 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--topic', default='/robot_a/sensor_pose')
    parser.add_argument('--seconds', type=float, default=6.0)
    args = parser.parse_args()

    out = Path(args.output)
    if out.exists():
        shutil.rmtree(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    writer = SequentialWriter()
    writer.open(
        StorageOptions(uri=str(out), storage_id='mcap'),
        ConverterOptions(
            input_serialization_format='cdr',
            output_serialization_format='cdr',
        ),
    )
    writer.create_topic(
        TopicMetadata(
            id=0,
            name=args.topic,
            type='turtlesim_msgs/msg/Pose',
            serialization_format='cdr',
        ),
    )

    rclpy.init()
    node = BagRecorder(writer, args.topic)
    deadline = time.time() + args.seconds
    while time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)

    count = node._count
    node.destroy_node()
    rclpy.shutdown()
    del writer
    # metadata.yaml is flushed shortly after the writer is destroyed
    meta = out / 'metadata.yaml'
    for _ in range(20):
        if meta.is_file():
            break
        time.sleep(0.1)

    print(f'recorded {count} messages -> {out}')
    if count < 1 or not meta.is_file():
        print(f'FAIL: count={count} meta={meta.is_file()}')
        return 1
    print(f'OK metadata: {meta}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
