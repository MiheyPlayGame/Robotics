# Декларация использования ИИ

## PR05

- Использован ИИ: да
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR05`
- Затронутые компоненты: `src/course_bringup/`; `config/qos-overrides.yaml`; `evidence/pr05/`; `.github/workflows/ci.yml`; `README.md`
- Характер помощи: разбор [ПР05](https://ros.lms.ci.nsu.ru/practices/pr05); namespace launch, best_effort `sensor_pose`, несовместимость с `reliable`, MCAP record/replay с QoS overrides; обход падения turtlesim в агентских терминалах из‑за Qt
- Как результат был проверен независимо: `pytest` по `patrol`/`course_bringup`; live reliable → timeout, best_effort → сообщение; `ros2 bag info` одного потока; `check_practice.py PR05`

## PR06

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР)
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR06`
- Затронутые компоненты: `src/course_description/` (URDF/Xacro, launch); `evidence/pr06/`; `.github/workflows/ci.yml`; `README.md`
- Характер помощи: разбор [ПР06](https://ros.lms.ci.nsu.ru/practices/pr06); параметризация Ackermann по SDF kit; `robot_state_publisher`; QoS `/tf_static` transient_local vs volatile; дефект parent `lidar_link`
- Как результат был проверен независимо: `pytest src/course_description/test`; xacro expand + разбор URDF; `tf-qos.txt` (transient_local exit=0, volatile exit=124); `check_practice.py PR06`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
