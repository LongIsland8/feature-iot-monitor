"""
SQLAlchemy модель для хранения событий датчиков.

TODO: Реализовать модель SensorEvent
- id (PK)
- sensor_id (str)
- location (str)
- temperature (float)
- humidity (float)
- severity (str): normal / warning / critical
- notification_sent (bool)
- error_message (str, nullable)
- created_at (datetime)
"""

# TODO: реализовать модель
# TODO: настроить Alembic для миграций

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SensorEvent(Base):
    __tablename__ = "sensor_events"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, nullable=False)
    location = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    severity = Column(String, nullable=False)  # normal / warning / critical
    notification_sent = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
