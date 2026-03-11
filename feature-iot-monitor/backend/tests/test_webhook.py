# backend/tests/test_webhook.py

import json
from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy import select

from app.models.event import SensorEvent
from app.database import SessionLocal


def test_valid_webhook_returns_200_with_task_id(client, mock_celery):
    data = {
        "sensor_id": "test-sensor",
        "location": "Test Room",
        "temperature": 25.0,
        "humidity": 60.0,
        "timestamp": "2026-03-11T12:00:00Z"
    }

    response = client.post("/webhooks/sensor", json=data)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "accepted"
    assert "task_id" in json_response
    mock_celery.assert_called_once_with(data)


def test_invalid_webhook_data_returns_422(client):
    invalid_data = {
        "sensor_id": "test-sensor",
        "temperature": "not_a_number",
        "humidity": 60.0,
        "timestamp": "2026-03-11T12:00:00Z"
    }

    response = client.post("/webhooks/sensor", json=invalid_data)
    assert response.status_code == 422


def test_celery_successful_processing_saves_to_db(db_session, mocker):
    from app.tasks.process import process_sensor_event

    event_data = {
        "sensor_id": "db-test-sensor",
        "location": "DB Room",
        "temperature": 40.0,
        "humidity": 70.0,
        "timestamp": "2026-03-11T12:00:00Z"
    }

    mocker.patch("app.tasks.telegram.send_telegram_notification.delay")

    result = process_sensor_event(event_data)

    assert result["severity"] == "warning"
    assert result["notification_sent"] is False

    saved = db_session.execute(
        select(SensorEvent).where(SensorEvent.sensor_id == "db-test-sensor")
    ).scalar_one_or_none()

    assert saved is not None
    assert saved.temperature == 40.0
    assert saved.severity == "warning"


def test_celery_retry_on_telegram_failure(mocker):
    from app.tasks.process import process_sensor_event
    from celery.exceptions import Retry

    event_data = {
        "sensor_id": "retry-sensor",
        "location": "Retry Room",
        "temperature": 55.0,
        "humidity": 80.0,
        "timestamp": "2026-03-11T12:00:00Z"
    }

    
    mocker.patch("app.tasks.telegram.send_telegram_notification.delay", side_effect=Exception("Network error"))

    with patch("app.tasks.process.process_sensor_event.retry") as mock_retry:
        mock_retry.side_effect = Retry()
        try:
            process_sensor_event(event_data)
        except Retry:
            pass

        mock_retry.assert_called()


def test_severity_classification_based_on_rules_json():
    from app.tasks.process import classify_severity

    import os
    import json
    rules_path = os.path.join(os.path.dirname(__file__), "..", "rules.json")
    with open(rules_path) as f:
        rules_data = json.load(f)
        rules = rules_data["rules"]  

    severity = classify_severity(45.0, 0, rules)
    assert severity == "high"

    severity = classify_severity(30.0, 0, rules)
    assert severity == "normal"

    critical_rule = next((r for r in rules if r["name"] == "critical"), None)
    if critical_rule:
        severity = classify_severity(critical_rule["threshold"] + 1, 0, rules)
        assert severity == "critical"