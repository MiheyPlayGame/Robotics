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

"""Pure command selection from the last known turtle pose."""

from __future__ import annotations

from geometry_msgs.msg import Twist

LINEAR_X = 0.5
ANGULAR_Z = 0.3
LINEAR_X_MIN = 0.0
LINEAR_X_MAX = 0.5
ANGULAR_Z_MIN = -1.0
ANGULAR_Z_MAX = 1.0


def clamp_command(cmd: Twist) -> Twist:
    """Limit Twist fields used by turtlesim to a safe range."""
    limited = Twist()
    limited.linear.x = min(LINEAR_X_MAX, max(LINEAR_X_MIN, float(cmd.linear.x)))
    limited.angular.z = min(ANGULAR_Z_MAX, max(ANGULAR_Z_MIN, float(cmd.angular.z)))
    return limited


def command_from_pose(pose: object | None) -> Twist:
    """
    Build a Twist from the last pose.

    Before any pose arrives, publish a zero command. After that, use the
    fixed patrol speeds and clamp them.
    """
    cmd = Twist()
    if pose is None:
        return cmd
    cmd.linear.x = LINEAR_X
    cmd.angular.z = ANGULAR_Z
    return clamp_command(cmd)
