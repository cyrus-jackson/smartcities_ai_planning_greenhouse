import json
from state_constants import *

class StateManager:
    # Define mutually exclusive state groups
    _MUTUALLY_EXCLUSIVE = [
        {FAN_ON, FAN_OFF},
        {WATER_PUMP_ON, WATER_PUMP_OFF},
        {RUN_ROOF_SERVO_S1, CLOSE_ROOF_SERVO_S1},
        {RUN_ROOF_SERVO_S2, CLOSE_ROOF_SERVO_S2},
    ]

    def __init__(self, rabbitmq_client, states_queue):
        self.state = DEFAULT_STATE
        self.rabbitmq_client = rabbitmq_client
        self.states_queue = states_queue

    def update_state(self, key):
        print(f"Updated state here: {self.state}")
        # Validation: Only allow one state in each mutually exclusive group to be 1
        for group in self._MUTUALLY_EXCLUSIVE:
            if key in group:
                for other_key in group:
                    self.state[other_key] = 1 if other_key == key else 0
                break
        else:
            # If not in any group, just set to 1
            self.state[key] = 1
        self.send_state()

    def update_plan(self, plan_id):
        try:
            if not isinstance(plan_id, int):
                raise ValueError(f"PLAN_ID must be an integer, got {type(plan_id).__name__}")
            self.state[PLAN_ID] = plan_id
        except Exception as e:
            print(f"Failed to set PLAN_ID: {e}")
            self.state[PLAN_ID] = None

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