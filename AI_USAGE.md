# Декларация использования ИИ

## PR02

- Использован ИИ: да
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR02`
- Затронутые компоненты: `src/turtle_bringup/` (пакет, `launch/sim.launch.py`, `setup.py`, `package.xml`); `evidence/pr02/`; `.github/workflows/ci.yml`; `README.md`; `.gitignore`; `AI_USAGE.md`
- Характер помощи: разбор условия ПР02 и runbook; создание ament_python пакета и launch; сборка colcon; запуск CLI-опытов (движение, сбой имени `/cmd_vel`, исправление); оформление evidence и двух commit
- Как результат был проверен независимо: `colcon build` дважды успешен; `ros2 launch turtle_bringup sim.launch.py` стартует `/turtlesim`; pub на `/turtle1/cmd_vel` меняет позу; на `/cmd_vel` publisher без subscriber turtlesim; после смены только имени поза снова движется; `python -m py_compile` и `check_practice.py PR02`

## PR03

- Использован ИИ: да
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR03`
- Затронутые компоненты: `src/patrol/` (нода, чистая функция команды, тесты); сохранён `src/turtle_bringup/`; `evidence/pr03/`; `.github/workflows/ci.yml`; `README.md`; `AI_USAGE.md`
- Характер помощи: разбор ПР03; создание пакета `patrol` с подпиской на позу, таймером 0,1 с и относительным `cmd_vel`; воспроизведение разрыва имени и remap; измерение частоты; оформление evidence и двух commit
- Как результат был проверен независимо: `colcon build --packages-select patrol` успешен; `pytest src/patrol/test` — 3 passed; без remap `/cmd_vel` без подписчика turtlesim и поза неподвижна; с `-r cmd_vel:=/turtle1/cmd_vel` поза движется (0.5/0.3), `topic hz` ≈ 10 Hz; `check_practice.py PR03`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
