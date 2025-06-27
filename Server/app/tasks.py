from .celery_worker import celery
from .ai import pddl as planner
from .db import timeseriesdb as tdb

import redis
import time
import json
from app.utils.config import load_config
from app.utils.rabbitmq_helper import RabbitMQHelper

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
        plan_id, parsed_plan = planner.insert_problem(data)
        print("Inserted Plan: " + str(plan_id))

        # Send the parsed plan dictionary to planner_queue using RabbitMQHelper
        rabbitmq = load_config()["rabbitmq"]
        planner_queue = rabbitmq.get("planner_queue", "planner_queue")
        RabbitMQHelper().send_message(planner_queue, json.dumps(parsed_plan))
        print(f"Sent plan dict to queue {planner_queue}: {parsed_plan}")

        return x + y
    finally:
        # Only release the lock if we acquired it
        if have_lock:
            redis_client.delete(lock_id)
            # Schedule the next run after 150 seconds
            self.apply_async(args=[x, y], countdown=100)

BATCH_SIZE = 10
BATCH_TIMEOUT = 5  # seconds

@celery.task
def rabbitmq_batch_consumer():
    config = load_config()
    rabbitmq = config["rabbitmq"]
    queue_name = rabbitmq.get("sensor_queue", "sensor_queue")

    helper = RabbitMQHelper()
    helper.declare_queue(queue_name)
    channel = helper.channel

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