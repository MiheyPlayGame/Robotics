# ПР06. Модель робота, tf2 и QoS преобразований

Личный репозиторий практики. Среда: ROS 2 **Lyrical**, Windows + pixi в `C:\ROS\ros2-windows`.
Course-kit: `v1-w06`, SHA-256 `6eda53e1c566f7f0a7e09d7afe1e5a6f3b98397175a7e57dede9a84c6d14d0fe`.

Пакет `course_description` содержит параметризованный `urdf/vehicle.urdf.xacro` (Ackermann, размеры из `models/course_ackermann`) и launch `display.launch.py` с `robot_state_publisher`.

## Подготовка

```bat
cd C:\ROS\ros2-windows
pixi shell
call local_setup.bat
set ROS_DOMAIN_ID=16
cd C:\Users\MPG\NSU\Robotics
```

## Сборка

```bat
colcon build --symlink-install --packages-select course_description
call install\setup.bat
```

## Запуск

```bat
ros2 launch course_description display.launch.py
```

В RViz: Fixed Frame = `base_link`, добавьте TF и RobotModel.

Проверка URDF:

```bat
python -c "import xacro; print(xacro.process_file('src/course_description/urdf/vehicle.urdf.xacro').toxml())" > evidence\pr06\vehicle.urdf
```

## Тесты и сдача

```bat
python -m pytest src/course_description/test -q
python .course-kit/v1/tools/check_practice.py PR06 --submission .
```

Evidence: `evidence/pr06/`.
