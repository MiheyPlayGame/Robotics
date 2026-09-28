# ПР03. Первая нода: поза и команда

Личный репозиторий практики. Среда: ROS 2 **Lyrical**, установка Windows + pixi в `C:\ROS\ros2-windows`.
Course-kit: `v1-w03`, SHA-256 `7fbfd3e8161ab6c6ebefc7663efdaf77d9a7d490399743507f33dcefbd5ac522`.

Пакет `turtle_bringup` (из ПР02) поднимает turtlesim. Пакет `patrol` подписывается на `/turtle1/pose` и по таймеру 0,1 с публикует `Twist` в относительный `cmd_vel`.

Тип позы на Lyrical: `turtlesim_msgs/msg/Pose` (`ros2 topic type /turtle1/pose`).

## Подготовка терминала

```bat
cd C:\ROS\ros2-windows
pixi shell
call local_setup.bat
set ROS_DOMAIN_ID=16
cd C:\Users\MPG\NSU\Robotics
```

## Сборка

```bat
colcon build --symlink-install --packages-select turtle_bringup patrol
call install\setup.bat
```

## Запуск

Терминал 1 — симулятор:

```bat
ros2 launch turtle_bringup sim.launch.py
```

Терминал 2 — patrol **с remap** (исправная связь):

```bat
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Без remap нода публикует в относительный `cmd_vel` (часто `/cmd_vel`), не соединённый с `/turtle1/cmd_vel` — дефект имени для ПР03.

## Тесты и проверка сдачи

```bat
python -m pytest src/patrol/test
python .course-kit/v1/tools/check_practice.py PR03 --submission .
```

Evidence: `evidence/pr03/`.
