from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("/", response_model=list[schemas.SensorEventResponse])
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(models.event.SensorEvent).offset(skip).limit(limit).all()
    return events
