import state_constants as states
from config import SERVO_1_GPIO, SERVO_2_GPIO
from grovepi import *

class RoofModule:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.servo_1 = SERVO_1_GPIO
        self.servo_2 = SERVO_2_GPIO
        # Initialize servos
        try:
            # Set servo pins as OUTPUT (optional for servo, but safe)
            pinMode(self.servo_1, "OUTPUT")
            pinMode(self.servo_2, "OUTPUT")
            print("Roof servos initialized successfully")
        except Exception as e:
            print(f"Error initializing roof servos: {e}")

    def open_roof(self, servo_state):
        """Open roof servo to 90 degrees"""
        try:
            servo = self.servo_1 if "s1" in servo_state else self.servo_2
            # Use grovepi.servo for correct PWM
            servo_angle = 90  # or adjust as needed for your hardware
            servoWrite(servo, servo_angle)
            print(f"RoofModule: Opening roof servo {servo} to {servo_angle} degrees")
            self.state_manager.update_state(servo_state)
        except Exception as e:
            print(f"Error opening roof servo: {e}")

    def close_roof(self, servo_state):
        """Close roof servo to 0 degrees"""
        try:
            servo = self.servo_1 if "s1" in servo_state else self.servo_2
            servo_angle = 0
            servoWrite(servo, servo_angle)
            print(f"RoofModule: Closing roof servo {servo} to {servo_angle} degrees")
            self.state_manager.update_state(servo_state)
        except Exception as e:
            print(f"Error closing roof servo: {e}")

    def cleanup(self):
        """Clean up resources"""
        try:
            # Return servos to closed position
            servoWrite(self.servo_1, 0)
            servoWrite(self.servo_2, 0)
        except Exception as e:
            print(f"Error during servo cleanup: {e}")