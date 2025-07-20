import RPi.GPIO as GPIO
import time
import state_constants as states
from config import SERVO_1_GPIO, SERVO_2_GPIO

class RoofModule:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.servo_1 = SERVO_1_GPIO
        self.servo_2 = SERVO_2_GPIO

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.servo_1, GPIO.OUT)
        GPIO.setup(self.servo_2, GPIO.OUT)

        # 50Hz PWM for standard servos
        self.pwm1 = GPIO.PWM(self.servo_1, 50)
        self.pwm2 = GPIO.PWM(self.servo_2, 50)
        self.pwm1.start(2.5)
        self.pwm2.start(2.5)
        # Immediately stop PWM to prevent jitter at startup
        self.pwm1.ChangeDutyCycle(0)
        self.pwm2.ChangeDutyCycle(0)
        print("Roof servos initialized successfully")

    def set_angle(self, pwm, angle):
        # interp maps the angle (0-180) to the PWM duty cycle (2.5-12.5) for the servo
        from numpy import interp
        angle = max(0, min(180, angle))
        try:
            if hasattr(pwm, 'last_angle'):
                start_angle = pwm.last_angle
            else:
                start_angle = 0
            if start_angle == angle:
                # Already at target
                duty = interp(angle, [0, 180], [2.5, 12.5])
                pwm.ChangeDutyCycle(duty)
                time.sleep(0.4)
                pwm.ChangeDutyCycle(0)
                return
            # Step direction
            step = 10 if angle > start_angle else -10
            # Use range that includes the final angle
            for a in range(int(start_angle), int(angle), step):
                duty = interp(a, [0, 180], [2.5, 12.5])
                pwm.ChangeDutyCycle(duty)
                time.sleep(0.4)
            # Ensure we always end at the exact target angle
            duty = interp(angle, [0, 180], [2.5, 12.5])
            pwm.ChangeDutyCycle(duty)
            time.sleep(0.2)
            pwm.ChangeDutyCycle(0)
            pwm.last_angle = angle
        except Exception as e:
            print(f"Error in graceful servo movement: {e}")

    def open_roof(self, servo_state):
        try:
            if "s1" in servo_state:
                self.set_angle(self.pwm1, 90)
                self.state_manager.update_state(states.RUN_ROOF_SERVO_S1)
                print(f"RoofModule: Opening roof servo {self.servo_1} to 90 degrees")
            else:
                self.set_angle(self.pwm2, 90)
                self.state_manager.update_state(states.RUN_ROOF_SERVO_S2)
                print(f"RoofModule: Opening roof servo {self.servo_2} to 90 degrees")
        except Exception as e:
            print(f"Error opening roof servo: {e}")

    def close_roof(self, servo_state):
        try:
            if "s1" in servo_state:
                self.set_angle(self.pwm1, 0)
                self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S1)
                print(f"RoofModule: Closing roof servo {self.servo_1} to 0 degrees")
            else:
                self.set_angle(self.pwm2, 0)
                print(f"RoofModule: Closing roof servo {self.servo_2} to 0 degrees")
                self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S2)
        except Exception as e:
            print(f"Error closing roof servo: {e}")

    def cleanup(self):
        try:
            self.pwm1.stop()
            self.pwm2.stop()
            GPIO.cleanup()
        except Exception as e:
            print(f"Error during servo cleanup: {e}")