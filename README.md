# ПР01. Окружение и граф ROS 2

Личный репозиторий практики. Среда: ROS 2 **Lyrical**, установка Windows + pixi в `C:\ROS\ros2-windows`.
Course-kit: `v1-w01`, SHA-256 `57866a9c98fa3abdec27b35a180697ee680bfb0f05cc015970ce306d6d849fea`.

## Подготовка трёх терминалов

В каждом терминале одна и та же среда и один домен:

```bat
cd C:\ROS\ros2-windows
pixi shell
call local_setup.bat
set ROS_DOMAIN_ID=16
cd C:\Users\MPG\NSU\Robotics
```

В bash/WSL эквивалент из условия курса:

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
```

Предупреждение RTI Connext DDS на Windows можно игнорировать: используется `rmw_fastrtps_cpp`.

## Терминал C — отчёт среды

```bat
mkdir evidence\pr01
ros2 doctor --report > evidence\pr01\doctor.txt 2>&1
```

## Терминал A — симулятор

```bat
ros2 run turtlesim turtlesim_node
```

Окно turtlesim должно оставаться открытым до конца опыта. Процесс запускается в домене 16 и **не перезапускается** при смене домена в других терминалах.

## Терминал B — teleop

```bat
ros2 run turtlesim turtle_teleop_key
```

Фокус в этом окне, стрелки двигают черепаху.

## Терминал C — исправный граф

```bat
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose
```

`hz` держать не меньше 10 с, затем Ctrl+C. Для Lyrical тип позы: `turtlesim_msgs/msg/Pose`.

В bash:

```bash
POSE_TYPE=$(ros2 topic type /turtle1/pose)
```

Наблюдения записываются в `evidence/pr01/graph.md`.

## Разрыв связи (домен 17)

Симулятор A **остаётся** в домене 16. В B остановить teleop (Ctrl+C) и запустить заново:

```bat
set ROS_DOMAIN_ID=17
ros2 run turtlesim turtle_teleop_key
```

Стрелки больше не двигают черепаху. В C:

```bat
set ROS_DOMAIN_ID=17
ros2 node list --no-daemon --spin-time 2
```

Ожидается `/teleop_turtle` без `/turtlesim`. Поза не приходит за 5 с (`exit=124`).

В bash:

```bash
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
```

На Windows нет GNU `timeout` в cmd: процесс `ros2 topic echo ... --once` останавливали через 5 с и писали код 124 в `evidence/pr01/pose-broken.txt`.

## Восстановление (домен 16)

В B остановить teleop, снова `set ROS_DOMAIN_ID=16` и запустить `turtle_teleop_key`. В C:

```bat
set ROS_DOMAIN_ID=16
ros2 node list --no-daemon --spin-time 2
```

Ожидаются обе ноды, поза приходит, стрелки снова работают. Результат: `evidence/pr01/pose-fixed.txt` (`exit=0`).

`ROS_DOMAIN_ID` применяется **при запуске процесса**. Уже работающий turtlesim остаётся в 16; teleop/CLI в 17 его не видят. Поэтому перезапускали teleop, а ROS и симулятор не переустанавливали.

## Локальная проверка файлов

```bash
python3 -m json.tool evidence/pr01/environment.json > /dev/null
python3 .course-kit/v1/tools/check_practice.py PR01 --submission .
```
