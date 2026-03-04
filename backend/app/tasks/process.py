"""
Celery-задача обработки событий от датчиков.

TODO: Реализовать задачу process_sensor_event
- Определить severity по правилам из rules.json
- Если critical — отправить уведомление в Telegram (mock API)
- Сохранить событие в PostgreSQL
- При ошибке Telegram — retry до 3 раз с экспоненциальной задержкой
"""

from app.tasks import celery_app


# TODO: реализовать задачу
