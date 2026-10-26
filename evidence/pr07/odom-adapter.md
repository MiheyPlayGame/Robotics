# Odometry adapter (PR07)

## Frames

| Role | Source (Gazebo / bridge `/vehicle/odom_gz`) | Normalized (`/vehicle/odom`) |
|------|-----------------------------------------------|------------------------------|
| Parent | `course_ackermann/odom` | `odom` |
| Child | `course_ackermann/base_link` | `base_link` |

Stamp, pose, twist, and both covariance blocks are copied unchanged.
Messages with any other frame pair or non-finite pose/twist values are dropped.

## TF ownership

| Edge | Owner | Topic |
|------|-------|-------|
| `odom` → `base_link` (dynamic) | `odom_adapter` | `/tf` |
| `base_link` → sensors (static) | `robot_state_publisher` (PR06 URDF) | `/tf_static` |

Exactly one dynamic publisher for `odom→base_link`.

## Stamp preservation test

Unit test `test_normalize_frames_and_preserve_stamp` builds an `Odometry` with
`header.stamp = (3, 500000000)` and asserts the normalized message keeps the same stamp.
Run: `python3 -m pytest src/course_simulation/test/test_odom_adapter.py -q`
