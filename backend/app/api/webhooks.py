"""
Webhook endpoint для приёма данных от IoT-датчиков.

TODO: Реализовать обработчик POST /webhooks/sensor
- Принять JSON с полями: sensor_id, location, temperature, humidity, timestamp
- Валидировать данные через Pydantic
- Отправить задачу в Celery-очередь
- Вернуть {"status": "accepted", "task_id": "..."}
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any
from ..tasks.process import process_sensor_event

# Создаём роутер для webhook-ов
router = APIRouter()

# Pydantic-модель для валидации входящих данных
class SensorData(BaseModel):
    sensor_id: str
    location: str
    temperature: float
    humidity: float
    timestamp: str  # Формат ISO 8601, например: "2026-03-04T10:30:00Z"

# Эндпоинт: POST /webhooks/sensor
@router.post("/webhooks/sensor")
async def webhook_sensor(data: SensorData) -> dict[str, Any]:
    # Отправляем задачу в Celery (асинхронно)
    task = process_sensor_event.delay(data.dict())
    # Возвращаем статус и ID задачи
    return {"status": "accepted", "task_id": task.id}


# TODO: реализовать эндпоинт
