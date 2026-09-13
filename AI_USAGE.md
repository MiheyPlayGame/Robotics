# Декларация использования ИИ

- Использован ИИ: да
- Модель и версия: Cursor Grok 4.6 (агент в IDE)
- Среда или интерфейс агента: Cursor, чат в репозитории `C:\Users\MPG\NSU\Robotics`
- Затронутые компоненты: git-репозиторий и GitHub remote; `.gitignore`; `.github/workflows/ci.yml` и `.gitverse/workflows/ci.yml`; `README.md`; каталог `evidence/pr01/` (`doctor.txt`, `graph.md`, `environment.json`, `report.json`, `pose-broken.txt`, `pose-fixed.txt`); `AI_USAGE.md`
- Характер помощи: разбор инструкций курса; адаптация команд Unix (`mkdir -p`, `curl -fLO`, `timeout`) к Windows/cmd; запуск turtlesim/CLI и съём наблюдений; заполнение отчёта и двух commit
- Как результат был проверен независимо: SHA-256 архива course-kit совпал с опубликованным digest; `ros2 doctor`, `node list`, `topic list`, `topic echo`, `topic hz` выполнены в локальной ROS 2 Lyrical; частота позы ≈62.5 Гц; разрыв домена 17 дал timeout 124, восстановление в 16 — позу и exit=0; `python -m json.tool` и `check_practice.py PR01` запускаются по файлам сдачи

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
