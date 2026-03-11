# backend/app/config.py

import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/iot_monitor")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL", "http://mock-telegram:8001")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "test-token")
CHAT_ID = os.getenv("CHAT_ID", "123456")