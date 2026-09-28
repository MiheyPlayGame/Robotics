# ПР03. Демонстрация ноды patrol

Среда: ROS 2 Lyrical, Windows + pixi (`C:\ROS\ros2-windows`), `ROS_DOMAIN_ID=16`.
Тип позы: `turtlesim_msgs/msg/Pose` (`evidence/pr03/pose-type.txt`).

## Роли `init`, `spin`, callback и Ctrl+C

- `rclpy.init()` — поднимает клиентскую библиотеку ROS 2 в процессе (контекст, DDS). Без него нельзя создавать ноды.
- `rclpy.spin(node)` — крутит исполнитель: доставляет сообщения в callbacks подписок и срабатывания таймеров. Пока идёт `spin`, нода «жива».
- Callback подписки `_on_pose` — только сохраняет последнее сообщение `/turtle1/pose` в поле объекта. Callback таймера `_on_timer` (0,1 с) берёт последнюю позу, вызывает чистую функцию `command_from_pose` и публикует `Twist` в относительный `cmd_vel`.
- Ctrl+C → `KeyboardInterrupt` → выход из `spin`, `destroy_node()` и `rclpy.shutdown()`. Исчезновение процесса **не** равно мгновенной команде торможения: turtlesim продолжает по инерции последнее полученное `Twist`, пока не получит ноль или не остановится сам. После остановки ноды нужно дождаться остановки turtlesim.

## Сборка и тесты

```bat
colcon build --symlink-install --packages-select turtle_bringup patrol
call install\setup.bat
python -m pytest src/patrol/test
```

Лог тестов: `evidence/pr03/tests.txt` (3 passed: нет позы → ноль; есть поза → 0.5/0.3; clamp angular).

## Дефект имени (без remap)

```bat
ros2 launch turtle_bringup sim.launch.py
ros2 run patrol patrol
```

Нода публикует в относительный `cmd_vel` → фактически `/cmd_vel`.
`topic info /cmd_vel --verbose`: Publisher=`patrol`, Subscription count=0 (`cmd-vel-broken.txt`).
`topic info /turtle1/cmd_vel --verbose`: только подписчик `turtlesim`, Publisher count=0 (`turtle1-cmd-vel-broken.txt`).
Поза не меняется (`pose-broken.txt`, `pose-broken-later.txt`: x≈5.54, v=0).

## Исправление remap

```bat
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

`topic info /turtle1/cmd_vel --verbose`: Publisher=`patrol` и Subscription=`turtlesim` (`turtle1-cmd-vel-fixed.txt`).
Поза движется с `linear_velocity=0.5`, `angular_velocity=0.3` (`pose-fixed-before.txt`, `pose-fixed-after.txt`).

## Частота команды (~10 с)

```bat
ros2 topic hz turtle1/cmd_vel --window 50
```

Окно ~10 с: average rate ≈ **10.0 Hz** (`hz.txt`), что соответствует таймеру 0,1 с.
