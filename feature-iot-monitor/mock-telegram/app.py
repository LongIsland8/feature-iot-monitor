# mock-telegram/app.py

from fastapi import FastAPI, HTTPException
import random
from typing import List, Dict

app = FastAPI()

# Храним сообщения в памяти
messages: List[Dict[str, str]] = []

@app.post("/bot{token}/sendMessage")
async def send_message(token: str, chat_id: int, text: str):
    if random.random() < 0.1:  # 10% шанс ошибки
        raise HTTPException(status_code=500, detail="Internal Server Error")
    messages.append({"chat_id": chat_id, "text": text})
    return {"ok": True, "result": {"message_id": len(messages)}}

@app.get("/bot{token}/messages")
async def get_messages(token: str):
    return {"messages": messages}

@app.get("/")
def home():
    return {
        "message": "Mock Telegram Bot API is running",
        "endpoints": [
            "POST /bot{token}/sendMessage",
            "GET /bot{token}/messages"
        ]
    }