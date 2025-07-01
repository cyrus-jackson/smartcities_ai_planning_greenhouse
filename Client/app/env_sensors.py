import time
import json
import pika

import state_constants as states
from config import load_config


class HumiditySensor:
    def get_reading(self):
        
        return 55  # percent

class TemperatureSensor:
    def get_reading(self):
        
        return 52  # Celsius
    
class SoilMoistureSensor:
    def get_reading(self):
        # Simulate reading temperature (constant value for now)
        return 38  # Celsius

def sensor_loop(rabbitmq_client, interval=10):
    # Create a new connection and channel for this thread
    config = rabbitmq_client.config if hasattr(rabbitmq_client, 'config') else load_config()
    rabbitmq = config["rabbitmq"]
    credentials = pika.PlainCredentials(rabbitmq["username"], rabbitmq["password"])
    parameters = pika.ConnectionParameters(
        host=rabbitmq["host"],
        port=rabbitmq["port"],
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq["sensor_queue"])

    humidity_sensor = HumiditySensor()
    temperature_sensor = TemperatureSensor()
    soil_moisture_sensor = SoilMoistureSensor()
    state_manager = rabbitmq_client.state_manager

    while True:
        humidity = humidity_sensor.get_reading()
        temperature = temperature_sensor.get_reading()
        soil_moisture = soil_moisture_sensor.get_reading()
        state = state_manager.get_state()
        plan_id = state.get(states.PLAN_ID, None)
        message = {
            states.HUMIDITY: humidity,
            states.TEMPERATURE: temperature,
            states.SOIL_MOISTURE: soil_moisture,
            states.PLAN_ID: plan_id
        }
        print(f"Sending sensor data: {message}")
        channel.basic_publish(
            exchange='',
            routing_key=rabbitmq["sensor_queue"],
            body=json.dumps(message).encode()
        )
        time.sleep(interval)