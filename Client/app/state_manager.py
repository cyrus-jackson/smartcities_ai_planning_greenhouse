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

    def __init__(self, client):
        self.client = client
        self.current_state = {**DEFAULT_STATE}

    def update_state(self, new_state_key):
        # Validation: Only allow one state in each mutually exclusive group to be 1
        for group in self._MUTUALLY_EXCLUSIVE:
            if new_state_key in group:
                for other_key in group:
                    self.current_state[other_key] = 1 if other_key == new_state_key else 0
                break
        else:
            # If not in any group, just set to 1
            self.current_state[new_state_key] = 1
        print(f"Updated state here: {self.current_state}")

        # Use the thread-safe method to send the state
        self.client.send_state_threadsafe(self.current_state)

    def update_plan(self, plan_id):
        try:
            if not isinstance(plan_id, int):
                raise ValueError(f"PLAN_ID must be an integer, got {type(plan_id).__name__}")
            self.current_state[PLAN_ID] = plan_id
        except Exception as e:
            print(f"Failed to set PLAN_ID: {e}")
            self.current_state[PLAN_ID] = None

    def get_current_state(self):
        return self.current_state.copy()