#!/usr/bin/env python3

import grovepi

class SoilMoistureSensor:
    def __init__(self, analog_port=1):
        """
        Initialize Grove Moisture Sensor v1.1
        
        Args:
            analog_port: Analog port number where the moisture sensor is connected (default: A1)
        """
        self.analog_port = analog_port
        self.is_initialized = False
        
        # Grove Moisture Sensor v1.1 specific calibration values
        self.dry_value = 20    # Typical dry soil reading
        self.wet_value = 580    # Typical wet soil reading
        
        self._init_sensor()
    
    def _init_sensor(self):
        """Initialize the Grove Moisture Sensor v1.1"""
        try:
            # Set the analog port as input
            grovepi.pinMode(self.analog_port, "INPUT")
            self.is_initialized = True
            print(f"SoilMoistureSensor v1.1: Initialized on analog port A{self.analog_port}")
            print(f"SoilMoistureSensor v1.1: Calibration - Dry: {self.dry_value}, Wet: {self.wet_value}")
        except Exception as e:
            print(f"SoilMoistureSensor v1.1: Error initializing sensor: {e}")
            self.is_initialized = False
    
    def get_reading(self):
        """Get soil moisture reading as percentage"""
        if not self.is_initialized:
            print("SoilMoistureSensor: ERROR - Sensor not initialized!")
            return 38  # Return default value
        
        try:
            # Read the analog value from the Grove Moisture Sensor v1.1
            sensor_value = grovepi.analogRead(self.analog_port)
            
            # Convert to moisture percentage
            # Grove Moisture Sensor v1.1 characteristics:
            # - Higher values (700-950) for dry soil
            # - Lower values (300-500) for wet soil
            # - Typical range: 300-950
            # Convert to percentage where 0% = very dry, 100% = very wet
            
            # Define calibration values for v1.1
            dry_value = 950    # Maximum dry reading
            wet_value = 300    # Maximum wet reading
            
            # Calculate moisture percentage using v1.1 calibration
            moisture_percentage = max(0, min(100, 100 - ((sensor_value - self.wet_value) * 100 / (self.dry_value - self.wet_value))))
            
            print(f"SoilMoistureSensor v1.1: Raw value: {sensor_value}, Moisture: {moisture_percentage:.1f}%")
            return round(moisture_percentage, 1)
            
        except Exception as e:
            print(f"SoilMoistureSensor: Error reading soil moisture: {e}")
            return 38  # Return default value on error
    
    def set_calibration(self, dry_value, wet_value):
        """
        Set custom calibration values for the Grove Moisture Sensor v1.1
        
        Args:
            dry_value: Sensor reading in completely dry soil
            wet_value: Sensor reading in completely wet soil
        """
        self.dry_value = dry_value
        self.wet_value = wet_value
        print(f"SoilMoistureSensor v1.1: Calibration updated - Dry: {dry_value}, Wet: {wet_value}")
    
    def get_raw_reading(self):
        """Get raw analog reading from the sensor"""
        if not self.is_initialized:
            print("SoilMoistureSensor v1.1: ERROR - Sensor not initialized!")
            return 0
        
        try:
            raw_value = grovepi.analogRead(self.analog_port)
            print(f"SoilMoistureSensor v1.1: Raw reading: {raw_value}")
            return raw_value
        except Exception as e:
            print(f"SoilMoistureSensor v1.1: Error reading raw value: {e}")
            return 0
    def calibrate_sensor(self, dry_readings=10, wet_readings=10):
        """
        Calibrate the Grove Moisture Sensor v1.1 by taking readings in dry and wet conditions
        
        Args:
            dry_readings: Number of readings to take in dry soil
            wet_readings: Number of readings to take in wet soil
        """
        print("SoilMoistureSensor v1.1: Starting calibration...")
        print("Place sensor in DRY soil and press Enter")
        input()
        
        dry_values = []
        for i in range(dry_readings):
            value = grovepi.analogRead(self.analog_port)
            dry_values.append(value)
            print(f"Dry reading {i+1}: {value}")
            import time
            time.sleep(0.5)
        
        dry_avg = sum(dry_values) / len(dry_values)
        print(f"Average dry value: {dry_avg}")
        
        print("\nPlace sensor in WET soil and press Enter")
        input()
        
        wet_values = []
        for i in range(wet_readings):
            value = grovepi.analogRead(self.analog_port)
            wet_values.append(value)
            print(f"Wet reading {i+1}: {value}")
            import time
            time.sleep(0.5)
        
        wet_avg = sum(wet_values) / len(wet_values)
        print(f"Average wet value: {wet_avg}")
        
        print(f"\nCalibration complete:")
        print(f"Dry soil average: {dry_avg}")
        print(f"Wet soil average: {wet_avg}")
        
        # Update calibration values
        self.set_calibration(int(dry_avg), int(wet_avg))
        
        # Test the new calibration
        print("\nTesting new calibration...")
        for i in range(3):
            moisture = self.get_reading()
            print(f"Test reading {i+1}: {moisture}%")
            import time
            time.sleep(1)
    
    def test_sensor(self, readings=5):
        """Test the Grove Moisture Sensor v1.1 with multiple readings"""
        print(f"SoilMoistureSensor v1.1: Testing with {readings} readings...")
        for i in range(readings):
            raw = self.get_raw_reading()
            moisture = self.get_reading()
            print(f"Reading {i+1}: Raw={raw}, Moisture={moisture}%")
            import time
            time.sleep(1)
        print("SoilMoistureSensor v1.1: Test completed")

# Test function
if __name__ == '__main__':
    print("Grove Moisture Sensor v1.1 Test")
    print("Connect Grove Moisture Sensor v1.1 to A1")
    print("=" * 40)
    
    try:
        sensor = SoilMoistureSensor(analog_port=1)
        
        print("Commands: 'test', 'raw', 'calibrate', 'set_cal', 'quit'")
        while True:
            command = input("Enter command: ").strip().lower()
            
            if command == 'test':
                sensor.test_sensor()
            elif command == 'raw':
                sensor.get_raw_reading()
            elif command == 'calibrate':
                sensor.calibrate_sensor()
            elif command == 'set_cal':
                try:
                    dry = int(input("Enter dry value: "))
                    wet = int(input("Enter wet value: "))
                    sensor.set_calibration(dry, wet)
                except ValueError:
                    print("Invalid values")
            elif command == 'quit' or command == 'exit':
                print("Exiting...")
                break
            else:
                print("Unknown command. Use: test, raw, calibrate, set_cal, quit")
                
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"Error: {e}")