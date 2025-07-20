import RPi.GPIO as GPIO
import time
from numpy import interp

SERVO_GPIO = 26  # BCM numbering (physical pin 37)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_GPIO, GPIO.OUT)

# 50Hz PWM (standard for servos)
pwm = GPIO.PWM(SERVO_GPIO, 50)
pwm.start(2.5)  # Initial duty cycle

def set_angle(angle):
    # Clamp angle and map to duty cycle
    angle = max(0, min(180, angle))
    duty = interp(angle, [0, 180], [2.5, 12.5])
    pwm.ChangeDutyCycle(duty)

try:
    while True:
        try:
            user_input = input("Enter angle (0-180, or 'q' to quit): ")
            if user_input.strip().lower() == 'q':
                break
            angle = float(user_input)
            if 0 <= angle <= 180:
                print(f"Moving to {angle}°")
                set_angle(angle)
            else:
                print("Please enter a value between 0 and 180.")
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 180, or 'q' to quit.")
except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()