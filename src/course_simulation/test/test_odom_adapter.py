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

"""Unit tests for odometry frame normalization."""

from __future__ import annotations

from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from std_msgs.msg import Header

from course_simulation.odom_adapter import normalize_odometry


def _make_odom(
    frame_id: str = 'course_ackermann/odom',
    child: str = 'course_ackermann/base_link',
    x: float = 1.5,
) -> Odometry:
    msg = Odometry()
    msg.header = Header(stamp=Time(sec=3, nanosec=500000000), frame_id=frame_id)
    msg.child_frame_id = child
    msg.pose.pose.position.x = x
    msg.pose.pose.orientation.w = 1.0
    return msg


def test_normalize_frames_and_preserve_stamp() -> None:
    src = _make_odom()
    out = normalize_odometry(src)
    assert out is not None
    assert out.header.frame_id == 'odom'
    assert out.child_frame_id == 'base_link'
    assert out.header.stamp.sec == 3
    assert out.header.stamp.nanosec == 500000000
    assert out.pose.pose.position.x == 1.5


def test_reject_wrong_frames() -> None:
    assert normalize_odometry(_make_odom(frame_id='odom')) is None
    assert normalize_odometry(_make_odom(child='base_link')) is None


def test_reject_non_finite() -> None:
    msg = _make_odom()
    msg.pose.pose.position.x = float('nan')
    assert normalize_odometry(msg) is None
