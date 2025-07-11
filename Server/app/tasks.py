from .ai import pddl as planner
from .db import timeseriesdb as tdb

import threading
import time
import json
import redis
import requests
import datetime

from app.utils.config import load_config
from app.utils.rabbitmq_helper import RabbitMQHelper
from app.db.sqldb import insert_weather_forecast

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
LOCK_EXPIRE = 60  # seconds

BATCH_SIZE = 50
BATCH_TIMEOUT = 5  # seconds

NOTIFICATIONS_KEY = "latest_notifications"
CURRENT_STATES = "current_states"
RAIN_HOURS = "rain_hours"


class QueueConsumerThread(threading.Thread):
    def __init__(self, stop_event, queue_name, process_func, batch_mode=False):
        super().__init__()
        self.stop_event = stop_event
        self.queue_name = queue_name
        self.process_func = process_func
        self.batch_mode = batch_mode

    def run(self):
        with RabbitMQHelper() as helper:
            helper.declare_queue(self.queue_name)
            channel = helper.channel

            batch = []
            last_batch_time = time.time()

            def on_message(ch, method, properties, body):
                nonlocal batch, last_batch_time
                msg = body.decode()
                if self.batch_mode:
                    batch.append(msg)
                    if len(batch) >= BATCH_SIZE or (time.time() - last_batch_time) > BATCH_TIMEOUT:
                        self.process_func(batch)
                        batch = []
                        last_batch_time = time.time()
                else:
                    self.process_func(msg)

            channel.basic_consume(queue=self.queue_name, on_message_callback=on_message, auto_ack=True)
            print(f"RabbitMQ consumer started on queue: {self.queue_name}")

            try:
                while not self.stop_event.is_set():
                    channel.connection.process_data_events(time_limit=1)
            except Exception as e:
                print(f"QueueConsumerThread ({self.queue_name}) encountered an error: {e}")
            finally:
                print(f"QueueConsumerThread ({self.queue_name}) cleaning up...")

# Thread management
consumer_threads = {}
consumer_stop_events = {}

def start_consumer(queue_name, process_func, batch_mode=False):
    stop_event = threading.Event()
    thread = QueueConsumerThread(stop_event, queue_name, process_func, batch_mode)
    consumer_threads[queue_name] = thread
    consumer_stop_events[queue_name] = stop_event
    thread.start()

def stop_consumer(queue_name):
    stop_event = consumer_stop_events.get(queue_name)
    thread = consumer_threads.get(queue_name)
    if stop_event:
        stop_event.set()
    if thread:
        thread.join(timeout=10)
        print(f"{queue_name} consumer thread stopped.")

# Processing functions
def process_sensor_batch(batch):
    print(f"Processing sensor batch: {batch}")
    dict_batch = [json.loads(msg) for msg in batch]
    tdb.write_sensor_data(dict_batch)

def process_state_message(msg):
    print(f"Processing state message: {msg}")
    try:
        state_dict = json.loads(msg)
        tdb.write_state_data(state_dict)
        redis_client.set(CURRENT_STATES, msg)
    except Exception as e:
        print(f"Error processing state message: {e}")

# Start/stop helpers for each queue
def start_rabbitmq_batch_consumer():
    config = load_config()
    queue_name = config["rabbitmq"].get("sensor_queue", "sensor_queue")
    start_consumer(queue_name, process_sensor_batch, batch_mode=True)

def stop_rabbitmq_batch_consumer():
    config = load_config()
    queue_name = config["rabbitmq"].get("sensor_queue", "sensor_queue")
    stop_consumer(queue_name)

def start_rabbitmq_state_consumer():
    config = load_config()
    queue_name = config["rabbitmq"].get("states_queue", "states_queue")
    start_consumer(queue_name, process_state_message, batch_mode=False)

def stop_rabbitmq_state_consumer():
    config = load_config()
    queue_name = config["rabbitmq"].get("states_queue", "states_queue")
    stop_consumer(queue_name)

def long_running_task(x, y):
    lock_id = "long_running_task_lock"
    have_lock = False
    try:
        have_lock = redis_client.set(lock_id, "true", nx=True, ex=LOCK_EXPIRE)
        if not have_lock:
            print("Task is already running. Skipping this run.")
            return None
        data = tdb.get_data()
        plan_id, parsed_plan, notifications = planner.insert_problem(data)
        print("Inserted Plan: " + str(plan_id))

        # Store notifications in Redis
        if notifications:
            redis_client.set(NOTIFICATIONS_KEY, json.dumps(notifications))
            
        redis_client.set(RAIN_HOURS, json.dumps(data['fluents']['hours_until_rain']))

        rabbitmq = load_config()["rabbitmq"]
        planner_queue = rabbitmq.get("planner_queue", "planner_queue")
        with RabbitMQHelper() as helper:
            helper.send_message(planner_queue, json.dumps(parsed_plan))
            print(f"Sent plan dict to queue {planner_queue}: {parsed_plan}")

        return x + y
    finally:
        if have_lock:
            redis_client.delete(lock_id)

def fetch_weather_forecast():
    url = "https://api.open-meteo.com/v1/forecast?latitude=48.7428207&longitude=9.1012773&hourly=rain,precipitation,precipitation_probability&timezone=auto&forecast_days=1"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        insert_weather_forecast(data)
        tdb.insert_hours_until_rain(data)
        print("Inserted Weather Data Successfully")
    except Exception as e:
        print(f"Failed to fetch weather forecast: {e}")

def reset_notifications():
     redis_client.delete(NOTIFICATIONS_KEY)