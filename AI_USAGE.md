# Декларация использования ИИ

## PR03

- Использован ИИ: да
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR03`
- Затронутые компоненты: `src/patrol/` (нода, чистая функция команды, тесты); сохранён `src/turtle_bringup/`; `evidence/pr03/`; `.github/workflows/ci.yml`; `README.md`; `AI_USAGE.md`
- Характер помощи: разбор ПР03; создание пакета `patrol` с подпиской на позу, таймером 0,1 с и относительным `cmd_vel`; воспроизведение разрыва имени и remap; измерение частоты; оформление evidence и двух commit
- Как результат был проверен независимо: `colcon build --packages-select patrol` успешен; `pytest src/patrol/test` — 3 passed; без remap `/cmd_vel` без подписчика turtlesim и поза неподвижна; с `-r cmd_vel:=/turtle1/cmd_vel` поза движется (0.5/0.3), `topic hz` ≈ 10 Hz; `check_practice.py PR03`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
