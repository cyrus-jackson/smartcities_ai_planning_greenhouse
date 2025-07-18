import pika
import json
import threading
import state_constants as states

from config import load_config, FAN_GPIO, WATER_PUMP_GPIO
from state_manager import StateManager

from fan_module import FanModule
from water_pump_module import WaterPumpModule
from env_sensors import sensor_loop, HumiditySensor
from roof_module import RoofModule


class RabbitMQClient:
    def __init__(self, config=None):
        if config is None:
            config = load_config()
        rabbitmq = config["rabbitmq"]
        self.planner_queue = rabbitmq["planner_queue"]
        self.sensor_queue = rabbitmq["sensor_queue"]
        self.states_queue = rabbitmq.get("states_queue", "states_queue")
        credentials = pika.PlainCredentials(rabbitmq["username"], rabbitmq["password"])
        parameters = pika.ConnectionParameters(
            host=rabbitmq["host"],
            port=rabbitmq["port"],
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.planner_queue)
        self.channel.queue_declare(queue=self.sensor_queue)
        self.channel.queue_declare(queue=self.states_queue)
        self.state_manager = StateManager(self, self.states_queue)
        # Instantiate modules once and reuse
        self.fan = FanModule(self.state_manager, relay_port=FAN_GPIO)
        self.water_pump = WaterPumpModule(self.state_manager, gpio_pin=WATER_PUMP_GPIO, auto_shutoff_duration=6)
        self.roof = RoofModule(self.state_manager)
        self.humidity_sensor = HumiditySensor()

    def send_to_sensor_queue(self, message):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.sensor_queue,
            body=message.encode()
        )

    def start_consuming(self, callback):
        def on_message(ch, method, properties, body):
            try:
                msg = body.decode()
                print(f"Received: {msg}")
                actions = json.loads(msg)
                print(actions)
                self.state_manager.update_plan(actions[states.PLAN_ID]) if states.PLAN_ID in actions else None
                for act in actions:
                    if act == states.PLAN_ID:
                        continue
                    callback(actions[act], self)
                    
            except json.JSONDecodeError:
                print("Received message is not valid JSON.")
        self.channel.basic_consume(queue=self.planner_queue, on_message_callback=on_message, auto_ack=True)
        print("Waiting for messages. To exit press CTRL+C")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Pressed CTRL+C")
        finally:
            self.close()

    def close(self):
        # Clean shutdown of modules
        self.fan.cleanup()
        self.water_pump.cleanup()
        self.connection.close()

def invoke_action(action, client):
    print(f"Invoking action: {action}")

    # First check if it's an informational message
    if action in states.INFO_MESSAGES:
        print(f"Info: {states.INFO_MESSAGES[action]}")
        return

    try:
        if isinstance(action, str):
            tokens = action.split()
            act = tokens[0]
            # Handle PDDL action names
            if act == "turn_on_fan":
                client.fan.turn_on()
                print("Action: Turning fan on")
            elif act == "turn_off_fan":
                client.fan.turn_off()
                print("Action: Turning fan off")
            elif act == "open_roof":
                servo = tokens[-1]  # Use last token for servo
                client.roof.open_roof(f"servo_on {servo}")
                print(f"Action: Opening roof servo {servo}")
            elif act == "close_roof":
                servo = tokens[-1]
                client.roof.close_roof(f"servo_on {servo}")
                print(f"Action: Closing roof servo {servo}")
            elif act == "turn_on_pump":
                client.water_pump.turn_on()
                print("Action: Turning water pump on")
            elif act == "turn_off_pump":
                client.water_pump.turn_off()
                print("Action: Turning water pump off")
            elif act in states.INFO_MESSAGES:
                print(f"Info: {states.INFO_MESSAGES[act]}")
            else:
                print(f"Unknown action: {action}")
    except Exception as e:
        print(f"Error executing action: {str(e)}")

def main():
    client = RabbitMQClient()
    sensor_thread = threading.Thread(target=sensor_loop, args=(client,), daemon=True)
    sensor_thread.start()
    client.start_consuming(invoke_action)

if __name__ == "__main__":
    main()