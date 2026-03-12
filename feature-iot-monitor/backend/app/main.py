# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints.events import router as events_router
from app.api.webhooks import router as webhook_router

app = FastAPI(
    title="IoT Monitor",
    version="0.1.0",
    description="IoT sensor monitoring service — test task",
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Вебхуки: POST /webhooks/sensor
app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])

# События: GET /api/events
app.include_router(events_router)  # ✅ Без дополнительного prefix!

@app.get("/health")
def health():
    return {"status": "ok"}