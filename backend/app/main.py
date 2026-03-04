from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.webhooks import router as webhook_router
from app.api.events import router as events_router

app = FastAPI(
    title="IoT Monitor",
    version="0.1.0",
    description="IoT sensor monitoring service — test task",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(events_router, prefix="/api", tags=["events"])


@app.get("/health")
async def health():
    return {"status": "ok"}
