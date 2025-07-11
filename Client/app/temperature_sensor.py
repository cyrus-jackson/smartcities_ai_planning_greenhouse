#!/usr/bin/env python3

import grovepi
import math
class TemperatureSensor:
    def __init__(self, analog_port=0):
        """
        Initialize Grove Temperature Sensor
        
        Args:
            analog_port: Analog port number where the temperature sensor is connected (default: A0)
        """
        self.analog_port = analog_port
        self.is_initialized = False
        self._init_sensor()
    
    def _init_sensor(self):
        """Initialize the temperature sensor"""
        try:
            # Set the analog port as input (Grove temperature sensor uses analog)
            grovepi.pinMode(self.analog_port, "INPUT")
            self.is_initialized = True
            print(f"TemperatureSensor: Initialized on analog port A{self.analog_port}")
        except Exception as e:
            print(f"TemperatureSensor: Error initializing sensor: {e}")
            self.is_initialized = False
    
    def get_reading(self):
        """Get temperature reading in Celsius"""
        if not self.is_initialized:
            print("TemperatureSensor: ERROR - Sensor not initialized!")
            return 52  # Return default value
        
        try:
            # Read the analog value from the Grove temperature sensor
            sensor_value = grovepi.analogRead(self.analog_port)
            
            # Convert to voltage (Grove Pi uses 5V reference)
            resistance = (float)(1023 - sensor_value) * 10000 / sensor_value
            
            # Convert voltage to temperature (typical Grove temperature sensor formula)
            # This formula may need adjustment based on your specific sensor model
            temperature = 1 / (math.log(resistance / 10000) / 3975 + 1 / 298.15) - 273.15
            temperature = round(temperature, 2)

            
            print(f"TemperatureSensor: Raw value: {sensor_value}, Resistance: {resistance:.2f}V, Temperature: {temperature:.1f}°C")
            return temperature
            
        except Exception as e:
            print(f"TemperatureSensor: Error reading temperature: {e}")
            return 52  # Return default value on error
    
    def test_sensor(self, readings=5):
        """Test the temperature sensor with multiple readings"""
        print(f"TemperatureSensor: Testing with {readings} readings...")
        for i in range(readings):
            temp = self.get_reading()
            print(f"Reading {i+1}: {temp}°C")
            import time
            time.sleep(1)
        print("TemperatureSensor: Test completed")

# Test function
if __name__ == '__main__':
    print("Grove Temperature Sensor Test")
    print("Connect Grove Temperature Sensor to A0")
    print("=" * 40)
    
    try:
        sensor = TemperatureSensor(analog_port=0)
        sensor.test_sensor()
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"Error: {e}")
