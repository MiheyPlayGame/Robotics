# ПР02. Типы сообщений

## Основные топики turtlesim

| Топик | Тип (Lyrical) | Назначение |
| --- | --- | --- |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Команда скорости: линейная и угловая |
| `/turtle1/pose` | `turtlesim_msgs/msg/Pose` | Текущая поза черепахи на плоскости |

Проверено командами:

```bat
ros2 topic type /turtle1/pose
ros2 topic type /turtle1/cmd_vel
ros2 interface show geometry_msgs/msg/Twist
```

## Поля `geometry_msgs/msg/Twist`

- `linear` (`Vector3`: `x`, `y`, `z`) — линейная скорость. В turtlesim для плоскости важен `linear.x` (вперёд/назад).
- `angular` (`Vector3`: `x`, `y`, `z`) — угловая скорость. В turtlesim важен `angular.z` (поворот в плоскости).

В опыте использовали `{linear: {x: 1.0}, angular: {z: 0.5}}`.

## Поля позы `turtlesim_msgs/msg/Pose`

- `x`, `y` — координаты на поле симулятора
- `theta` — ориентация (рад)
- `linear_velocity`, `angular_velocity` — текущие скорости после команды
