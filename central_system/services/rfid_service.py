import logging
import threading
import time
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RFIDService:
    """
    RFID Service for reading RFID cards via USB RFID reader.
    
    This service uses evdev to read input from a USB RFID reader 
    which typically behaves like a keyboard.
    
    For Windows systems, a simulation mode is available for testing.
    """
    
    def __init__(self):
        self.os_platform = sys.platform
        self.device_path = os.environ.get('RFID_DEVICE_PATH', None)
        self.simulation_mode = os.environ.get('RFID_SIMULATION_MODE', 'false').lower() == 'true'
        
        # Events and callbacks
        self.callbacks = []
        self.running = False
        self.read_thread = None
        
        # Try to auto-detect RFID reader on initialization
        if not self.device_path and self.os_platform.startswith('linux'):
            self._detect_rfid_device()
            
        logger.info(f"RFID Service initialized (OS: {self.os_platform}, Simulation: {self.simulation_mode}, Device: {self.device_path})")
    
    def _detect_rfid_device(self):
        """
        Auto-detect RFID device on Linux systems.
        """
        try:
            import evdev
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            
            # Check all input devices
            for device in devices:
                # Log available devices to help debug
                device_info = f"Found input device: {device.name} ({device.path})"
                capabilities = []
                
                # Check device capabilities
                if evdev.ecodes.EV_KEY in device.capabilities():
                    capabilities.append("Keyboard")
                if evdev.ecodes.EV_ABS in device.capabilities():
                    capabilities.append("Touchscreen/Pad")
                if evdev.ecodes.EV_REL in device.capabilities():
                    capabilities.append("Mouse/Pointer")
                    
                device_info += f" - Capabilities: {', '.join(capabilities)}"
                logger.info(device_info)
                
                # Look for devices that might be RFID readers
                # Many RFID readers present as HID keyboard devices
                if (
                    "rfid" in device.name.lower() or 
                    "card" in device.name.lower() or 
                    "reader" in device.name.lower() or 
                    "hid" in device.name.lower() or
                    "usb" in device.name.lower()
                ):
                    # Check if it has keyboard capabilities
                    if evdev.ecodes.EV_KEY in device.capabilities():
                        key_caps = device.capabilities().get(evdev.ecodes.EV_KEY, [])
                        # RFID readers typically have number keys at minimum
                        key_count = len(key_caps)
                        
                        if key_count > 10:  # It should have at least digit keys
                            self.device_path = device.path
                            logger.info(f"Auto-detected RFID reader: {device.name} ({device.path})")
                            return True
            
            logger.warning("No RFID reader device auto-detected. Will use simulation mode.")
            return False
            
        except ImportError:
            logger.error("evdev library not installed. Please install it with: pip install evdev")
            return False
        except Exception as e:
            logger.error(f"Error detecting RFID devices: {str(e)}")
            return False
    
    def start(self):
        """
        Start the RFID reading service.
        """
        if self.running:
            logger.warning("RFID Service is already running")
            return
        
        self.running = True
        
        # If we're not in simulation mode and on Linux, try one more time to detect the device
        if not self.simulation_mode and self.os_platform.startswith('linux') and not self.device_path:
            if not self._detect_rfid_device():
                logger.warning("No RFID device detected, falling back to simulation mode")
                self.simulation_mode = True
        
        if self.simulation_mode:
            logger.info("Starting RFID Service in simulation mode")
            self.read_thread = threading.Thread(target=self._simulate_rfid_reading)
        else:
            if self.os_platform.startswith('linux'):
                logger.info(f"Starting RFID Service in Linux mode with device: {self.device_path}")
                self.read_thread = threading.Thread(target=self._read_linux_rfid)
            else:
                logger.warning(f"RFID hardware mode not supported on {self.os_platform}, falling back to simulation")
                self.read_thread = threading.Thread(target=self._simulate_rfid_reading)
        
        self.read_thread.daemon = True
        self.read_thread.start()
        logger.info("RFID Service started")
    
    def stop(self):
        """
        Stop the RFID reading service.
        """
        self.running = False
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=1.0)
        logger.info("RFID Service stopped")
    
    def register_callback(self, callback):
        """
        Register a callback function to be called when an RFID card is read.
        
        Args:
            callback (callable): Function that takes an RFID UID string as argument
        """
        self.callbacks.append(callback)
        logger.info(f"Registered RFID callback: {callback.__name__}")
    
    def _notify_callbacks(self, rfid_uid):
        """
        Notify all registered callbacks with the RFID UID.
        
        Args:
            rfid_uid (str): The RFID UID that was read
        """
        for callback in self.callbacks:
            try:
                callback(rfid_uid)
            except Exception as e:
                logger.error(f"Error in RFID callback: {str(e)}")
    
    def _read_linux_rfid(self):
        """
        Read RFID input using evdev on Linux.
        """
        try:
            import evdev
            from evdev import categorize, ecodes
            
            # Verify device path is available
            if not self.device_path:
                logger.error("No RFID device path specified. Falling back to simulation mode.")
                self.simulation_mode = True
                self._simulate_rfid_reading()
                return
            
            try:
                # Open the device
                device = evdev.InputDevice(self.device_path)
                logger.info(f"Reading RFID from device: {device.name} ({self.device_path})")
            except Exception as e:
                logger.error(f"Error opening RFID device {self.device_path}: {str(e)}")
                logger.info("Falling back to simulation mode")
                self.simulation_mode = True
                self._simulate_rfid_reading()
                return
            
            # Mapping from key codes to characters
            key_map = {
                evdev.ecodes.KEY_0: "0", evdev.ecodes.KEY_1: "1",
                evdev.ecodes.KEY_2: "2", evdev.ecodes.KEY_3: "3",
                evdev.ecodes.KEY_4: "4", evdev.ecodes.KEY_5: "5",
                evdev.ecodes.KEY_6: "6", evdev.ecodes.KEY_7: "7",
                evdev.ecodes.KEY_8: "8", evdev.ecodes.KEY_9: "9",
                evdev.ecodes.KEY_A: "A", evdev.ecodes.KEY_B: "B",
                evdev.ecodes.KEY_C: "C", evdev.ecodes.KEY_D: "D",
                evdev.ecodes.KEY_E: "E", evdev.ecodes.KEY_F: "F"
            }
            
            # Read input events
            current_rfid = ""
            last_event_time = 0
            
            logger.info("RFID reader is active and waiting for cards")
            
            while self.running:
                try:
                    for event in device.read_loop():
                        if not self.running:
                            break
                        
                        # Reset the RFID string if there's a pause between key events
                        current_time = time.time()
                        if current_time - last_event_time > 0.5 and current_rfid:
                            current_rfid = ""
                        
                        last_event_time = current_time
                        
                        if event.type == evdev.ecodes.EV_KEY and event.value == 1:  # Key pressed
                            if event.code in key_map:
                                current_rfid += key_map[event.code]
                            elif event.code == evdev.ecodes.KEY_ENTER:
                                if current_rfid:
                                    logger.info(f"RFID read: {current_rfid}")
                                    self._notify_callbacks(current_rfid)
                                    current_rfid = ""
                except OSError as e:
                    logger.error(f"Device read error (device may have been disconnected): {str(e)}")
                    # Try to reopen the device
                    try:
                        device = evdev.InputDevice(self.device_path)
                        logger.info(f"Reconnected to RFID device: {device.name}")
                    except Exception as e2:
                        logger.error(f"Failed to reopen device: {str(e2)}")
                        time.sleep(5)  # Wait before trying again
        
        except ImportError:
            logger.error("evdev library not installed. Please install it with: pip install evdev")
            logger.info("Falling back to simulation mode")
            self.simulation_mode = True
            self._simulate_rfid_reading()
        except Exception as e:
            logger.error(f"Error reading RFID: {str(e)}")
            logger.info("Falling back to simulation mode")
            self.simulation_mode = True
            self._simulate_rfid_reading()
    
    def _simulate_rfid_reading(self):
        """
        Simulate RFID reading for development and testing.
        """
        logger.info("RFID simulation mode active. Use simulate_card_read() to trigger simulated reads.")
        
        while self.running:
            time.sleep(1)  # Just keep the thread alive
    
    def simulate_card_read(self, rfid_uid=None):
        """
        Simulate an RFID card read with a specified or random UID.
        
        Args:
            rfid_uid (str, optional): RFID UID to simulate. If None, a random UID is generated.
        """
        if not rfid_uid:
            # Generate a random RFID UID (8 characters hexadecimal)
            import random
            rfid_uid = ''.join(random.choices('0123456789ABCDEF', k=8))
        
        logger.info(f"Simulating RFID read: {rfid_uid}")
        self._notify_callbacks(rfid_uid)
        return rfid_uid

# Singleton instance
rfid_service = None

def get_rfid_service():
    """
    Get the singleton RFID service instance.
    """
    global rfid_service
    if rfid_service is None:
        rfid_service = RFIDService()
    return rfid_service 