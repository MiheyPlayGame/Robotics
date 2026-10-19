# Декларация использования ИИ

## PR06

- Использован ИИ: да
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR06`
- Затронутые компоненты: `src/course_description/` (URDF/Xacro, launch); `evidence/pr06/`; `.github/workflows/ci.yml`; `README.md`
- Характер помощи: разбор [ПР06](https://ros.lms.ci.nsu.ru/practices/pr06); параметризация Ackermann по SDF kit; `robot_state_publisher`; QoS `/tf_static` transient_local vs volatile
- Как результат был проверен независимо: `pytest src/course_description/test`; xacro expand + разбор URDF; `tf-qos.txt` (transient_local exit=0, volatile exit=124); `check_practice.py PR06`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
