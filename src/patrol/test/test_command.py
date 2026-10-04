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

"""Unit tests for pure Twist selection and parameter validation."""

import math
from types import SimpleNamespace

from geometry_msgs.msg import Twist

from patrol.command import (
    DEFAULT_LINEAR_SPEED,
    DEFAULT_TURN_RATE,
    TURN_RATE_MAX,
    clamp_command,
    command_from_pose,
    timer_period_from_hz,
    validate_linear_speed,
    validate_publish_hz,
    validate_turn_rate,
)


def test_command_without_pose_is_zero() -> None:
    cmd = command_from_pose(None)
    assert cmd.linear.x == 0.0
    assert cmd.angular.z == 0.0


def test_command_with_pose_uses_patrol_speeds() -> None:
    pose = SimpleNamespace(x=1.0, y=2.0, theta=0.5)
    cmd = command_from_pose(pose)
    assert cmd.linear.x == DEFAULT_LINEAR_SPEED
    assert cmd.angular.z == DEFAULT_TURN_RATE


def test_command_with_pose_uses_custom_speeds() -> None:
    pose = SimpleNamespace(x=1.0, y=2.0, theta=0.5)
    cmd = command_from_pose(pose, linear_speed=0.2, turn_rate=-0.4)
    assert cmd.linear.x == 0.2
    assert cmd.angular.z == -0.4


def test_clamp_command_limits_angular() -> None:
    raw = Twist()
    raw.linear.x = 0.4
    raw.angular.z = 5.0
    limited = clamp_command(raw)
    assert limited.linear.x == 0.4
    assert limited.angular.z == TURN_RATE_MAX


def test_publish_hz_change_10_to_5_is_accepted() -> None:
    assert validate_publish_hz(10.0) is None
    assert validate_publish_hz(5.0) is None
    assert timer_period_from_hz(5.0) == 0.2


def test_publish_hz_zero_is_rejected() -> None:
    assert validate_publish_hz(0.0) is not None


def test_publish_hz_negative_is_rejected() -> None:
    assert validate_publish_hz(-1.0) is not None


def test_publish_hz_nan_is_rejected() -> None:
    assert validate_publish_hz(float('nan')) is not None
    assert validate_publish_hz(math.nan) is not None


def test_linear_speed_and_turn_rate_bounds() -> None:
    assert validate_linear_speed(0.0) is None
    assert validate_linear_speed(1.0) is None
    assert validate_linear_speed(-0.1) is not None
    assert validate_linear_speed(1.1) is not None
    assert validate_turn_rate(-1.0) is None
    assert validate_turn_rate(1.0) is None
    assert validate_turn_rate(-1.1) is not None
    assert validate_turn_rate(float('inf')) is not None
