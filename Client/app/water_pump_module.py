#!/usr/bin/env python3

import time
import grovepi
import threading
import state_constants as states

class WaterPumpModule:
    def __init__(self, state_manager, relay_port=3, auto_shutoff_duration=6):
        """
        Initialize the WaterPumpModule with relay control and auto-shutoff
        
        Args:
            state_manager: State manager instance for tracking pump state
            relay_port: Digital port number where the relay is connected (default: D3)
            auto_shutoff_duration: Duration in seconds after which pump automatically turns off
        """
        self.state_manager = state_manager
        self.relay_port = relay_port
        self.auto_shutoff_duration = auto_shutoff_duration
        self.is_initialized = False
        self.shutoff_timer = None
        
        # Initialize the relay
        self._init_relay()
    
    def _init_relay(self):
        """Initialize the relay pin as output"""
        try:
            grovepi.pinMode(self.relay_port, "OUTPUT")
            # Start with pump OFF
            grovepi.digitalWrite(self.relay_port, 0)
            self.is_initialized = True
            print(f"WaterPumpModule: Relay initialized on port D{self.relay_port}")
        except Exception as e:
            print(f"WaterPumpModule: Error initializing relay: {e}")
            self.is_initialized = False
    
    def _auto_shutoff(self):
        """Internal method to automatically turn off the pump after specified duration"""
        print(f"WaterPumpModule: Auto-shutoff triggered after {self.auto_shutoff_duration} seconds")
        self.turn_off()
    
    def turn_on(self, duration=None):
        """
        Turn the water pump ON by activating the relay
        
        Args:
            duration: Optional duration in seconds to override default auto-shutoff
        """
        if not self.is_initialized:
            print("WaterPumpModule: ERROR - Relay not initialized!")
            return False
        
        # Cancel any existing timer
        if self.shutoff_timer:
            self.shutoff_timer.cancel()
        
        try:
            print("WaterPumpModule: Turning water pump ON")
            grovepi.digitalWrite(self.relay_port, 1)
            self.state_manager.update_state(states.WATER_PUMP_ON)
            
            # Set auto-shutoff timer
            shutoff_time = duration if duration is not None else self.auto_shutoff_duration
            print(f"WaterPumpModule: Water pump will auto-shutoff in {shutoff_time} seconds")
            
            self.shutoff_timer = threading.Timer(shutoff_time, self._auto_shutoff)
            self.shutoff_timer.start()
            
            print("WaterPumpModule: Water pump is now ON - Device connected to relay is powered")
            return True
        except Exception as e:
            print(f"WaterPumpModule: Error turning water pump on: {e}")
            return False
    
    def turn_off(self):
        """Turn the water pump OFF by deactivating the relay"""
        if not self.is_initialized:
            print("WaterPumpModule: ERROR - Relay not initialized!")
            return False
        
        # Cancel any existing timer
        if self.shutoff_timer:
            self.shutoff_timer.cancel()
            self.shutoff_timer = None
        
        try:
            print("WaterPumpModule: Turning water pump OFF")
            grovepi.digitalWrite(self.relay_port, 0)
            self.state_manager.update_state(states.WATER_PUMP_OFF)
            print("WaterPumpModule: Water pump is now OFF - Device connected to relay is unpowered")
            return True
        except Exception as e:
            print(f"WaterPumpModule: Error turning water pump off: {e}")
            return False
    
    def toggle(self, duration=None):
        """Toggle the water pump state"""
        current_state = self.state_manager.get_current_state()
        
        if current_state == states.WATER_PUMP_ON:
            return self.turn_off()
        else:
            return self.turn_on(duration)
    
    def get_status(self):
        """Get the current water pump status"""
        current_state = self.state_manager.get_current_state()
        return current_state == states.WATER_PUMP_ON
    
    def get_remaining_time(self):
        """Get remaining time before auto-shutoff (if pump is running)"""
        if self.shutoff_timer and self.shutoff_timer.is_alive():
            # This is an approximation since Timer doesn't expose remaining time
            return "Timer active"
        return "No timer active"
    
    def set_auto_shutoff_duration(self, duration):
        """Set the auto-shutoff duration"""
        self.auto_shutoff_duration = duration
        print(f"WaterPumpModule: Auto-shutoff duration set to {duration} seconds")
    
    def test_pump_cycle(self, cycles=3, on_duration=5, off_duration=5):
        """
        Test the water pump by cycling it on and off
        
        Args:
            cycles: Number of test cycles
            on_duration: How long to keep pump on (seconds)
            off_duration: How long to keep pump off (seconds)
        """
        print(f"WaterPumpModule: Testing water pump cycle ({cycles} cycles)...")
        
        for i in range(cycles):
            print(f"WaterPumpModule: Test cycle {i+1}/{cycles}:")
            
            # Turn pump ON with custom duration
            if self.turn_on(duration=on_duration):
                time.sleep(on_duration + 1)  # Wait for auto-shutoff + 1 second
            
            # Manually turn off if still running
            if self.get_status():
                self.turn_off()
            
            # Wait between cycles
            time.sleep(off_duration)
        
        print("WaterPumpModule: Water pump test completed")
    
    def emergency_shutdown(self):
        """Emergency shutdown - immediately turn off the pump"""
        print("WaterPumpModule: EMERGENCY SHUTDOWN - Turning off water pump immediately!")
        
        # Cancel timer
        if self.shutoff_timer:
            self.shutoff_timer.cancel()
            self.shutoff_timer = None
        
        try:
            grovepi.digitalWrite(self.relay_port, 0)
            self.state_manager.update_state(states.WATER_PUMP_OFF)
            print("WaterPumpModule: Emergency shutdown completed")
        except Exception as e:
            print(f"WaterPumpModule: Error during emergency shutdown: {e}")
    
    def cleanup(self):
        """Clean shutdown of the water pump module"""
        print("WaterPumpModule: Cleaning up...")
        self.turn_off()
        print("WaterPumpModule: Cleanup completed")

# testing
if __name__ == '__main__':
    # Mock state manager for testing
    class MockStateManager:
        def __init__(self):
            self.current_state = states.WATER_PUMP_OFF
        
        def update_state(self, new_state):
            self.current_state = new_state
            print(f"StateManager: State updated to {new_state}")
        
        def get_current_state(self):
            return self.current_state
    
    print("WaterPumpModule Test Program")
    print("Connect Grove Relay to digital port D3")
    print("Connect your water pump to the relay output")
    print("WARNING: Only connect appropriate power devices to the relay!")
    print("=" * 50)
    
    # Create state manager and water pump module
    state_manager = MockStateManager()
    pump = WaterPumpModule(state_manager, relay_port=3, auto_shutoff_duration=10)
    
    try:
        # Interactive control
        print("\nInteractive Water Pump Control:")
        print("Commands: 'on', 'off', 'on <duration>', 'toggle', 'status', 'test', 'set_duration <seconds>', 'quit'")
        
        while True:
            try:
                command = input("Enter command: ").strip().lower()
                
                if command == 'on':
                    pump.turn_on()
                elif command.startswith('on '):
                    try:
                        duration = int(command.split()[1])
                        pump.turn_on(duration)
                    except (ValueError, IndexError):
                        print("Invalid duration. Use: on <seconds>")
                elif command == 'off':
                    pump.turn_off()
                elif command == 'toggle':
                    pump.toggle()
                elif command.startswith('toggle '):
                    try:
                        duration = int(command.split()[1])
                        pump.toggle(duration)
                    except (ValueError, IndexError):
                        print("Invalid duration. Use: toggle <seconds>")
                elif command == 'status':
                    status = "ON" if pump.get_status() else "OFF"
                    remaining = pump.get_remaining_time()
                    print(f"WaterPumpModule: Current status - {status}, Timer: {remaining}")
                elif command == 'test':
                    pump.test_pump_cycle()
                elif command.startswith('set_duration '):
                    try:
                        duration = int(command.split()[1])
                        pump.set_auto_shutoff_duration(duration)
                    except (ValueError, IndexError):
                        print("Invalid duration. Use: set_duration <seconds>")
                elif command == 'quit' or command == 'exit':
                    print("Exiting...")
                    pump.cleanup()
                    break
                else:
                    print("Unknown command. Use: on, off, toggle, status, test, set_duration <seconds>, quit")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                pump.emergency_shutdown()
                break
                
    except Exception as e:
        print(f"Error: {e}")
        pump.emergency_shutdown()