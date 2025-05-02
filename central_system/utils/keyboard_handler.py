import os
import subprocess
import logging
from PyQt5.QtCore import QObject, QEvent, Qt
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
        
        logger.info(f"Initialized keyboard handler with keyboard type: {self.keyboard_type}")
    
    def _detect_keyboard(self):
        """Detect which virtual keyboard is installed on the system.
        
        Returns:
            str: The keyboard type ('squeekboard', 'onboard', 'matchbox-keyboard', or None)
        """
        # Check for each supported keyboard in order of preference
        keyboards = ['squeekboard', 'onboard', 'matchbox-keyboard']
        
        for keyboard in keyboards:
            try:
                result = subprocess.run(['which', keyboard], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
                if result.returncode == 0:
                    logger.info(f"Found virtual keyboard: {keyboard}")
                    return keyboard
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
            self.show_keyboard()
        
        # Handle focus out events for text input widgets
        elif event.type() == QEvent.FocusOut and obj == self.current_focus_widget:
            # Only hide keyboard if focus is not moving to another text input
            focus_widget = QApplication.focusWidget()
            if not (isinstance(focus_widget, QLineEdit) or isinstance(focus_widget, QTextEdit)):
                self.hide_keyboard()
                self.current_focus_widget = None
        
        # Pass the event along
        return super(KeyboardHandler, self).eventFilter(obj, event)
    
    def show_keyboard(self):
        """Show the appropriate virtual keyboard."""
        if not self.keyboard_type:
            logger.warning("Cannot show keyboard - no supported keyboard installed")
            return
        
        # Don't start another instance if already running
        if self.keyboard_process and self.keyboard_process.poll() is None:
            logger.debug("Keyboard already running")
            return
        
        try:
            if self.keyboard_type == 'squeekboard':
                self.keyboard_process = subprocess.Popen(['squeekboard'])
            elif self.keyboard_type == 'onboard':
                self.keyboard_process = subprocess.Popen(['onboard', '--size=small', '--layout=Phone'])
            elif self.keyboard_type == 'matchbox-keyboard':
                self.keyboard_process = subprocess.Popen(['matchbox-keyboard'])
            
            logger.info(f"Started virtual keyboard: {self.keyboard_type}")
        except Exception as e:
            logger.error(f"Failed to start virtual keyboard: {e}")
    
    def hide_keyboard(self):
        """Hide the virtual keyboard."""
        if not self.keyboard_process:
            return
        
        try:
            # Check if process is still running
            if self.keyboard_process.poll() is None:
                self.keyboard_process.terminate()
                logger.info("Virtual keyboard terminated")
        except Exception as e:
            logger.error(f"Error terminating virtual keyboard: {e}")
        
        self.keyboard_process = None

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