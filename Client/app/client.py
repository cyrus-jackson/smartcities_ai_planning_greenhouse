import pika
import json
import threading
import state_constants as states

from config import load_config
from state_manager import StateManager

from fan_module import FanModule
from env_sensors import sensor_loop
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
        self.fan = FanModule(self.state_manager)
        self.roof = RoofModule(self.state_manager)

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
                plan_id = actions[states.PLAN_ID]
                self.state_manager.update_plan(plan_id)
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
        self.connection.close()

def invoke_action(action, client):
    print(f"Invoking action: {action}")
    # Use the pre-instantiated modules from the client
    if action == states.FAN_ON:
        client.fan.turn_on()
    elif action == states.FAN_OFF:
        client.fan.turn_off()
    elif action.startswith("run_servo"):
        servo = action.split()[-1]
        if servo == "s1":
            client.roof.open_roof(states.RUN_ROOF_SERVO_S1)
        elif servo == "s2":
            client.roof.open_roof(states.RUN_ROOF_SERVO_S2)
    elif action.startswith("close_servo"):
        servo = action.split()[-1]
        if servo == "s1":
            client.roof.close_roof(states.CLOSE_ROOF_SERVO_S1)
        elif servo == "s2":
            client.roof.close_roof(states.CLOSE_ROOF_SERVO_S2)

def main():
    client = RabbitMQClient()
    sensor_thread = threading.Thread(target=sensor_loop, args=(client,), daemon=True)
    sensor_thread.start()
    client.start_consuming(invoke_action)

if __name__ == "__main__":
    main()