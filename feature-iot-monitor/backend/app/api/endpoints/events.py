# backend/app/api/endpoints/events.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.models.event import SensorEvent
from app.schemas.event import SensorEventResponse
from app.database import get_db

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/", response_model=list[SensorEventResponse])
def get_events(
    db: Session = Depends(get_db),
    severity: str | None = Query(None, description="Filter by severity: normal, warning, critical"),
    sensor_id: str | None = Query(None, description="Filter by sensor ID"),
    date_from: str | None = Query(None, description="ISO format, e.g. 2026-03-04T00:00:00"),
    date_to: str | None = Query(None, description="ISO format"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Получить список событий с фильтрацией, пагинацией и сортировкой.
    Новые события — в начале.
    """
    try:
        query = db.query(SensorEvent)

        # 🔍 Фильтрация
        if severity:
            query = query.filter(SensorEvent.severity == severity)
        if sensor_id:
            query = query.filter(SensorEvent.sensor_id == sensor_id)
        if date_from:
            dt = datetime.fromisoformat(date_from)
            query = query.filter(SensorEvent.created_at >= dt)
        if date_to:
            dt = datetime.fromisoformat(date_to)
            query = query.filter(SensorEvent.created_at <= dt)

        # ⏫ Сортировка: новые первыми
        # 📄 Пагинация
        events = query.order_by(desc(SensorEvent.created_at)).offset(offset).limit(limit).all()

        print(f"✅ Найдено событий: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Ошибка при получении событий: {e}")
        raise