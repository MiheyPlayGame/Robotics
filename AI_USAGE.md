# Декларация использования ИИ

## PR04

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР)
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR04`
- Затронутые компоненты: `src/patrol/` (параметры, валидация, пересоздание таймера, тесты); `evidence/pr04/`; `.github/workflows/ci.yml`; `README.md`
- Характер помощи: разбор [ПР04](https://ros.lms.ci.nsu.ru/practices/pr04); параметры `linear_speed`/`turn_rate`/`publish_hz`; воспроизведение ZeroDivisionError при отключённой проверке частоты; service `/clear` и action `rotate_absolute`; оформление evidence и двух commit
- Как результат был проверен независимо: `pytest src/patrol/test` — 9 passed; `ros2 param set /patrol publish_hz 5.0` меняет поток ≈5 Hz; `publish_hz 0.0` отклонён, значение остаётся 5.0; без проверки частоты `0.0` даёт `ZeroDivisionError`; `check_practice.py PR04`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
