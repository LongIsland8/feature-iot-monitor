# backend/app/tasks/process.py

from celery import shared_task
from celery.exceptions import Retry
from app.database import SessionLocal
from app.models.event import SensorEvent
import json
import os
from typing import List, Dict, Any


def classify_severity(temperature: float, humidity: float, rules: List[Dict[str, Any]]) -> str:
    """
    Classify event severity based on JSON rules.

    Expected rule format in rules.json:
    {
        "id": "...",
        "name": "high",                # human‑readable name
        "description": "...",
        "condition": {
            "field": "temperature",    # "temperature" | "humidity"
            "operator": ">",           # one of >, >=, <, <=, ==
            "value": 30
        },
        "severity": "high",            # severity value to return
        "notification": true
    }
    """
    metrics = {
        "temperature": temperature,
        "humidity": humidity,
    }

    result = "normal"

    for rule in rules:
        condition = rule.get("condition") or {}
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        if field not in metrics or operator is None or value is None:
            continue

        current = metrics[field]
        matched = False

        if operator == ">":
            matched = current > value
        elif operator == ">=":
            matched = current >= value
        elif operator == "<":
            matched = current < value
        elif operator == "<=":
            matched = current <= value
        elif operator == "==":
            matched = current == value

        if matched:
            # Prefer explicit severity, fall back to name
            result = rule.get("severity") or rule.get("name") or result
            break

    return result


@shared_task
def process_sensor_event(event_data: dict):
    """
    Обрабатывает событие датчика:
    - классифицирует severity
    - сохраняет в БД
    - отправляет уведомление при high/critical
    """
    from app.tasks.telegram import send_telegram_notification

    db = SessionLocal()
    try:
        # Загружаем правила
        rules_path = "/app/rules.json"
        with open(rules_path) as f:
            rules_data = json.load(f)
            rules = rules_data["rules"]

        # Классификация
        severity = classify_severity(
            event_data["temperature"],
            event_data["humidity"],
            rules,
        )

        # Сохраняем событие (только поддерживаемые полями модели атрибуты)
        db_event = SensorEvent(
            sensor_id=event_data["sensor_id"],
            location=event_data["location"],
            temperature=event_data["temperature"],
            humidity=event_data["humidity"],
            severity=severity,
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        # Базовые флаги результата
        notification_sent = False
        error_message = None

        # Отправляем уведомление только для серьёзных событий
        if severity in ["high", "critical"]:
            try:
                send_telegram_notification.delay(
                    chat_id=12345,
                    text=(
                        f"🚨 Alert: {severity.upper()} severity event from {event_data['sensor_id']}\n"
                        f"Location: {event_data['location']}\n"
                        f"Temp: {event_data['temperature']}°C\n"
                        f"Humidity: {event_data['humidity']}%"
                    ),
                )
                notification_sent = True
            except Exception as e:
                # При ошибке отправки уведомления повторяем задачу
                error_message = str(e)
                raise process_sensor_event.retry(exc=e, countdown=5)

        return {
            "id": db_event.id,
            "severity": severity,
            "notification_sent": notification_sent,
            "error_message": error_message,
        }

    finally:
        db.close()