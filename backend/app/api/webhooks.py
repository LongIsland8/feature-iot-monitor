"""
Webhook endpoint для приёма данных от IoT-датчиков.

TODO: Реализовать обработчик POST /webhooks/sensor
- Принять JSON с полями: sensor_id, location, temperature, humidity, timestamp
- Валидировать данные через Pydantic
- Отправить задачу в Celery-очередь
- Вернуть {"status": "accepted", "task_id": "..."}
"""

from fastapi import APIRouter

router = APIRouter()


# TODO: реализовать эндпоинт
