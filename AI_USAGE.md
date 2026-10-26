# Декларация использования ИИ

## PR07

- Использован ИИ: да
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR07`
- Затронутые компоненты: `src/course_simulation/` (launch, bridge, cmd/odom adapters); `docker/`; `evidence/pr07/`; `.github/workflows/ci.yml`; `README.md`
- Характер помощи: разбор [ПР07](https://ros.lms.ci.nsu.ru/practices/pr07); каркас пакета и контракт адаптеров; Docker-путь Lyrical/Jetty вместо native Windows Gazebo
- Как результат был проверен независимо: pytest адаптеров; `check_practice.py PR07`; headless launch и bag в Docker (после установки Docker Desktop)

## PR06

- Использован ИИ: да
- Модель и версия: Cursor Composer (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`, ветка `PR06`
- Затронутые компоненты: `src/course_description/` (URDF/Xacro, launch); `evidence/pr06/`; `.github/workflows/ci.yml`; `README.md`
- Характер помощи: разбор [ПР06](https://ros.lms.ci.nsu.ru/practices/pr06); параметризация Ackermann по SDF kit; `robot_state_publisher`; QoS `/tf_static` transient_local vs volatile
- Как результат был проверен независимо: `pytest src/course_description/test`; xacro expand + разбор URDF; `tf-qos.txt` (transient_local exit=0, volatile exit=124); `check_practice.py PR06`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
