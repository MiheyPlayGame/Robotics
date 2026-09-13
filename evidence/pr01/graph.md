# ПР01. Граф ROS 2 и разрыв домена

Среда: native Windows 11, ROS 2 Lyrical, `rmw_fastrtps_cpp`.
Домены опыта: 16 (исправный / восстановление) и 17 (разрыв).
Тип позы: `turtlesim_msgs/msg/Pose`.

## Роли нод

| Нода | Роль |
| --- | --- |
| `/turtlesim` | симулятор: публикует `/turtle1/pose`, подписывается на `/turtle1/cmd_vel` |
| `/teleop_turtle` | управление с клавиатуры: публикует `/turtle1/cmd_vel` |

## Топики и типы

| Топик | Тип |
| --- | --- |
| `/turtle1/pose` | `turtlesim_msgs/msg/Pose` |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` |
| `/turtle1/color_sensor` | `turtlesim_msgs/msg/Color` |

## Исправный граф (домен 16)

Оба процесса запущены с `ROS_DOMAIN_ID=16`. Стрелки в терминале B двигают черепаху.

### `ros2 node list --no-daemon --spin-time 2`

```
/teleop_turtle
/turtlesim
```

### `ros2 topic list -t`

```
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim_msgs/msg/Color]
/turtle1/pose [turtlesim_msgs/msg/Pose]
```

### `ros2 node info /turtlesim`

```
/turtlesim
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim_msgs/msg/Color
    /turtle1/pose: turtlesim_msgs/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim_msgs/srv/Kill
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim_msgs/srv/Spawn
    /turtle1/set_pen: turtlesim_msgs/srv/SetPen
    /turtle1/teleport_absolute: turtlesim_msgs/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim_msgs/srv/TeleportRelative
    /turtlesim/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /turtlesim/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    /turtlesim/get_type_description: type_description_interfaces/srv/GetTypeDescription
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    /turtlesim/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Action Servers:
    /turtle1/rotate_absolute: turtlesim_msgs/action/RotateAbsolute
```

### `ros2 topic type /turtle1/pose`

```
turtlesim_msgs/msg/Pose
```

### `ros2 topic echo /turtle1/pose --once`

```
A message was lost!!!
	total count change:1
	total count: 1---
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
```

Поза публикуется и у неподвижной черепахи (старт в центре окна). Строка `A message was lost` — предупреждение Fast DDS при первом `echo`, само сообщение пришло.

### `ros2 topic hz /turtle1/pose` (замер 12 с)

```
WARNING: topic [/turtle1/pose] does not appear to be published yet
average rate: 62.628
	min: 0.014s max: 0.031s std dev: 0.00274s window: 62
average rate: 62.659
	min: 0.014s max: 0.031s std dev: 0.00272s window: 125
average rate: 62.714
	min: 0.014s max: 0.031s std dev: 0.00276s window: 187
average rate: 62.642
	min: 0.013s max: 0.031s std dev: 0.00274s window: 251
average rate: 62.450
	min: 0.013s max: 0.032s std dev: 0.00288s window: 313
average rate: 62.458
	min: 0.013s max: 0.032s std dev: 0.00285s window: 376
average rate: 62.479
	min: 0.013s max: 0.032s std dev: 0.00283s window: 438
average rate: 62.523
	min: 0.013s max: 0.032s std dev: 0.00282s window: 502
average rate: 62.537
	min: 0.013s max: 0.032s std dev: 0.00281s window: 565
average rate: 62.562
	min: 0.013s max: 0.032s std dev: 0.00280s window: 628
average rate: 62.478
	min: 0.013s max: 0.032s std dev: 0.00284s window: 689
```

Фактическая частота: **≈62.5 Гц** (окно 62–689 сообщений за ~12 с). Ориентир курса 60–62.5 Гц.

## До / сбой / после

| | До (домен 16) | Сбой (CLI и teleop в 17, turtlesim в 16) | После (все снова в 16) |
| --- | --- | --- | --- |
| `ros2 node list --no-daemon --spin-time 2` | `/teleop_turtle`, `/turtlesim` | `/teleop_turtle` (нет `/turtlesim`) | `/teleop_turtle`, `/turtlesim` |
| поза `/turtle1/pose --once` | приходит | не приходит за 5 с | приходит |
| код выхода echo | 0 | **124** | **0** |
| стрелки teleop | двигают черепаху | не двигают | снова двигают |

### Сбой: teleop и CLI в домене 17

Симулятор A не перезапускался. Teleop остановлен Ctrl+C и запущен с `ROS_DOMAIN_ID=17`. CLI в C тоже переведён в 17.

`ros2 node list --no-daemon --spin-time 2` (домен 17):

```
/teleop_turtle
```

`timeout 5s ros2 topic echo /turtle1/pose turtlesim_msgs/msg/Pose --once` → пустой вывод, **exit=124**. Файл: `pose-broken.txt`.

В домене 16 в это время по-прежнему виден только `/turtlesim`: процессы в разных доменах друг друга не обнаруживают.

### После: teleop снова в домене 16

Teleop перезапущен с `ROS_DOMAIN_ID=16`. Симулятор не трогали.

`ros2 node list --no-daemon --spin-time 3` (домен 16):

```
/teleop_turtle
/turtlesim
```

`timeout 5s ros2 topic echo /turtle1/pose turtlesim_msgs/msg/Pose --once` → поза пришла, **exit=0**. Файл: `pose-fixed.txt`.

## Причина

`ROS_DOMAIN_ID` задаётся **при запуске процесса**. Уже работающий `/turtlesim` остаётся в домене 16. Teleop и CLI, запущенные в 17, ищут участников в другой области обнаружения и не видят симулятор. Поэтому достаточно перезапустить teleop (и CLI) в исходном домене; ROS и симулятор переустанавливать не нужно.
