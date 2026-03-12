# backend/app/tasks/telegram.py

from celery import shared_task
import httpx

@shared_task(bind=True, max_retries=3)
def send_telegram_notification(self, chat_id: int, text: str):
    """
    Отправляет уведомление в Telegram.
    Повторяет попытку при ошибке.
    """
    from app.core.config import settings

    try:
        response = httpx.post(
            f"{settings.TELEGRAM_API_URL}/bot123/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=5.0
        )
        response.raise_for_status()
        return {"status": "sent", "response": response.json()}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)  # ждём 60 секунд