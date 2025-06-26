import json

class StateManager:
    def __init__(self, rabbitmq_client, states_queue):
        self.state = {}
        self.rabbitmq_client = rabbitmq_client
        self.states_queue = states_queue

    def update_state(self, key, value):
        self.state[key] = value

    def get_state(self):
        return self.state.copy()

    def send_state(self):
        message = json.dumps(self.state)
        self.rabbitmq_client.channel.basic_publish(
            exchange='',
            routing_key=self.states_queue,
            body=message.encode()
        )
        print(f"Sent state to {self.states_queue}: {self.state}")