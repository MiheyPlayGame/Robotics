# Декларация использования ИИ

## PR05

- Использован ИИ: да
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR05`
- Затронутые компоненты: `src/course_bringup/`; `config/qos-overrides.yaml`; `evidence/pr05/`; `.github/workflows/ci.yml`; `README.md`
- Характер помощи: разбор [ПР05](https://ros.lms.ci.nsu.ru/practices/pr05); namespace launch, best_effort `sensor_pose`, несовместимость с `reliable`, MCAP record/replay с QoS overrides; обход падения turtlesim в агентских терминалах из‑за Qt
- Как результат был проверен независимо: `pytest` по `patrol`/`course_bringup`; live `ros2 topic echo` reliable → timeout, best_effort → сообщение; `ros2 bag info` одного потока; `check_practice.py PR05`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
