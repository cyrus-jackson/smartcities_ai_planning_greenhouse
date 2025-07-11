import time
import json
import pika

import state_constants as states
from config import load_config, TEMPERATURE_GPIO, WATER_TANK_GPIO, WATER_TANK_HEIGHT, SOIL_MOISTURE_GPIO

from temperature_sensor import TemperatureSensor
from water_tank_level_sensor import WaterTankLevelSensor
from soil_moisture_sensor import SoilMoistureSensor

class HumiditySensor:
    def get_reading(self):
        return 55  # percent
    

def sensor_loop(rabbitmq_client, interval=5):
    """
    Main sensor loop that reads all sensors and publishes data to RabbitMQ
    
    Args:
        rabbitmq_client: RabbitMQ client instance
        interval: Time interval between sensor readings (seconds)
    """
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
    temperature_sensor = TemperatureSensor(analog_port=TEMPERATURE_GPIO)  # A0
    soil_moisture_sensor = SoilMoistureSensor(analog_port=SOIL_MOISTURE_GPIO) # A1
    water_level_sensor = WaterTankLevelSensor(digital_port=WATER_TANK_GPIO, tank_height=WATER_TANK_HEIGHT)  # D4, 100cm tank
    
    state_manager = rabbitmq_client.state_manager

    print("Starting sensor loop...")
    print(f"Sensor reading interval: {interval} seconds")
    print("=" * 50)
    
    while True:
        try:
            # Read all sensors
            humidity = float(humidity_sensor.get_reading())
            temperature = float(temperature_sensor.get_reading())
            soil_moisture = float(soil_moisture_sensor.get_reading())
            water_level = float(water_level_sensor.get_reading())
            
            # Get current state and plan ID
            state = state_manager.get_state()
            plan_id = state.get(states.PLAN_ID, None)
            
            # Create message payload
            message = {
                states.HUMIDITY: humidity,
                states.TEMPERATURE: temperature,
                states.SOIL_MOISTURE: soil_moisture,
                states.WATER_LEVEL: water_level,
                states.PLAN_ID: plan_id
            }
            
            print(f"Sending sensor data: {message}")
            
            # Publish to RabbitMQ
            channel.basic_publish(
                exchange='',
                routing_key=rabbitmq["sensor_queue"],
                body=json.dumps(message).encode()
            )
            
        except Exception as e:
            print(f"Error in sensor loop: {e}")
            
        time.sleep(interval)


def test_all_sensors():
    """Test all sensors individually"""
    print("Testing All Grove Sensors...")
    print("=" * 50)
    
    # Test Humidity Sensor
    print("1. Testing Humidity Sensor:")
    humidity_sensor = HumiditySensor()
    for i in range(3):
        humidity = humidity_sensor.get_reading()
        print(f"   Reading {i+1}: {humidity}%")
        time.sleep(1)
    print()
    
    # Test Temperature Sensor
    print("2. Testing Temperature Sensor (A0):")
    temperature_sensor = TemperatureSensor(analog_port=TEMPERATURE_GPIO)
    for i in range(3):
        temp = temperature_sensor.get_reading()
        print(f"   Reading {i+1}: {temp}°C")
        time.sleep(1)
    print()
    
    # Test Soil Moisture Sensor
    print("3. Testing Soil Moisture Sensor (A1):")
    soil_sensor = SoilMoistureSensor(analog_port=SOIL_MOISTURE_GPIO)
    for i in range(3):
        moisture = soil_sensor.get_reading()
        print(f"   Reading {i+1}: {moisture}%")
        time.sleep(1)
    print()
    
    # Test Water Level Sensor
    print("4. Testing Water Level Sensor (D4):")
    water_sensor = WaterTankLevelSensor(digital_port=WATER_TANK_GPIO, tank_height=WATER_TANK_HEIGHT)
    for i in range(3):
        level = water_sensor.get_reading()
        distance = water_sensor.get_distance()
        print(f"   Reading {i+1}: {level}% (Distance: {distance}cm)")
        time.sleep(1)
    print()
    
    print("All sensor tests completed!")


def interactive_sensor_test():
    
    print("Interactive Sensor Test Interface")
    print("=" * 40)
    
    # Initialize sensors
    humidity_sensor = HumiditySensor()
    temperature_sensor = TemperatureSensor(analog_port=0)
    soil_sensor = SoilMoistureSensor(analog_port=1)
    water_sensor = WaterTankLevelSensor(digital_port=4, tank_height=100)
    
    print("Available commands:")
    print("  'humidity' - Read humidity sensor")
    print("  'temperature' - Read temperature sensor")
    print("  'soil' - Read soil moisture sensor")
    print("  'water' - Read water level sensor")
    print("  'all' - Read all sensors")
    print("  'continuous' - Continuous reading (Ctrl+C to stop)")
    print("  'quit' - Exit")
    print()
    
    while True:
        try:
            command = input("Enter command: ").strip().lower()
            
            if command == 'humidity':
                humidity = humidity_sensor.get_reading()
                print(f"Humidity: {humidity}%")
                
            elif command == 'temperature':
                temp = temperature_sensor.get_reading()
                print(f"Temperature: {temp}°C")
                
            elif command == 'soil':
                moisture = soil_sensor.get_reading()
                print(f"Soil Moisture: {moisture}%")
                
            elif command == 'water':
                level = water_sensor.get_reading()
                distance = water_sensor.get_distance()
                print(f"Water Level: {level}% (Distance: {distance}cm)")
                
            elif command == 'all':
                print("Reading all sensors...")
                humidity = humidity_sensor.get_reading()
                temp = temperature_sensor.get_reading()
                moisture = soil_sensor.get_reading()
                level = water_sensor.get_reading()
                
                print(f"Humidity: {humidity}%")
                print(f"Temperature: {temp}°C")
                print(f"Soil Moisture: {moisture}%")
                print(f"Water Level: {level}%")
                
            elif command == 'continuous':
                print("Starting continuous reading (Ctrl+C to stop)...")
                try:
                    while True:
                        humidity = humidity_sensor.get_reading()
                        temp = temperature_sensor.get_reading()
                        moisture = soil_sensor.get_reading()
                        level = water_sensor.get_reading()
                        
                        print(f"H:{humidity}% T:{temp}°C S:{moisture}% W:{level}%")
                        time.sleep(2)
                except KeyboardInterrupt:
                    print("Continuous reading stopped")
                    
            elif command == 'quit' or command == 'exit':
                print("Exiting...")
                break
                
            else:
                print("Unknown command. Use: humidity, temperature, soil, water, all, continuous, quit")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    print("Grove Environmental Sensors Test Program")
    print("Make sure your sensors are connected:")
    print("- Grove Temperature Sensor -> A0")
    print("- Grove Soil Moisture Sensor -> A1") 
    print("- Grove Ultrasonic Ranger v2.0 -> D4")
    print("- Humidity Sensor -> Software only (static value)")
    print("=" * 50)
    
    print("Test modes:")
    print("  1. Quick test all sensors")
    print("  2. Interactive sensor test")
    print("  3. Exit")
    
    try:
        choice = input("Select test mode (1-3): ").strip()
        
        if choice == '1':
            test_all_sensors()
        elif choice == '2':
            interactive_sensor_test()
        elif choice == '3':
            print("Exiting...")
        else:
            print("Invalid choice. Running quick test...")
            test_all_sensors()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")
