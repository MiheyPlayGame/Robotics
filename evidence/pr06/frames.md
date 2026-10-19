# PR06 frames

Fixed Frame for RViz: `base_link`.

| Parent | Child | Joint | Type | Expected transform (xyz, rpy) | Publisher |
| --- | --- | --- | --- | --- | --- |
| `base_link` | `camera_link` | `camera_joint` | fixed | `0.28 0 0.38`, `0 0 0` | `robot_state_publisher` → `/tf_static` |
| `base_link` | `lidar_link` | `lidar_joint` | fixed | `0.28 0 0.38`, `0 0 0` | `robot_state_publisher` → `/tf_static` |
| `base_link` | `imu_link` | `imu_joint` | fixed | `0.28 0 0.38`, `0 0 0` | `robot_state_publisher` → `/tf_static` |
| `base_link` | `front_left_wheel` | `front_left_wheel_joint` | continuous | `0.4 0.31 0`, `0 0 0` | `/tf` only after `/joint_states` |
| `base_link` | `front_right_wheel` | `front_right_wheel_joint` | continuous | `0.4 -0.31 0`, `0 0 0` | `/tf` only after `/joint_states` |
| `base_link` | `rear_left_wheel` | `rear_left_wheel_joint` | continuous | `-0.4 0.31 0`, `0 0 0` | `/tf` only after `/joint_states` |
| `base_link` | `rear_right_wheel` | `rear_right_wheel_joint` | continuous | `-0.4 -0.31 0`, `0 0 0` | `/tf` only after `/joint_states` |

Parameters (from SDF `models/course_ackermann`): `wheel_radius=0.12`, `track=0.62`, `wheel_base=0.8`, body `1.05×0.52×0.22`.

## Defect

Wrong parent: `lidar_parent:=camera_link` keeps the same joint offset, so lidar sits at roughly `0.56 0 0.76` in `base_link` instead of `0.28 0 0.38`. `check_urdf` still passes; `test_lidar_parent_is_base_link` fails. Restored `lidar_parent:=base_link`.
