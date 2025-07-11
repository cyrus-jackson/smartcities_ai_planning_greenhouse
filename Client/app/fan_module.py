#!/usr/bin/env python3

import time
import grovepi
import state_constants as states

class FanModule:
    def __init__(self, state_manager, relay_port=2):
        """
        Initialize the FanModule with relay control
        
        Args:
            state_manager: State manager instance for tracking fan state
            relay_port: Digital port number where the relay is connected (default: D2)
        """
        self.state_manager = state_manager
        self.relay_port = relay_port
        self.is_initialized = False
        
        # Initialize the relay
        self._init_relay()
    
    def _init_relay(self):
        """Initialize the relay pin as output"""
        try:
            grovepi.pinMode(self.relay_port, "OUTPUT")
            # Start with fan OFF
            grovepi.digitalWrite(self.relay_port, 0)
            self.is_initialized = True
            print(f"FanModule: Relay initialized on port D{self.relay_port}")
        except Exception as e:
            print(f"FanModule: Error initializing relay: {e}")
            self.is_initialized = False
    
    def turn_on(self):
        """Turn the fan ON by activating the relay"""
        if not self.is_initialized:
            print("FanModule: ERROR - Relay not initialized!")
            return False
        
        try:
            print("FanModule: Turning fan ON")
            grovepi.digitalWrite(self.relay_port, 1)
            self.state_manager.update_state(states.FAN_ON)
            print("FanModule: Fan is now ON - Device connected to relay is powered")
            return True
        except Exception as e:
            print(f"FanModule: Error turning fan on: {e}")
            return False
    
    def turn_off(self):
        """Turn the fan OFF by deactivating the relay"""
        if not self.is_initialized:
            print("FanModule: ERROR - Relay not initialized!")
            return False
        
        try:
            print("FanModule: Turning fan OFF")
            grovepi.digitalWrite(self.relay_port, 0)
            self.state_manager.update_state(states.FAN_OFF)
            print("FanModule: Fan is now OFF - Device connected to relay is unpowered")
            return True
        except Exception as e:
            print(f"FanModule: Error turning fan off: {e}")
            return False
    
    def toggle(self):
        current_state = self.state_manager.get_current_state()
        
        if current_state == states.FAN_ON:
            return self.turn_off()
        else:
            return self.turn_on()
    
    def get_status(self):
        """Get the current fan status"""
        current_state = self.state_manager.get_current_state()
        return current_state == states.FAN_ON
    
    def test_fan_cycle(self, cycles=3, on_duration=2, off_duration=2):
        """
        Test the fan by cycling it on and off
        
        Args:
            cycles: Number of test cycles
            on_duration: How long to keep fan on (seconds)
            off_duration: How long to keep fan off (seconds)
        """
        print(f"FanModule: Testing fan cycle ({cycles} cycles)...")
        
        for i in range(cycles):
            print(f"FanModule: Test cycle {i+1}/{cycles}:")
            
            # Turn fan ON
            if self.turn_on():
                time.sleep(on_duration)
            
            # Turn fan OFF
            if self.turn_off():
                time.sleep(off_duration)
        
        print("FanModule: Fan test completed")
    
    def emergency_shutdown(self):
        """Emergency shutdown - immediately turn off the fan"""
        print("FanModule: EMERGENCY SHUTDOWN - Turning off fan immediately!")
        try:
            grovepi.digitalWrite(self.relay_port, 0)
            self.state_manager.update_state(states.FAN_OFF)
            print("FanModule: Emergency shutdown completed")
        except Exception as e:
            print(f"FanModule: Error during emergency shutdown: {e}")
    
    def cleanup(self):
        """Clean shutdown of the fan module"""
        print("FanModule: Cleaning up...")
        self.turn_off()
        print("FanModule: Cleanup completed")

# Example usage and testing
if __name__ == '__main__':
    # Mock state manager for testing
    class MockStateManager:
        def __init__(self):
            self.current_state = states.FAN_OFF
        
        def update_state(self, new_state):
            self.current_state = new_state
            print(f"StateManager: State updated to {new_state}")
        
        def get_current_state(self):
            return self.current_state
    
    print("FanModule Test Program")
    print("Connect Grove Relay to digital port D2")
    print("Connect your fan to the relay output")
    print("WARNING: Only connect low-power devices to the relay!")
    print("=" * 50)
    
    # Create state manager and fan module
    state_manager = MockStateManager()
    fan = FanModule(state_manager)
    
    try:
        # Interactive control
        print("\nInteractive Fan Control:")
        print("Commands: 'on', 'off', 'toggle', 'status', 'test', 'quit'")
        
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == 'on':
                    fan.turn_on()
                elif command == 'off':
                    fan.turn_off()
                elif command == 'toggle':
                    fan.toggle()
                elif command == 'status':
                    status = "ON" if fan.get_status() else "OFF"
                    print(f"FanModule: Current status - {status}")
                elif command == 'test':
                    fan.test_fan_cycle()
                elif command == 'quit' or command == 'exit':
                    print("Exiting...")
                    fan.cleanup()
                    break
                else:
                    print("Unknown command. Use: on, off, toggle, status, test, quit")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                fan.emergency_shutdown()
                break
                
    except Exception as e:
        print(f"Error: {e}")
        fan.emergency_shutdown()