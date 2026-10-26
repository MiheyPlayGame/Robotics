# ПР06. Модель робота, tf2 и QoS преобразований

Личный репозиторий практики. Среда: ROS 2 **Lyrical**, Windows + pixi в `C:\ROS\ros2-windows`.
Course-kit: `v1-w06`, SHA-256 `6eda53e1c566f7f0a7e09d7afe1e5a6f3b98397175a7e57dede9a84c6d14d0fe`.

Пакет `course_description` содержит параметризованный `urdf/vehicle.urdf.xacro` (Ackermann, размеры из `models/course_ackermann`) и launch `display.launch.py` с `robot_state_publisher`.

## Подготовка

Во **всех** терминалах (launch, RViz, проверки) одинаковый domain и транспорт:

```bat
cd C:\ROS\ros2-windows
pixi shell
call local_setup.bat
set ROS_DOMAIN_ID=16
cd C:\Users\MPG\NSU\Robotics
call install\setup.bat
set FASTDDS_BUILTIN_TRANSPORTS=UDPv4
```

`FASTDDS_BUILTIN_TRANSPORTS=UDPv4` нужен на Windows, иначе RViz часто не видит `/tf_static` (разный Fast DDS SHM/UDP).

## Сборка

```bat
colcon build --symlink-install --packages-select course_description
call install\setup.bat
```

## Запуск

Терминал 1 — модель и `/tf_static`:

```bat
ros2 launch course_description display.launch.py
```

Ожидание: `Robot initialized` (WARN KDL про inertia у `base_link` — норма).

Терминал 2 — RViz (на Windows без HiDPI-флагов 3D-viewport часто чёрный и мерцает):

```bat
set QT_ENABLE_HIGHDPI_SCALING=0
set QT_SCREEN_SCALE_FACTORS=1
ros2 run rviz2 rviz2
```

В RViz: Fixed Frame = `base_link` → Add → **TF** и **RobotModel**.  
Ожидание в TF: `base_link`, `camera_link`, `imu_link`, `lidar_link` — Transform OK; дерево `base_link` → сенсоры.

Колёса появятся в `/tf` только после `joint_state_publisher` (в launch его нет). Visual/Collision кузова на части Windows-машин не рисуется при Status Ok — для демо достаточно осей TF.

## Проверка QoS `/tf_static`

Пока launch жив (тот же setup / domain / `FASTDDS_BUILTIN_TRANSPORTS`):

```bat
ros2 topic info /tf_static --verbose
python evidence\pr06\_recv_tf_static.py --durability transient_local --timeout 5
python evidence\pr06\_recv_tf_static.py --durability volatile --timeout 4
```

Publisher: RELIABLE + **TRANSIENT_LOCAL**.  
`transient_local` → 3 transforms (camera/imu/lidar); `volatile` → timeout.

Проверка URDF:

```bat
python -c "import xacro; print(xacro.process_file('src/course_description/urdf/vehicle.urdf.xacro').toxml())" > evidence\pr06\vehicle.urdf
```

или `python evidence\pr06\_make_model_check.py`.

## Тесты и сдача

```bat
python -m pytest src/course_description/test -q
python .course-kit/v1/tools/check_practice.py PR06 --submission .
```

Evidence: `evidence/pr06/`.
