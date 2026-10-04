# ПР04. Параметризуем движение

Личный репозиторий практики. Среда: ROS 2 **Lyrical**, установка Windows + pixi в `C:\ROS\ros2-windows`.
Course-kit: `v1-w04`, SHA-256 `fec6b4e886c19146078bf69fbf90a19279a4cd33f656642395350b299efeb226`.

Пакет `turtle_bringup` поднимает turtlesim. Пакет `patrol` подписывается на `/turtle1/pose` и публикует `Twist` в относительный `cmd_vel` с параметрами `linear_speed`, `turn_rate`, `publish_hz`.

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

Терминал 2 — patrol с remap:

```bat
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Параметры (по умолчанию `0.5`, `0.3`, `10.0`):

```bat
ros2 param set /patrol publish_hz 5.0
ros2 param set /patrol publish_hz 0.0
```

Допустимы: скорость `0…1` м/с, поворот `−1…1` рад/с, частота `1…30` Гц. Нулевая/NaN/отрицательная частота отклоняется без смены таймера.

## Тесты и проверка сдачи

```bat
python -m pytest src/patrol/test
python .course-kit/v1/tools/check_practice.py PR04 --submission .
```

Evidence: `evidence/pr04/`.
