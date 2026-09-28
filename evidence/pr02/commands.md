# ПР02. Команды и наблюдения

Среда: ROS 2 Lyrical, Windows + pixi (`C:\ROS\ros2-windows`), `ROS_DOMAIN_ID=16`.
Корень workspace = корень репозитория.

## Три Linux/терминальные команды

### 1. `pwd` / текущий каталог

```bat
cd /d C:\Users\MPG\NSU\Robotics
cd
```

Назначение: убедиться, что терминал стоит в корне workspace (личный репозиторий), а не в установке ROS.
Результат: `C:\Users\MPG\NSU\Robotics`. Это путь к репозиторию; `ros2 pkg prefix turtlesim` даёт `C:\ROS\ros2-windows` — это другой каталог (установленный пакет).

### 2. `mkdir -p` / `mkdir` с созданием родителя

```bat
mkdir src evidence\pr02
```

Назначение: создать каталог исходников и evidence для этой работы.
Результат: появились `src\` и `evidence\pr02\`.

### 3. `tee` / перенаправление сборки в лог

На bash: `colcon build ... 2>&1 | tee evidence/pr02/build.txt`.
На Windows зафиксировали эквивалент:

```bat
colcon build --symlink-install --packages-select turtle_bringup > evidence\pr02\build.txt 2>&1
```

Назначение: сохранить полный лог сборки (stdout и stderr) в файл сдачи.
Результат: `Finished <<< turtle_bringup`, summary «1 package finished».

## `>` против `|`, `source`/`call` против новой программы

- `>` пишет stdout **в файл** и **заменяет** прежнее содержимое. Следующая команда этот поток не читает.
- `|` передаёт stdout **следующей команде** (конвейер). `tee` читает поток, показывает на экране и одновременно пишет в файл.
- `source` / `call local_setup.bat` выполняет скрипт **в текущем** процессе оболочки: переменные `PATH`, `AMENT_PREFIX_PATH` остаются после выхода из скрипта.
- Запуск новой программы (`ros2`, `colcon`) создаёт отдельный процесс; он наследует уже подготовленную среду, но сам `setup` не «вшивает» в родителя, если его не подключали через `source`/`call`.

## Launch: запуск, граф, остановка

```bat
call C:\ROS\ros2-windows\local_setup.bat
set ROS_DOMAIN_ID=16
cd /d C:\Users\MPG\NSU\Robotics
call install\setup.bat
ros2 pkg prefix turtle_bringup
:: C:\Users\MPG\NSU\Robotics\install\turtle_bringup
dir "%CD%\install\turtle_bringup\share\turtle_bringup\launch"
:: sim.launch.py
ros2 launch turtle_bringup sim.launch.py
```

Наблюдение: окно turtlesim открылось; в логе `Spawning turtle [turtle1]`.
В другом терминале с той же средой и доменом:

```bat
ros2 node list --no-daemon --spin-time 2
```

Вывод: `/turtlesim`.
`Ctrl+C` в терминале launch завершил процесс `turtlesim_node` вместе с launch.

## Движение по правильному топику

Ожидание: `linear.x=1.0`, `angular.z=0.5` — черепаха едет вперёд и поворачивает влево (против часовой).

Поза до:

```text
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
```

```bat
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.5}}"
```

Поза после:

```text
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
```

Координаты изменились в ожидаемом направлении; без новых команд скорости снова 0.

## До / сбой / после (имя топика)

### До (исправная доставка уже показана выше)

Издатель и подписчик на `/turtle1/cmd_vel`, поза меняется.

### Сбой: тот же Twist в `/cmd_vel`

```bat
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.5}}"
```

`ros2 topic info /cmd_vel --verbose`:

- Publisher count: 1 (`_ros2cli_...`)
- Subscription count: **0**

`ros2 topic info /turtle1/cmd_vel --verbose`:

- Publisher count: 0
- Subscription count: 1 (`turtlesim`)

Поза во время сбоя осталась `x≈6.509`, `y≈5.797`, `theta≈0.504` — черепаха не едет.
Тип сообщения тот же (`geometry_msgs/msg/Twist`), но полное имя топика другое: discovery видит издателя на `/cmd_vel`, а turtlesim слушает только `/turtle1/cmd_vel`. Сообщения не доставляются.

### После: исправлено только имя

```bat
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.5}}"
```

`ros2 topic info /turtle1/cmd_vel --verbose`: Publisher count 1 и Subscription count 1 (`turtlesim`).
Поза после исправления:

```text
x: 7.168434143066406
y: 6.3883056640625
theta: 0.9504441022872925
linear_velocity: 1.0
angular_velocity: 0.5
```

Файл на диске (`sim.launch.py`) ≠ запущенная нода (`/turtlesim`) ≠ сообщение в графе (публикация в конкретное полное имя топика). Правильный тип недостаточен без совпадения имени.
