#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Relay pin configuration from config.py
RELAY_PIN = 27  # GPIO 18 in BCM mode for water pump relay

def setup_gpio():
    """Initialize GPIO settings for the relay"""
    try:
        GPIO.setmode(GPIO.BCM)  # Use BCM numbering
        GPIO.setup(RELAY_PIN, GPIO.OUT)  # Set pin as output
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Start with relay OFF
        print(f"GPIO {RELAY_PIN} initialized successfully for relay control")
        return True
    except Exception as e:
        print(f"Error initializing GPIO {RELAY_PIN}: {e}")
        return False

def test_relay():
    """Test the relay by toggling it ON and OFF"""
    print(f"Testing relay on GPIO {RELAY_PIN}...")
    try:
        # Turn relay ON
        print("Turning relay ON (should hear a click or see LED on relay)")
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        time.sleep(2)  # Wait 2 seconds
        
        # Turn relay OFF
        print("Turning relay OFF")
        GPIO.output(RELAY_PIN, GPIO.LOW)
        time.sleep(2)  # Wait 2 seconds
        
        print("Relay test completed")
    except Exception as e:
        print(f"Error during relay test: {e}")
    finally:
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Ensure relay is OFF

def check_pin_status():
    """Check the current status of the relay pin"""
    try:
        # Read the current output state of the pin
        state = GPIO.input(RELAY_PIN)
        status = "HIGH (ON)" if state == GPIO.HIGH else "LOW (OFF)"
        print(f"Current state of GPIO {RELAY_PIN}: {status}")
    except Exception as e:
        print(f"Error checking pin status: {e}")

def cleanup():
    """Clean up GPIO settings"""
    print("Cleaning up GPIO...")
    try:
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Ensure relay is OFF
        GPIO.cleanup()
        print("GPIO cleanup completed")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    print("Relay Pin Check Program for Raspberry Pi 3B+ with GrovePi+")
    print(f"Checking standard relay connected to GPIO {RELAY_PIN} (BCM)")
    print("WARNING: Ensure relay is properly connected and powered!")
    print("=" * 50)
    
    # Initialize GPIO
    if not setup_gpio():
        print("Failed to initialize GPIO. Exiting...")
        exit(1)
    
    try:
        # Check initial pin status
        check_pin_status()
        
        # Test relay by toggling
        test_relay()
        
        # Check final pin status
        check_pin_status()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        cleanup()
