class FanModule:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def turn_on(self):
        print("FanModule: Turning fan ON")
        # Here you would add hardware control logic if needed
        self.state_manager.update_state("fan", "on")
        self.state_manager.send_state()

    def turn_off(self):
        print("FanModule: Turning fan OFF")
        # Here you would add hardware control logic if needed
        self.state_manager.update_state("fan", "off")
        self.state_manager.send_state()