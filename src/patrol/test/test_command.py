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

"""Unit tests for pure Twist selection."""

from types import SimpleNamespace

from geometry_msgs.msg import Twist

from patrol.command import (
    ANGULAR_Z,
    ANGULAR_Z_MAX,
    LINEAR_X,
    clamp_command,
    command_from_pose,
)


def test_command_without_pose_is_zero() -> None:
    cmd = command_from_pose(None)
    assert cmd.linear.x == 0.0
    assert cmd.angular.z == 0.0


def test_command_with_pose_uses_patrol_speeds() -> None:
    pose = SimpleNamespace(x=1.0, y=2.0, theta=0.5)
    cmd = command_from_pose(pose)
    assert cmd.linear.x == LINEAR_X
    assert cmd.angular.z == ANGULAR_Z


def test_clamp_command_limits_angular() -> None:
    raw = Twist()
    raw.linear.x = 0.4
    raw.angular.z = 5.0
    limited = clamp_command(raw)
    assert limited.linear.x == 0.4
    assert limited.angular.z == ANGULAR_Z_MAX
