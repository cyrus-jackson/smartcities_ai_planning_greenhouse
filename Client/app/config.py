import json
import os

# A0
TEMPERATURE_GPIO = 0

# A1
SOIL_MOISTURE_GPIO = 1

# D2
FAN_GPIO = 2

# Water Pump Relay GPIO. This is not a Groove Relay. 
WATER_PUMP_GPIO = 18

# D4
WATER_TANK_GPIO = 4
# In Centimeters
WATER_TANK_HEIGHT = 100


# D3
SERVO_1_GPIO = 3
# D8
SERVO_2_GPIO = 8


DEFAULT_CONFIG = {
    "rabbitmq": {
        "host": os.environ.get("RABBITMQ_HOST", "localhost"),
        "port": int(os.environ.get("RABBITMQ_PORT", "5672")),
        "username": os.environ.get("RABBITMQ_USERNAME", "guest"),
        "password": os.environ.get("RABBITMQ_PASSWORD", "guest"),
        "planner_queue": os.environ.get("RABBITMQ_PLANNER_QUEUE", "planner_queue"),
        "sensor_queue": os.environ.get("RABBITMQ_SENSOR_QUEUE", "sensor_queue"),
        "states_queue": os.environ.get("RABBITMQ_STATES_QUEUE", "states_queue")
    }
}

def load_config(config_path="config.json"):
    """
    Load configuration from file or environment variables.
    Priority: config file > environment variables > defaults
    """
    config = DEFAULT_CONFIG.copy()
    
    # Load from file if it exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            file_config = json.load(f)
            # Merge file config with defaults
            config["rabbitmq"].update(file_config.get("rabbitmq", {}))
    
    # Override with environment variables (highest priority)
    config["rabbitmq"]["host"] = os.environ.get("RABBITMQ_HOST", config["rabbitmq"]["host"])
    config["rabbitmq"]["port"] = int(os.environ.get("RABBITMQ_PORT", str(config["rabbitmq"]["port"])))
    config["rabbitmq"]["username"] = os.environ.get("RABBITMQ_USERNAME", config["rabbitmq"]["username"])
    config["rabbitmq"]["password"] = os.environ.get("RABBITMQ_PASSWORD", config["rabbitmq"]["password"])
    
    return config