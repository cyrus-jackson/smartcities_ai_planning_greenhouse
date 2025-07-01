import state_constants as states

class FanModule:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def turn_on(self):
        print("FanModule: Turning fan ON")
        self.state_manager.update_state(states.FAN_ON)

    def turn_off(self):
        print("FanModule: Turning fan OFF")
        self.state_manager.update_state(states.FAN_OFF)
