
class RoofModule:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def open_roof(self, servo_state):
        print(f"RoofModule: Opening roof with state {servo_state}")
        self.state_manager.update_state(servo_state)

    def close_roof(self, servo_state):
        print(f"RoofModule: Closing roof with state {servo_state}")
        self.state_manager.update_state(servo_state)