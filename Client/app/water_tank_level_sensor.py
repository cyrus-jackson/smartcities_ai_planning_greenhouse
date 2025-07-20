#!/usr/bin/env python3

import grovepi

class WaterTankLevelSensor:
    def __init__(self, digital_port=4, tank_height=22):
        """
        Initialize Grove Ultrasonic Ranger v2.0 for water tank level measurement
        
        Args:
            digital_port: Digital port number where the ultrasonic sensor is connected (default: D4)
            tank_height: Total tank height in cm (default: 22cm)
        """
        self.digital_port = digital_port
        self.tank_height = tank_height
        self.is_initialized = False
        self._init_sensor()
    
    def _init_sensor(self):
        """Initialize the ultrasonic sensor"""
        try:
            # Grove ultrasonic sensor uses digital port
            grovepi.pinMode(self.digital_port, "INPUT")
            self.is_initialized = True
            print(f"WaterTankLevelSensor: Initialized on digital port D{self.digital_port}")
            print(f"WaterTankLevelSensor: Tank height set to {self.tank_height}cm")
        except Exception as e:
            print(f"WaterTankLevelSensor: Error initializing sensor: {e}")
            self.is_initialized = False
    
    def get_reading(self):
        """Get water level reading as percentage of tank capacity"""
        if not self.is_initialized:
            print("WaterTankLevelSensor: ERROR - Sensor not initialized!")
            return 10  # Return default value
        
        try:
            # Read distance from ultrasonic sensor
            distance = grovepi.ultrasonicRead(self.digital_port)
            
            # Convert distance to water level percentage
            # Distance from sensor to water surface
            # Water level = tank_height - distance_to_water
            water_level_cm = self.tank_height - distance
            water_level_percentage = max(0, min(100, (water_level_cm / self.tank_height) * 100))
            
            print(f"WaterTankLevelSensor: Distance: {distance}cm, Water level: {water_level_percentage:.1f}%")
            return round(water_level_percentage, 1)
            
        except Exception as e:
            print(f"WaterTankLevelSensor: Error reading water level: {e}")
            return 10  # Return default value on error
    
    def get_distance(self):
        """Get raw distance reading in cm"""
        if not self.is_initialized:
            print("WaterTankLevelSensor: ERROR - Sensor not initialized!")
            return 0
        
        try:
            distance = grovepi.ultrasonicRead(self.digital_port)
            print(f"WaterTankLevelSensor: Distance: {distance}cm")
            return distance
        except Exception as e:
            print(f"WaterTankLevelSensor: Error reading distance: {e}")
            return 0
    
    def get_water_level_cm(self):
        """Get water level in centimeters"""
        distance = self.get_distance()
        if distance == 0:
            return 0
        
        water_level_cm = max(0, self.tank_height - distance)
        print(f"WaterTankLevelSensor: Water level: {water_level_cm}cm")
        return water_level_cm
    
    def set_tank_height(self, height_cm):
        """Set the total tank height for accurate percentage calculations"""
        self.tank_height = height_cm
        print(f"WaterTankLevelSensor: Tank height set to {height_cm}cm")
    
    def calibrate_sensor(self):
        """Calibrate the sensor by measuring empty and full tank"""
        print("WaterTankLevelSensor: Starting calibration...")
        print("Place sensor at the top of EMPTY tank and press Enter")
        input()
        
        empty_distance = self.get_distance()
        print(f"Empty tank distance: {empty_distance}cm")
        
        print("\nFill tank completely and press Enter")
        input()
        
        full_distance = self.get_distance()
        print(f"Full tank distance: {full_distance}cm")
        
        calculated_height = empty_distance - full_distance
        print(f"\nCalibration complete:")
        print(f"Calculated tank height: {calculated_height}cm")
        print(f"Current tank height setting: {self.tank_height}cm")
        
        update = input("Update tank height with calculated value? (y/n): ").strip().lower()
        if update == 'y':
            self.set_tank_height(calculated_height)
    
    def test_sensor(self, readings=5):
        """Test the water level sensor with multiple readings"""
        print(f"WaterTankLevelSensor: Testing with {readings} readings...")
        for i in range(readings):
            distance = self.get_distance()
            water_level_cm = self.get_water_level_cm()
            water_level_percent = self.get_reading()
            print(f"Reading {i+1}: Distance={distance}cm, Level={water_level_cm}cm ({water_level_percent}%)")
            import time
            time.sleep(1)
        print("WaterTankLevelSensor: Test completed")

# Test function
if __name__ == '__main__':
    print("Grove Ultrasonic Ranger v2.0 Water Level Sensor Test")
    print("Connect Grove Ultrasonic Ranger to D4")
    print("=" * 50)
    
    try:
        # Ask user for tank height
        try:
            tank_height = float(input("Enter tank height in cm (default 22): ") or "22")
        except ValueError:
            tank_height = 22
        
        sensor = WaterTankLevelSensor(digital_port=4, tank_height=tank_height)
        
        print("Commands: 'test', 'distance', 'level', 'calibrate', 'set_height', 'quit'")
        while True:
            command = input("Enter command: ").strip().lower()
            
            if command == 'test':
                sensor.test_sensor()
            elif command == 'distance':
                sensor.get_distance()
            elif command == 'level':
                sensor.get_reading()
            elif command == 'calibrate':
                sensor.calibrate_sensor()
            elif command == 'set_height':
                try:
                    height = float(input("Enter new tank height in cm: "))
                    sensor.set_tank_height(height)
                except ValueError:
                    print("Invalid height value")
            elif command == 'quit' or command == 'exit':
                print("Exiting...")
                break
            else:
                print("Unknown command. Use: test, distance, level, calibrate, set_height, quit")
                
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except Exception as e:
        print(f"Error: {e}")