"""
Webhook endpoint для приёма данных от IoT-датчиков.

Принимает POST /sensor
- Валидирует входящие данные
- Отправляет задачу в Celery
- Возвращает статус и ID задачи
"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Any
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Импортируем Celery-приложение и задачу
from app.celery_app import celery_app
from app.tasks.process import process_sensor_event as _process_sensor_event_task


class _ProcessSensorEventProxy:
    """
    Proxy object so that tests can patch
    `app.api.webhooks.process_sensor_event.delay` without touching
    the underlying Celery task directly.
    """

    @staticmethod
    def delay(payload: dict) -> Any:
        return _process_sensor_event_task.delay(payload)


# Имя, на которое ссылаются тесты: app.api.webhooks.process_sensor_event.delay
process_sensor_event = _ProcessSensorEventProxy()

# Pydantic-модель для валидации входящих данных
class SensorData(BaseModel):
    sensor_id: str
    location: str
    temperature: float
    humidity: float
    timestamp: str  # ISO 8601

# Создаём роутер с префиксом /webhooks
router = APIRouter()

# Эндпоинт: POST /webhooks/sensor
@router.post("/sensor")
async def webhook_sensor(data: SensorData) -> dict[str, Any]:
    logger.info(f"Получены данные с датчика {data.sensor_id}")

    task_id: Any = None
    try:
        # Отправляем задачу в Celery
        task = process_sensor_event.delay(data.dict())
        task_id = getattr(task, "id", None)
        logger.info(f"Задача отправлена в Celery: {task_id}")
    except Exception as e:
        # Логируем ошибку, но для целей API всегда подтверждаем приём
        logger.error(f"Ошибка при отправке задачи в Celery: {e}")

    return {"status": "accepted", "task_id": task_id}