from celery import Celery
from celery.schedules import crontab

from app.core.config import settings


CELERY_BROKER_URL = settings.get_rabbitmq_url()


celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend="rpc://"
)


celery_app.conf.update(
    task_track_started=True,
    timezone="UTC",
    result_expires=3600,
)


celery_app.autodiscover_tasks(["app.features.books"])


celery_app.conf.beat_schedule = {
    "check-abandoned-books-every-day": {
        "task": "app.features.books.tasks.check_abandoned_books",
        "schedule": crontab(hour=0, minute=0)
    }
}