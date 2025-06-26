import time
import json

class HumiditySensor:
    def get_reading(self):
        # Simulate reading humidity (constant value for now)
        return 55  # percent

class TemperatureSensor:
    def get_reading(self):
        # Simulate reading temperature (constant value for now)
        return 22  # Celsius

def sensor_loop(rabbitmq_client, interval=10):
    humidity_sensor = HumiditySensor()
    temperature_sensor = TemperatureSensor()
    while True:
        humidity = humidity_sensor.get_reading()
        temperature = temperature_sensor.get_reading()
        message = {
            "humidity": humidity,
            "temperature": temperature
        }
        print(f"Sending sensor data: {message}")
        rabbitmq_client.send_to_sensor_queue(json.dumps(message))
        time.sleep(interval)