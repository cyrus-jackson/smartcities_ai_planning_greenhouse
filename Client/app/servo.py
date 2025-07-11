#!/usr/bin/env python3

import time
import grovepi
import state_constants as states

class ServoModule:
    def __init__(self, state_manager, servo_port_1=3, servo_port_2=5):
        """
        Initialize the ServoModule to control two Grove servos
        
        Args:
            state_manager: State manager instance for tracking servo states
            servo_port_1: Digital port for first servo (default: D3)
            servo_port_2: Digital port for second servo (default: D5)
        """
        self.state_manager = state_manager
        self.servo_port_1 = servo_port_1
        self.servo_port_2 = servo_port_2
        self.is_initialized = False
        
        # Initialize the servos
        self._init_servos()
    
    def _init_servos(self):
        """Initialize the servo pins as output and set to closed position"""
        try:
            grovepi.pinMode(self.servo_port_1, "OUTPUT")
            grovepi.pinMode(self.servo_port_2, "OUTPUT")
            # Start with servos at 0 degrees (closed)
            grovepi.analogWrite(self.servo_port_1, 0)
            grovepi.analogWrite(self.servo_port_2, 0)
            self.is_initialized = True
            self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S1, 1)
            self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S2, 1)
            self.state_manager.update_state(states.RUN_ROOF_SERVO_S1, 0)
            self.state_manager.update_state(states.RUN_ROOF_SERVO_S2, 0)
            print(f"ServoModule: Servos initialized on ports D{self.servo_port_1} and D{self.servo_port_2}")
        except Exception as e:
            print(f"ServoModule: Error initializing servos: {e}")
            self.is_initialized = False
    
    def run_servo_s1(self):
        """Move servo S1 to 90 degrees (run/open)"""
        if not self.is_initialized:
            print("ServoModule: ERROR - Servos not initialized!")
            return False
        
        try:
            print("ServoModule: Running servo S1 (90 degrees)")
            grovepi.analogWrite(self.servo_port_1, 180)
            self.state_manager.update_state(states.RUN_ROOF_SERVO_S1, 1)
            self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S1, 0)
            print("ServoModule: Servo S1 is now RUNNING - Moved to 90 degrees")
            return True
        except Exception as e:
            print(f"ServoModule: Error running servo S1: {e}")
            return False
    
    def run_servo_s2(self):
        """Move servo S2 to 90 degrees (run/open)"""
        if not self.is_initialized:
            print("ServoModule: ERROR - Servos not initialized!")
            return False
        
        try:
            print("ServoModule: Running servo S2 (90 degrees)")
            grovepi.analogWrite(self.servo_port_2, 180)
            self.state_manager.update_state(states.RUN_ROOF_SERVO_S2, 1)
            self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S2, 0)
            print("ServoModule: Servo S2 is now RUNNING - Moved to 90 degrees")
            return True
        except Exception as e:
            print(f"ServoModule: Error running servo S2: {e}")
            return False
    
    def close_servo_s1(self):
        """Move servo S1 to 0 degrees (close)"""
        if not self.is_initialized:
            print("ServoModule: ERROR - Servos not initialized!")
            return False
        
        try:
            print("ServoModule: Closing servo S1 (0 degrees)")
            grovepi.analogWrite(self.servo_port_1, 0)
            self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S1, 1)
            self.state_manager.update_state(states.RUN_ROOF_SERVO_S1, 0)
            print("ServoModule: Servo S1 is now CLOSED - Moved to 0 degrees")
            return True
        except Exception as e:
            print(f"ServoModule: Error closing servo S1: {e}")
            return False
    
    def close_servo_s2(self):
        """Move servo S2 to 0 degrees (close)"""
        if not self.is_initialized:
            print("ServoModule: ERROR - Servos not initialized!")
            return False
        
        try:
            print("ServoModule: Closing servo S2 (0 degrees)")
            grovepi.analogWrite(self.servo_port_2, 0)
            self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S2, 1)
            self.state_manager.update_state(states.RUN_ROOF_SERVO_S2, 0)
            print("ServoModule: Servo S2 is now CLOSED - Moved to 0 degrees")
            return True
        except Exception as e:
            print(f"ServoModule: Error closing servo S2: {e}")
            return False
    
    def toggle_servo_s1(self):
        """Toggle servo S1 between RUN and CLOSE states"""
        current_state = self.state_manager.get_current_state()
        
        if current_state[states.RUN_ROOF_SERVO_S1] == 1:
            return self.close_servo_s1()
        else:
            return self.run_servo_s1()
    
    def toggle_servo_s2(self):
        """Toggle servo S2 between RUN and CLOSE states"""
        current_state = self.state_manager.get_current_state()
        
        if current_state[states.RUN_ROOF_SERVO_S2] == 1:
            return self.close_servo_s2()
        else:
            return self.run_servo_s2()
    
    def get_status(self):
        """Get the current status of both servos"""
        current_state = self.state_manager.get_current_state()
        s1_status = "RUNNING (90°)" if current_state[states.RUN_ROOF_SERVO_S1] == 1 else "CLOSED (0°)"
        s2_status = "RUNNING (90°)" if current_state[states.RUN_ROOF_SERVO_S2] == 1 else "CLOSED (0°)"
        return {"S1": s1_status, "S2": s2_status}
    
    def test_servo_cycle(self, cycles=3, on_duration=2, off_duration=2):
        """
        Test both servos by cycling between 0 and 90 degrees
        
        Args:
            cycles: Number of test cycles
            on_duration: How long to keep servos at 90 degrees (seconds)
            off_duration: How long to keep servos at 0 degrees (seconds)
        """
        print(f"ServoModule: Testing servo cycle ({cycles} cycles)...")
        
        for i in range(cycles):
            print(f"ServoModule: Test cycle {i+1}/{cycles}:")
            
            # Run both servos (90 degrees)
            print("ServoModule: Testing RUN state")
            if self.run_servo_s1():
                time.sleep(on_duration / 2)
            if self.run_servo_s2():
                time.sleep(on_duration / 2)
            
            # Close both servos (0 degrees)
            print("ServoModule: Testing CLOSE state")
            if self.close_servo_s1():
                time.sleep(off_duration / 2)
            if self.close_servo_s2():
                time.sleep(off_duration / 2)
        
        print("ServoModule: Servo test completed")
    
    def emergency_shutdown(self):
        """Emergency shutdown - immediately move both servos to 0 degrees"""
        print("ServoModule: EMERGENCY SHUTDOWN - Moving servos to 0 degrees!")
        try:
            grovepi.analogWrite(self.servo_port_1, 0)
            grovepi.analogWrite(self.servo_port_2, 0)
            self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S1, 1)
            self.state_manager.update_state(states.CLOSE_ROOF_SERVO_S2, 1)
            self.state_manager.update_state(states.RUN_ROOF_SERVO_S1, 0)
            self.state_manager.update_state(states.RUN_ROOF_SERVO_S2, 0)
            print("ServoModule: Emergency shutdown completed")
        except Exception as e:
            print(f"ServoModule: Error during emergency shutdown: {e}")
    
    def cleanup(self):
        """Clean shutdown of the servo module"""
        print("ServoModule: Cleaning up...")
        self.close_servo_s1()
        self.close_servo_s2()
        print("ServoModule: Cleanup completed")

# Example usage and testing
if __name__ == '__main__':
    # Mock state manager for testing
    class MockStateManager:
        def __init__(self):
            self.current_state = states.DEFAULT_STATE.copy()
        
        def update_state(self, state_key, value):
            self.current_state[state_key] = value
            print(f"StateManager: Updated {state_key} to {value}")
        
        def get_current_state(self):
            return self.current_state
    
    print("ServoModule Test Program")
    print("Connect Grove Servos to digital ports D3 and D5")
    print("WARNING: Ensure servos are properly connected and powered!")
    print("=" * 50)
    
    # Create state manager and servo module
    state_manager = MockStateManager()
    servo = ServoModule(state_manager)
    
    try:
        # Interactive control
        print("\nInteractive Servo Control:")
        print("Commands: 'run_s1', 'run_s2', 'close_s1', 'close_s2', 'toggle_s1', 'toggle_s2', 'status', 'test', 'quit'")
        
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == 'run_s1':
                    servo.run_servo_s1()
                elif command == 'run_s2':
                    servo.run_servo_s2()
                elif command == 'close_s1':
                    servo.close_servo_s1()
                elif command == 'close_s2':
                    servo.close_servo_s2()
                elif command == 'toggle_s1':
                    servo.toggle_servo_s1()
                elif command == 'toggle_s2':
                    servo.toggle_servo_s2()
                elif command == 'status':
                    status = servo.get_status()
                    print(f"ServoModule: Current status - S1: {status['S1']}, S2: {status['S2']}")
                elif command == 'test':
                    servo.test_servo_cycle()
                elif command == 'quit' or command == 'exit':
                    print("Exiting...")
                    servo.cleanup()
                    break
                else:
                    print("Unknown command. Use: run_s1, run_s2, close_s1, close_s2, toggle_s1, toggle_s2, status, test, quit")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                servo.emergency_shutdown()
                break
                
    except Exception as e:
        print(f"Error: {e}")
        servo.emergency_shutdown()
