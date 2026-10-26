# ПР07. Gazebo и мост ros_gz

Личный репозиторий практики. Код правится на Windows; симуляция — в **Docker**
(`osrf/ros:lyrical-desktop-full` + `ros-lyrical-ros-gz`, Gazebo Jetty).

Course-kit: `v1-w07`, SHA-256 `9b7fdd5424d3d97e47d51dbe23064934585e62135dc2902844dd679529bda929`.

Пакеты: `course_description` (URDF/tf из ПР06), `course_simulation` (мир, bridge, адаптеры).

## Docker

Нужен Docker Desktop. Первый запуск:

```powershell
.\docker\run-pr07.ps1
docker exec -it robotics-pr07 bash
```

### Пересоздание контейнера

Если в логе launch есть `Another world of the same name is running`, или
`/vehicle/scan` даёт ~20 Гц вместо ~5 — в контейнере остался старый Gazebo.
Останови launch (`Ctrl+C`), выйди из bash и пересоздай контейнер:

```powershell
docker rm -f robotics-pr07
.\docker\run-pr07.ps1
docker exec -it robotics-pr07 bash
```

Дальше снова `colcon build` (если `install/` ещё на месте — можно сразу launch)
и один экземпляр `simulation.launch.py`. Не запускай второй launch в том же контейнере.

В контейнере:

```bash
cd /ws
source /opt/ros/lyrical/setup.bash
colcon build --symlink-install --packages-up-to course_simulation
source install/setup.bash
export GZ_SIM_RESOURCE_PATH="$PWD/src/course_simulation/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
export ROS_DOMAIN_ID=16
gz sdf -k src/course_simulation/models/course_ackermann/model.sdf
mkdir -p evidence/pr07 fixtures
ros2 launch course_simulation simulation.launch.py headless:=true 2>&1 | tee evidence/pr07/headless.txt
```

Проверки — во втором `docker exec` (launch не останавливать):

```bash
source /opt/ros/lyrical/setup.bash
source /ws/install/setup.bash
export ROS_DOMAIN_ID=16
ros2 topic echo /clock --once
ros2 topic hz /vehicle/scan
ros2 topic info -v /vehicle/imu
```

Ожидание: `/clock` отвечает; `/vehicle/scan` ≈ **5 Гц**; в логе launch нет
`Another world…`.

Запись bag (≥ 30 с sim-time):

```bash
timeout --preserve-status --signal=INT --kill-after=5s 35s \
  ros2 bag record --storage mcap --use-sim-time -o fixtures/pr07-sensors \
  --topics /vehicle/camera/image_raw /vehicle/scan /vehicle/imu /vehicle/odom \
  /tf /tf_static /clock
ros2 bag info fixtures/pr07-sensors | tee evidence/pr07/bag-info.txt
```

Тесты и checker:

```bash
colcon test --packages-select course_simulation
python3 .course-kit/v1/tools/check_practice.py PR07 --submission .
```

## Изменение модели

В `models/course_ackermann/model.sdf` частота лидара изменена с 10 Гц на **5 Гц**
(заявленная частота в `sensors.json`). Namespace нод адаптеров: `sim`
(абсолютные `/vehicle/...`, `/drive/safe`, `/clock` без изменений).

## Адаптеры

- `/drive/safe` → `/vehicle/gz_cmd_vel` (`cmd_adapter`)
- `/vehicle/odom_gz` → `/vehicle/odom` + `/tf` odom→base_link (`odom_adapter`)
