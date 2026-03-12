# backend/app/schemas/event.py

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class SensorEventBase(BaseModel):
    sensor_id: str
    location: str
    temperature: float
    humidity: float
    severity: str
    notification_sent: bool
    error_message: Optional[str]
    created_at: datetime


class SensorEventCreate(SensorEventBase):
    pass


class SensorEventResponse(SensorEventBase):
    id: int

    class Config:
        from_attributes = True