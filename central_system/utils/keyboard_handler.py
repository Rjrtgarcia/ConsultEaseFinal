import os
import subprocess
import logging
import signal
import time
import sys
from PyQt5.QtCore import QObject, QEvent, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QLineEdit, QTextEdit

logger = logging.getLogger(__name__)

class KeyboardHandler(QObject):
    """
    Handler for virtual keyboard management on touchscreen interfaces.
    
    This class manages the auto-showing of on-screen keyboards when text input
    fields receive focus, and hiding them when focus is lost. It supports
    multiple virtual keyboard implementations (squeekboard, onboard, matchbox-keyboard).
    """
    
    def __init__(self, parent=None):
        """Initialize the keyboard handler.
        
        Args:
            parent: Parent QObject
        """
        super(KeyboardHandler, self).__init__(parent)
        
        # Detect available keyboard
        self.keyboard_type = self._detect_keyboard()
        self.keyboard_process = None
        self.current_focus_widget = None
        self.keyboard_visible = False
        
        # Timer to add a slight delay for keyboard appearance
        self.keyboard_timer = QTimer(self)
        self.keyboard_timer.setSingleShot(True)
        self.keyboard_timer.timeout.connect(self._delayed_show_keyboard)
        
        # Log detected keyboard
        if self.keyboard_type:
            keyboard_info = f"Initialized keyboard handler with keyboard type: {self.keyboard_type}"
            self._check_keyboard_availability()
        else:
            keyboard_info = "No on-screen keyboard detected. Touch keyboard functionality will be disabled."
            
        logger.info(keyboard_info)
    
    def _check_keyboard_availability(self):
        """Check if the detected keyboard can actually be launched"""
        try:
            # Try to start and immediately kill the keyboard process
            if self.keyboard_type == 'squeekboard':
                startup_check = subprocess.Popen(['squeekboard', '--help'], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE)
            elif self.keyboard_type == 'onboard':
                startup_check = subprocess.Popen(['onboard', '--help'], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE)
            elif self.keyboard_type == 'matchbox-keyboard':
                startup_check = subprocess.Popen(['matchbox-keyboard', '--help'], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE)
            else:
                return False
                
            # Wait briefly then kill the process
            time.sleep(0.5)
            startup_check.terminate()
            return_code = startup_check.wait(timeout=1)
            
            logger.info(f"Keyboard availability check completed with return code: {return_code}")
            return True
        except Exception as e:
            logger.error(f"Error checking keyboard availability: {e}")
            if isinstance(e, FileNotFoundError):
                logger.warning(f"Keyboard {self.keyboard_type} was found by 'which' but can't be executed.")
                self.keyboard_type = None
            return False
    
    def _detect_keyboard(self):
        """Detect which virtual keyboard is installed on the system.
        
        Returns:
            str: The keyboard type ('squeekboard', 'onboard', 'matchbox-keyboard', or None)
        """
        # If not on Linux, return None as on-screen keyboards are primarily for Linux-based systems
        if not sys.platform.startswith('linux'):
            logger.info("Not on Linux platform, on-screen keyboard detection skipped")
            return None
            
        # Check environment variable override
        env_keyboard = os.environ.get('CONSULTEASE_KEYBOARD', None)
        if env_keyboard:
            logger.info(f"Using keyboard specified in environment: {env_keyboard}")
            return env_keyboard
            
        # Check for each supported keyboard in order of preference
        keyboards = ['squeekboard', 'onboard', 'matchbox-keyboard']
        
        # Log all available keyboards for debugging
        logger.info("Checking for available on-screen keyboards...")
        
        for keyboard in keyboards:
            try:
                result = subprocess.run(['which', keyboard], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
                if result.returncode == 0:
                    keyboard_path = result.stdout.decode('utf-8').strip()
                    logger.info(f"Found virtual keyboard: {keyboard} at {keyboard_path}")
                    return keyboard
                else:
                    logger.info(f"Keyboard not found: {keyboard}")
            except Exception as e:
                logger.debug(f"Error checking for keyboard {keyboard}: {e}")
        
        logger.warning("No supported virtual keyboard found")
        return None
    
    def eventFilter(self, obj, event):
        """Filter events to detect focus changes in text input widgets.
        
        Args:
            obj: The object that received the event
            event: The event
            
        Returns:
            bool: True if the event was handled and should be filtered out
        """
        # Handle focus in events for text input widgets
        if event.type() == QEvent.FocusIn and (isinstance(obj, QLineEdit) or isinstance(obj, QTextEdit)):
            self.current_focus_widget = obj
            # Delay keyboard showing slightly to avoid rapid show/hide cycles
            if not self.keyboard_timer.isActive() and not self.keyboard_visible:
                self.keyboard_timer.start(300)  # 300ms delay

        # Handle focus out events for text input widgets
        elif event.type() == QEvent.FocusOut and obj == self.current_focus_widget:
            # Get the new focus widget
            focus_widget = QApplication.focusWidget()
            
            # Only hide keyboard if focus is not moving to another text input
            if not (isinstance(focus_widget, QLineEdit) or isinstance(focus_widget, QTextEdit)):
                self.hide_keyboard()
                self.current_focus_widget = None
                
            # If moving to another text input, update the current focus widget
            elif focus_widget != obj:
                self.current_focus_widget = focus_widget
        
        # Pass the event along
        return super(KeyboardHandler, self).eventFilter(obj, event)
    
    def _delayed_show_keyboard(self):
        """Show keyboard after a short delay to prevent flicker"""
        if self.current_focus_widget and self.current_focus_widget.isVisible():
            self.show_keyboard()
    
    def show_keyboard(self):
        """Show the appropriate virtual keyboard."""
        if not self.keyboard_type:
            logger.debug("Cannot show keyboard - no supported keyboard installed")
            return
            
        # Don't start another instance if already marked as visible
        if self.keyboard_visible:
            logger.debug("Keyboard already visible")
            return
            
        # Check if process exists and is still running
        if self.keyboard_process:
            try:
                if self.keyboard_process.poll() is None:
                    logger.debug("Keyboard process still running")
                    self.keyboard_visible = True
                    return
            except Exception:
                # Process might be invalid, create a new one
                self.keyboard_process = None
        
        try:
            logger.info(f"Starting virtual keyboard: {self.keyboard_type}")
            
            if self.keyboard_type == 'squeekboard':
                # Use more robust method to launch squeekboard
                self.keyboard_process = subprocess.Popen(
                    ['squeekboard'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True  # Ensure it runs in its own session
                )
            elif self.keyboard_type == 'onboard':
                # Onboard with more appropriate options for touch screens
                self.keyboard_process = subprocess.Popen(
                    ['onboard', '--size=small', '--layout=Phone', '--enable-background-transparency'], 
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif self.keyboard_type == 'matchbox-keyboard':
                self.keyboard_process = subprocess.Popen(
                    ['matchbox-keyboard'],
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
            
            self.keyboard_visible = True
            logger.info(f"Virtual keyboard started: {self.keyboard_type}")
        except Exception as e:
            logger.error(f"Failed to start virtual keyboard: {e}")
            self.keyboard_visible = False
    
    def hide_keyboard(self):
        """Hide the virtual keyboard."""
        if not self.keyboard_visible or not self.keyboard_process:
            return
        
        try:
            # Check if process is still running
            if self.keyboard_process.poll() is None:
                # Try gentle termination first
                self.keyboard_process.terminate()
                
                # Wait briefly for termination
                try:
                    self.keyboard_process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    # Force kill if not terminated
                    if self.keyboard_process.poll() is None:
                        try:
                            self.keyboard_process.kill()
                        except:
                            # On Linux, try using os.killpg as last resort
                            if hasattr(os, 'killpg'):
                                try:
                                    os.killpg(os.getpgid(self.keyboard_process.pid), signal.SIGKILL)
                                except:
                                    pass
                
                logger.info("Virtual keyboard terminated")
        except Exception as e:
            logger.error(f"Error terminating virtual keyboard: {e}")
        
        self.keyboard_process = None
        self.keyboard_visible = False

def install_keyboard_handler(app):
    """Install the keyboard handler for the application.
    
    Args:
        app: QApplication instance
        
    Returns:
        KeyboardHandler: The installed keyboard handler instance
    """
    handler = KeyboardHandler()
    
    # Install event filter on application to catch all events
    app.installEventFilter(handler)
    
    return handler 