class RoofModule:
    def __init__(self, state_manager):
        self.state_manager = state_manager

    def open_roof(self, servo):
        print(f"RoofModule: Opening roof servo {servo}")
        self.state_manager.update_state(f"servo_{servo}", "open")
        self.state_manager.send_state()

    def close_roof(self, servo):
        print(f"RoofModule: Closing roof servo {servo}")
        self.state_manager.update_state(f"servo_{servo}", "closed")
        self.state_manager.send_state()