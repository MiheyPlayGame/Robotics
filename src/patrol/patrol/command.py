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

"""Pure command selection and parameter validation for patrol."""

from __future__ import annotations

import math

from geometry_msgs.msg import Twist

DEFAULT_LINEAR_SPEED = 0.5
DEFAULT_TURN_RATE = 0.3
DEFAULT_PUBLISH_HZ = 10.0

LINEAR_SPEED_MIN = 0.0
LINEAR_SPEED_MAX = 1.0
TURN_RATE_MIN = -1.0
TURN_RATE_MAX = 1.0
PUBLISH_HZ_MIN = 1.0
PUBLISH_HZ_MAX = 30.0


def clamp_command(cmd: Twist) -> Twist:
    """Limit Twist fields used by turtlesim to the allowed ranges."""
    limited = Twist()
    limited.linear.x = min(LINEAR_SPEED_MAX, max(LINEAR_SPEED_MIN, float(cmd.linear.x)))
    limited.angular.z = min(TURN_RATE_MAX, max(TURN_RATE_MIN, float(cmd.angular.z)))
    return limited


def command_from_pose(
    pose: object | None,
    linear_speed: float = DEFAULT_LINEAR_SPEED,
    turn_rate: float = DEFAULT_TURN_RATE,
) -> Twist:
    """
    Build a Twist from the last pose and current speed parameters.

    Before any pose arrives, publish a zero command. After that, use the
    provided patrol speeds and clamp them.
    """
    cmd = Twist()
    if pose is None:
        return cmd
    cmd.linear.x = float(linear_speed)
    cmd.angular.z = float(turn_rate)
    return clamp_command(cmd)


def _reject_non_finite(value: float, name: str) -> str | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return f'{name} must be a finite number'
    if not math.isfinite(number):
        return f'{name} must be a finite number'
    return None


def validate_linear_speed(value: float) -> str | None:
    """Return None if linear_speed is allowed, otherwise a rejection reason."""
    reason = _reject_non_finite(value, 'linear_speed')
    if reason is not None:
        return reason
    number = float(value)
    if number < LINEAR_SPEED_MIN or number > LINEAR_SPEED_MAX:
        return (
            f'linear_speed must be in [{LINEAR_SPEED_MIN}, {LINEAR_SPEED_MAX}] m/s'
        )
    return None


def validate_turn_rate(value: float) -> str | None:
    """Return None if turn_rate is allowed, otherwise a rejection reason."""
    reason = _reject_non_finite(value, 'turn_rate')
    if reason is not None:
        return reason
    number = float(value)
    if number < TURN_RATE_MIN or number > TURN_RATE_MAX:
        return f'turn_rate must be in [{TURN_RATE_MIN}, {TURN_RATE_MAX}] rad/s'
    return None


def validate_publish_hz(value: float) -> str | None:
    """Return None if publish_hz is allowed, otherwise a rejection reason."""
    reason = _reject_non_finite(value, 'publish_hz')
    if reason is not None:
        return reason
    number = float(value)
    if number < PUBLISH_HZ_MIN or number > PUBLISH_HZ_MAX:
        return f'publish_hz must be in [{PUBLISH_HZ_MIN}, {PUBLISH_HZ_MAX}] Hz'
    return None


def timer_period_from_hz(publish_hz: float) -> float:
    """Convert a validated publish frequency to a timer period in seconds."""
    return 1.0 / float(publish_hz)
