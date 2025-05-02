from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5.QtCore import Qt, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class BaseWindow(QMainWindow):
    """
    Base window class for ConsultEase.
    All windows should inherit from this class.
    """
    # Signal for changing windows
    change_window = pyqtSignal(str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """
        Initialize the UI components.
        This method should be overridden by subclasses.
        """
        # Set window properties
        self.setWindowTitle('ConsultEase')
        self.setMinimumSize(800, 480)  # Minimum size for Raspberry Pi 7" touchscreen
        self.apply_touch_friendly_style()
        
        # Center window on screen
        self.center()
    
    def apply_touch_friendly_style(self):
        """
        Apply touch-friendly styles to the application
        """
        self.setStyleSheet('''
            /* General styles */
            QWidget {
                font-size: 14pt;
            }
            
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            /* Touch-friendly buttons */
            QPushButton {
                min-height: 50px;
                padding: 10px 20px;
                font-size: 14pt;
                border-radius: 5px;
                background-color: #4a86e8;
                color: white;
            }
            
            QPushButton:hover {
                background-color: #5a96f8;
            }
            
            QPushButton:pressed {
                background-color: #3a76d8;
            }
            
            /* Touch-friendly input fields */
            QLineEdit, QTextEdit, QComboBox {
                min-height: 40px;
                padding: 5px 10px;
                font-size: 14pt;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #4a86e8;
            }
            
            /* Table headers and cells */
            QTableWidget {
                font-size: 12pt;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 8px;
                font-size: 12pt;
                font-weight: bold;
            }
            
            /* Tabs for better touch */
            QTabBar::tab {
                min-width: 120px;
                min-height: 40px;
                padding: 8px 16px;
                font-size: 14pt;
            }
            
            /* Dialog buttons */
            QDialogButtonBox > QPushButton {
                min-width: 100px;
                min-height: 40px;
            }
        ''')
        logger.info("Applied touch-optimized UI settings")
    
    def center(self):
        """
        Center the window on the screen.
        """
        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def keyPressEvent(self, event):
        """
        Handle key press events.
        """
        # Handle ESC key to go back to main menu
        if event.key() == Qt.Key_Escape:
            self.change_window.emit('login', None)
        else:
            super().keyPressEvent(event)
    
    def showEvent(self, event):
        """
        Called when the window is shown.
        """
        # Set window to fullscreen for better touch experience on Raspberry Pi
        # Uncomment this line when deploying on Raspberry Pi
        # self.showFullScreen()
        super().showEvent(event) 