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

"""Unit tests for Ackermann → Twist conversion."""

from __future__ import annotations

import math

from course_simulation.cmd_adapter import convert_drive


def test_straight_motion() -> None:
    result = convert_drive(1.0, 0.0, stamp_age_s=0.01)
    assert result.reason is None
    assert result.twist.linear.x == 1.0
    assert abs(result.twist.angular.z) < 1e-12


def test_turn() -> None:
    result = convert_drive(1.0, 0.4, stamp_age_s=0.01)
    assert result.reason is None
    assert result.twist.linear.x == 1.0
    expected = 1.0 * math.tan(0.4) / 0.8
    assert abs(result.twist.angular.z - expected) < 1e-9


def test_zero_speed() -> None:
    result = convert_drive(0.0, 0.3, stamp_age_s=0.01)
    assert result.reason is None
    assert result.twist.linear.x == 0.0
    assert result.twist.angular.z == 0.0


def test_speed_and_steer_clamped() -> None:
    result = convert_drive(5.0, 1.0, stamp_age_s=0.01)
    assert result.reason is None
    assert result.twist.linear.x == 1.2
    expected = 1.2 * math.tan(0.45) / 0.8
    assert abs(result.twist.angular.z - expected) < 1e-9


def test_stale_command() -> None:
    result = convert_drive(1.0, 0.0, stamp_age_s=0.3)
    assert result.reason == 'stale'
    assert result.twist.linear.x == 0.0
    assert result.twist.angular.z == 0.0


def test_non_finite_speed() -> None:
    result = convert_drive(float('nan'), 0.0, stamp_age_s=0.01)
    assert result.reason == 'non_finite'
    assert result.twist.linear.x == 0.0


def test_non_finite_steer() -> None:
    result = convert_drive(0.5, float('inf'), stamp_age_s=0.01)
    assert result.reason == 'non_finite'
    assert result.twist.angular.z == 0.0
