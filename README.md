# ПР02. Терминал, пакет и запуск turtlesim

Личный репозиторий практики. Среда: ROS 2 **Lyrical**, установка Windows + pixi в `C:\ROS\ros2-windows`.
Course-kit: `v1-w03`, SHA-256 `7fbfd3e8161ab6c6ebefc7663efdaf77d9a7d490399743507f33dcefbd5ac522`.

Пакет `turtle_bringup` запускает установленный `turtlesim_node` через `sim.launch.py`.

## Подготовка терминала

```bat
cd C:\ROS\ros2-windows
pixi shell
call local_setup.bat
set ROS_DOMAIN_ID=16
cd C:\Users\MPG\NSU\Robotics
mkdir src evidence\pr02
```

В bash/WSL:

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
cd "$(git rev-parse --show-toplevel)"
mkdir -p src evidence/pr02
```

## Сборка пакета

Из корня репозитория (подключена только базовая ROS):

```bat
colcon build --symlink-install --packages-select turtle_bringup
```

Логи: `evidence/pr02/build-empty.txt` (без launch), `evidence/pr02/build.txt` (с launch).

Подключить workspace:

```bat
call install\setup.bat
ros2 pkg prefix turtle_bringup
```

## Запуск

```bat
ros2 launch turtle_bringup sim.launch.py
```

В другом терминале с тем же `local_setup`, `install\setup.bat` и `ROS_DOMAIN_ID=16`:

```bat
ros2 node list --no-daemon --spin-time 2
ros2 topic echo /turtle1/pose --once
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.5}}"
```

## Сбой имени топика и исправление

Сбой (издатель виден, turtlesim не подписан):

```bat
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.5}}"
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
```

Исправление — только полное имя:

```bat
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.5}}"
```

Подробности: `evidence/pr02/commands.md`, типы: `evidence/pr02/types.md`.

## Локальная проверка файлов

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```
