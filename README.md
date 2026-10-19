# ПР05. Launch, QoS и повтор записи

Личный репозиторий практики. Среда: ROS 2 **Lyrical**, установка Windows + pixi в `C:\ROS\ros2-windows`.
Course-kit: `v1-w06`, SHA-256 `6eda53e1c566f7f0a7e09d7afe1e5a6f3b98397175a7e57dede9a84c6d14d0fe`.

Пакет `course_bringup` одной командой поднимает turtlesim, `patrol`, `pose_relay` (best_effort `sensor_pose`) и `qos_probe` с настраиваемой reliability. Опционально пишет MCAP.

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
colcon build --symlink-install --packages-select turtle_bringup patrol course_bringup
call install\setup.bat
```

## Запуск

Несовместимый QoS (`reliable` против `best_effort`):

```bat
ros2 launch course_bringup patrol.launch.py namespace:=robot_a subscriber_reliability:=reliable record:=false
```

Совместимый профиль и запись:

```bat
ros2 launch course_bringup patrol.launch.py namespace:=robot_a subscriber_reliability:=best_effort record:=true bag_dir:=evidence/pr05/bag
```

Replay с override:

```bat
ros2 bag play evidence/pr05/bag --qos-profile-overrides-path config/qos-overrides.yaml
```

## Тесты и проверка сдачи

```bat
python -m pytest src/patrol/test
python .course-kit/v1/tools/check_practice.py PR05 --submission .
```

Evidence: `evidence/pr05/`.
