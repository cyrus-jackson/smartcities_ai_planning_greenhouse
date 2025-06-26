import json
import os

DEFAULT_CONFIG = {
    "rabbitmq": {
        "host": "localhost",
        "port": 5672,
        "username": os.environ.get("RABBITMQ_USERNAME", "guest"),
        "password": os.environ.get("RABBITMQ_PASSWORD", "guest"),
        "planner_queue": "planner_queue",
        "sensor_queue": "sensor_queue"
    }
}

def load_config(config_path="config.json"):
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
        
        config["rabbitmq"]["username"] = os.environ.get("RABBITMQ_USERNAME", config["rabbitmq"].get("username", "guest"))
        config["rabbitmq"]["password"] = os.environ.get("RABBITMQ_PASSWORD", config["rabbitmq"].get("password", "guest"))
        return config
    return DEFAULT_CONFIG