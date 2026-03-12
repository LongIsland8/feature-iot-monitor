from celery import Celery

celery_app = Celery(
    "iot_monitor",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)


celery_app.autodiscover_tasks(["app.tasks"])
