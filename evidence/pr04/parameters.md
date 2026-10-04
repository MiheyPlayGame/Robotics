# ПР04. Параметры, отказ и сервис/действие

Среда: ROS 2 Lyrical, Windows + pixi (`C:\ROS\ros2-windows`), `ROS_DOMAIN_ID=16`.
Course-kit: `v1-w04`, SHA-256 `fec6b4e886c19146078bf69fbf90a19279a4cd33f656642395350b299efeb226`.

Запуск: `ros2 launch turtle_bringup sim.launch.py`, затем
`ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel`.

## Параметры по умолчанию

```bat
ros2 param get /patrol publish_hz
ros2 param get /patrol linear_speed
ros2 param get /patrol turn_rate
```

```
Double value is: 10.0
Double value is: 0.5
Double value is: 0.3
```

## Допустимая смена частоты 10 → 5 Гц

```bat
ros2 param set /patrol publish_hz 5.0
ros2 param get /patrol publish_hz
ros2 topic hz /turtle1/cmd_vel --window 20
```

```
Set parameter successful
Double value is: 5.0
```

Фрагмент `topic hz` после смены:

```
average rate: 5.003
	min: 0.188s max: 0.215s std dev: 0.00651s window: 20
average rate: 5.004
	min: 0.191s max: 0.211s std dev: 0.00513s window: 20
```

Таймер пересоздан с периодом `1/5 = 0.2` с; поток стал ≈5 Гц.

## Отклонение нуля (исправный код)

```bat
ros2 param set /patrol publish_hz 0.0
ros2 param get /patrol publish_hz
```

```
Setting parameter failed: publish_hz must be in [1.0, 30.0] Hz
Double value is: 5.0
```

Значение и период таймера остаются `5.0` / `0.2` с (см. также `param-set-0-fixed.txt`).

## Дефект: проверка частоты временно отключена

Временно убрали `validate_publish_hz` из `add_on_set_parameters_callback` и передали `0.0`.
Результат (`param-set-0-broken.txt`):

```
before publish_hz=10.0
EXCEPTION while setting publish_hz=0.0:
...
ZeroDivisionError: float division by zero
parameter value after exception: 0.0
```

Причина: `timer_period_from_hz` считает `1/publish_hz` уже после записи параметра; ноль ломает post-set и портит активное состояние. С проверкой отказ происходит до изменения таймера и значения.

## Чистые тесты

`python -m pytest src/patrol/test` → 9 passed (`tests.txt`): смена 10→5, ноль, отрицательное, NaN.

## Сервис `/clear` и action `/turtle1/rotate_absolute`

```bat
ros2 service call /clear std_srvs/srv/Empty {}
ros2 action list -t
```

```
requester: making request: std_srvs.srv.Empty_Request()

response:
std_srvs.srv.Empty_Response()

/turtle1/rotate_absolute [turtlesim_msgs/action/RotateAbsolute]
```

Сервисный запрос — однократный обмен request/response без промежуточного статуса.
Цель action — длительная задача с feedback и возможностью отмены до завершения.
