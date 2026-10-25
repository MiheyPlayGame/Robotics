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
call install\setup.bat
set FASTDDS_BUILTIN_TRANSPORTS=UDPv4
```

`FASTDDS_BUILTIN_TRANSPORTS=UDPv4` нужен на Windows: иначе после Ctrl+C / обрыва часто сыпятся Python-ноды с exit `3221225477` (Access Violation) из‑за shared memory Fast DDS.

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

Ожидание: черепаха едет; в логе `qos_probe: ... reliability=reliable` и **нет** `received sensor_pose`. Во втором терминале (тот же setup / domain / `FASTDDS_BUILTIN_TRANSPORTS`):

```bat
ros2 topic info /robot_a/sensor_pose -v
python evidence\pr05\_recv_once.py --reliability reliable --timeout 3
```

Publisher — `best_effort`, subscription — `reliable`; `_recv_once` → timeout / incompatible QoS.

Совместимый профиль и запись (`-o` не перезаписывает папку — укажи новый `bag_dir`, если старый уже есть):

```bat
ros2 launch course_bringup patrol.launch.py namespace:=robot_a subscriber_reliability:=best_effort record:=true bag_dir:=evidence/pr05/bag_demo
```

Ожидание: в логе `received sensor_pose #1` / `#50`; `_recv_once` с `best_effort` печатает pose. После Ctrl+C:

```bat
python evidence\pr05\_recv_once.py --reliability best_effort --timeout 5
ros2 bag info evidence/pr05/bag_demo
```

Replay с override (путь к bag подставь свой):

```bat
ros2 bag play evidence/pr05/bag --qos-profile-overrides-path config/qos-overrides.yaml
```

## Тесты и проверка сдачи

```bat
python -m pytest src/patrol/test
python .course-kit/v1/tools/check_practice.py PR05 --submission .
```

Evidence: `evidence/pr05/`.
