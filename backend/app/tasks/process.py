"""
Celery-задача обработки событий от датчиков.

TODO: Реализовать задачу process_sensor_event
- Определить severity по правилам из rules.json
- Если critical — отправить уведомление в Telegram (mock API)
- Сохранить событие в PostgreSQL
- При ошибке Telegram — retry до 3 раз с экспоненциальной задержкой
"""

import json
import requests
from celery import shared_task
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.config import DATABASE_URL, TELEGRAM_TOKEN, CHAT_ID

# === Настройка SQLAlchemy (вне FastAPI) ===
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# === Загрузка правил из rules.json ===
def load_rules():
    with open("rules.json") as f:
        return json.load(f)

rules = load_rules()
TEMPERATURE_CRITICAL = rules.get("temperature_critical", 50)
HUMIDITY_CRITICAL = rules.get("humidity_critical", 95)
TEMPERATURE_WARNING = rules.get("temperature_warning", 35)
HUMIDITY_WARNING = rules.get("humidity_warning", 80)

# === URL для Telegram mock ===
TELEGRAM_URL = f"http://mock-telegram:8001/bot{TELEGRAM_TOKEN}/sendMessage"

# === Основная Celery-задача ===
@shared_task(bind=True)
def process_sensor_event(self, data):
    """
    Обрабатывает событие с датчика:
    - Определяет severity
    - Сохраняет в БД
    - Отправляет уведомление при critical (с retry)
    """
    db = SessionLocal()
    try:
        temp = data["temperature"]
        hum = data["humidity"]

        # Определение уровня серьёзности
        if temp > TEMPERATURE_CRITICAL or hum > HUMIDITY_CRITICAL:
            severity = "critical"
        elif temp > TEMPERATURE_WARNING or hum > HUMIDITY_WARNING:
            severity = "warning"
        else:
            severity = "normal"

        # Импортируем модель здесь, чтобы избежать циклических импортов
        from app.models.event import SensorEvent

        # Создаём объект события
        event = SensorEvent(
            sensor_id=data["sensor_id"],
            location=data["location"],
            temperature=temp,
            humidity=hum,
            severity=severity,
            notification_sent=False,
            error_message=None,
            created_at=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        # Если критическая ситуация — отправляем в Telegram
        if severity == "critical":
            message = f"🚨 CRITICAL: {data['sensor_id']} ({data['location']}) — {temp}°C"

            # Попытки отправки с экспоненциальной задержкой
            for attempt in range(3):
                try:
                    response = requests.post(TELEGRAM_URL, json={"chat_id": CHAT_ID, "text": message}, timeout=5)
                    if response.status_code == 200:
                        event.notification_sent = True
                        db.commit()
                        break
                    else:
                        raise Exception(f"Telegram error: {response.status_code}")
                except Exception as e:
                    if attempt == 2:  # Последняя попытка
                        event.error_message = str(e)
                        db.commit()
                        raise
                    # Ждём перед повтором: 1, 2, 4 секунды
                    time.sleep(2 ** attempt)
            # Конец retry-логики

        return {"status": "processed", "event_id": event.id, "severity": severity}

    except Exception as exc:
        db.rollback()
        # Пробрасываем исключение, чтобы Celery мог сделать retry
        raise self.retry(exc=exc, countdown=2 ** self.request.retries) from exc
    finally:
        db.close()


# TODO: реализовать задачу
