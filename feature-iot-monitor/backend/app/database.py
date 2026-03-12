# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Получаем URL из переменной окружения или используем дефолтный
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/iot_monitor")

# Создаём engine
engine = create_engine(DATABASE_URL)

# Создаём SessionLocal (фабрика сессий)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Зависимость для внедрения сессии в FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()