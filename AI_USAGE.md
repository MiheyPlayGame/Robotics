# Декларация использования ИИ

## PR02

- Использован ИИ: да
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR02`
- Затронутые компоненты: `src/turtle_bringup/` (пакет, `launch/sim.launch.py`, `setup.py`, `package.xml`); `evidence/pr02/`; `.github/workflows/ci.yml`; `README.md`; `.gitignore`; `AI_USAGE.md`
- Характер помощи: разбор условия ПР02 и runbook; создание ament_python пакета и launch; сборка colcon; запуск CLI-опытов (движение, сбой имени `/cmd_vel`, исправление); оформление evidence и двух commit; обновление CI под course-kit `v1-w03`
- Как результат был проверен независимо: SHA-256 course-kit `v1-w03` совпал с API; `colcon build` дважды успешен; `ros2 launch turtle_bringup sim.launch.py` стартует `/turtlesim`; pub на `/turtle1/cmd_vel` меняет позу; на `/cmd_vel` publisher без subscriber turtlesim; после смены только имени поза снова движется; `python -m py_compile` и `check_practice.py PR02`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
