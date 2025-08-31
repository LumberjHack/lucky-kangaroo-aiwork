import os
from celery import Celery

BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
BACKEND_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery = Celery('lucky_kangaroo', broker=BROKER_URL, backend=BACKEND_URL)

@celery.task
def ping(task_id: str):
    return {"task_id": task_id, "pong": True}
