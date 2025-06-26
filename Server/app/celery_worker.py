from celery import Celery

celery = Celery(
    "app",
    broker="pyamqp://guest:guest@localhost:5672//",
    backend="rpc://",
    include=['app.tasks']
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)