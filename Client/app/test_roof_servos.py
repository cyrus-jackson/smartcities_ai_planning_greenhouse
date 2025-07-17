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
        print("Moving to 0°")
        set_angle(0)
        time.sleep(1)
        print("Moving to 90°")
        set_angle(90)
        time.sleep(1)
        print("Moving to 180°")
        set_angle(180)
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()