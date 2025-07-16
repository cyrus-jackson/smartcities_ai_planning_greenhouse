import time
from grovepi import pinMode, servo

# Define the GrovePi+ digital ports for the servos
SERVO_1_GPIO = 3  # D3
SERVO_2_GPIO = 8  # D8

def test_servos():
    print("Initializing servos...")
    try:
        pinMode(SERVO_1_GPIO, "OUTPUT")
        pinMode(SERVO_2_GPIO, "OUTPUT")
        print("Servos initialized successfully.")
    except Exception as e:
        print(f"Error initializing servos: {e}")
        return

    try:
        # Test open (90 degrees)
        print("Opening Servo 1 (D3) to 90 degrees")
        servo(SERVO_1_GPIO, 90)
        time.sleep(2)

        print("Opening Servo 2 (D8) to 90 degrees")
        servo(SERVO_2_GPIO, 90)
        time.sleep(2)

        # Test close (0 degrees)
        print("Closing Servo 1 (D3) to 0 degrees")
        servo(SERVO_1_GPIO, 0)
        time.sleep(2)

        print("Closing Servo 2 (D8) to 0 degrees")
        servo(SERVO_2_GPIO, 0)
        time.sleep(2)

        # Test full range (optional)
        print("Moving Servo 1 (D3) to 170 degrees")
        servo(SERVO_1_GPIO, 170)
        time.sleep(2)
        print("Returning Servo 1 (D3) to 0 degrees")
        servo(SERVO_1_GPIO, 0)
        time.sleep(2)

        print("Moving Servo 2 (D8) to 170 degrees")
        servo(SERVO_2_GPIO, 170)
        time.sleep(2)
        print("Returning Servo 2 (D8) to 0 degrees")
        servo(SERVO_2_GPIO, 0)
        time.sleep(2)

        print("Servo test complete.")

    except Exception as e:
        print(f"Error during servo test: {e}")

if __name__ == "__main__":
    test_servos()