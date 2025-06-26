from .celery_worker import celery
from .ai import pddl as planner
from .db import timeseriesdb as tdb

import pika
import redis
import time
from app.utils.config import load_config

# Configure Redis connection (adjust host/port/db as needed)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

LOCK_EXPIRE = 60  # seconds

@celery.task(bind=True)
def long_running_task(self, x, y):
    lock_id = "long_running_task_lock"
    have_lock = False
    try:
        # Try to acquire the lock
        have_lock = redis_client.set(lock_id, "true", nx=True, ex=LOCK_EXPIRE)
        if not have_lock:
            print("Task is already running. Skipping this run.")
            return None
        data = tdb.get_data()
        time.sleep(5)
        planner.insert_problem(data)
        print("The Result: " + str(x + y))
        return x + y
    finally:
        # Only release the lock if we acquired it
        if have_lock:
            redis_client.delete(lock_id)
            # Schedule the next run after 50 seconds
            self.apply_async(args=[x, y], countdown=150)



BATCH_SIZE = 10
BATCH_TIMEOUT = 5  # seconds

@celery.task
def rabbitmq_batch_consumer():
    config = load_config()
    rabbitmq = config["rabbitmq"]
    queue_name = rabbitmq.get("sensor_queue", "sensor_queue")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq.get("host", "localhost"),
            port=rabbitmq.get("port", 5672),
            credentials=pika.PlainCredentials(
                rabbitmq.get("username", "guest"),
                rabbitmq.get("password", "guest")
            )
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    batch = []
    last_batch_time = time.time()

    def on_message(ch, method, properties, body):
        nonlocal batch, last_batch_time
        batch.append(body.decode())
        if len(batch) >= BATCH_SIZE or (time.time() - last_batch_time) > BATCH_TIMEOUT:
            process_batch(batch)
            batch = []
            last_batch_time = time.time()

    def process_batch(batch):
        print(f"Processing batch: {batch}")
        # You can trigger another Celery task here if needed

    channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=True)
    print(f"RabbitMQ batch consumer started on queue: {queue_name}")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()