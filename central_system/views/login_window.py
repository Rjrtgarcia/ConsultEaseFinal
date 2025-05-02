from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon
import os

from .base_window import BaseWindow

class LoginWindow(BaseWindow):
    """
    Login window for student RFID authentication.
    """
    # Signal to notify when a student is authenticated
    student_authenticated = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Initialize state variables
        self.rfid_reading = False
        self.scanning_timer = QTimer(self)
        self.scanning_timer.timeout.connect(self.update_scanning_animation)
        self.scanning_animation_frame = 0
        
        # For simulation during development - add to left side panel
        self.left_panel = QFrame(self)
        self.left_panel.setStyleSheet("background-color: #4a86e8;")
        self.left_panel.setFixedWidth(250)
        self.left_panel.move(0, 0)
        
        left_panel_layout = QVBoxLayout(self.left_panel)
        left_panel_layout.setAlignment(Qt.AlignCenter)
        
        self.simulate_button = QPushButton("Simulate RFID Scan")
        self.simulate_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #4a86e8;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        self.simulate_button.clicked.connect(self.simulate_rfid_scan)
        left_panel_layout.addWidget(self.simulate_button)
    
    def init_ui(self):
        """
        Initialize the login UI components.
        """
        # Set up main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create content widget with proper margin
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(50, 30, 50, 30)
        content_layout.setSpacing(20)
        
        # Dark header background
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #232323; color: white;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("ConsultEase")
        title_label.setStyleSheet("font-size: 36pt; font-weight: bold; color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Instruction label
        instruction_label = QLabel("Please scan your RFID card to authenticate")
        instruction_label.setStyleSheet("font-size: 18pt; color: white;")
        instruction_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(instruction_label)
        
        # Add header to main layout
        main_layout.addWidget(header_frame, 0)
        
        # Content area - white background
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #f5f5f5;")
        content_frame_layout = QVBoxLayout(content_frame)
        content_frame_layout.setContentsMargins(50, 50, 50, 50)
        
        # RFID scanning indicator
        self.scanning_frame = QFrame()
        self.scanning_frame.setStyleSheet('''
            QFrame {
                background-color: #e0e0e0;
                border-radius: 10px;
                border: 2px solid #ccc;
            }
        ''')
        scanning_layout = QVBoxLayout(self.scanning_frame)
        scanning_layout.setContentsMargins(30, 30, 30, 30)
        scanning_layout.setSpacing(20)
        
        self.scanning_status_label = QLabel("Ready to Scan")
        self.scanning_status_label.setStyleSheet("font-size: 20pt; color: #4a86e8;")
        self.scanning_status_label.setAlignment(Qt.AlignCenter)
        scanning_layout.addWidget(self.scanning_status_label)
        
        self.rfid_icon_label = QLabel()
        # Ideally, we would have an RFID icon image here
        self.rfid_icon_label.setText("🔄")
        self.rfid_icon_label.setStyleSheet("font-size: 48pt; color: #4a86e8;")
        self.rfid_icon_label.setAlignment(Qt.AlignCenter)
        scanning_layout.addWidget(self.rfid_icon_label)
        
        content_frame_layout.addWidget(self.scanning_frame, 1)
        
        # Add content to main layout
        main_layout.addWidget(content_frame, 1)
        
        # Footer with admin login button
        footer_frame = QFrame()
        footer_frame.setStyleSheet("background-color: #232323;")
        footer_frame.setFixedHeight(70)
        footer_layout = QHBoxLayout(footer_frame)
        
        # Admin login button
        admin_button = QPushButton("Admin Login")
        admin_button.setStyleSheet('''
            QPushButton {
                background-color: #808080;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                max-width: 200px;
            }
            QPushButton:hover {
                background-color: #909090;
            }
        ''')
        admin_button.clicked.connect(self.admin_login)
        
        footer_layout.addStretch()
        footer_layout.addWidget(admin_button)
        footer_layout.addStretch()
        
        main_layout.addWidget(footer_frame, 0)
        
        # Set the main layout to a widget and make it the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def showEvent(self, event):
        """Override showEvent to properly position side panel"""
        super().showEvent(event)
        self.left_panel.setFixedHeight(self.height())
        
    def resizeEvent(self, event):
        """Handle window resize to adjust side panel"""
        super().resizeEvent(event)
        if hasattr(self, 'left_panel'):
            self.left_panel.setFixedHeight(self.height())
    
    def start_rfid_scanning(self):
        """
        Start the RFID scanning animation and process.
        """
        self.rfid_reading = True
        self.scanning_status_label.setText("Scanning...")
        self.scanning_status_label.setStyleSheet("font-size: 20pt; color: #4a86e8;")
        self.scanning_frame.setStyleSheet('''
            QFrame {
                background-color: #e0e0e0;
                border-radius: 10px;
                border: 2px solid #4a86e8;
            }
        ''')
        self.scanning_timer.start(500)  # Update animation every 500ms
    
    def stop_rfid_scanning(self):
        """
        Stop the RFID scanning animation.
        """
        self.rfid_reading = False
        self.scanning_timer.stop()
        self.scanning_status_label.setText("Ready to Scan")
        self.scanning_status_label.setStyleSheet("font-size: 20pt; color: #4a86e8;")
        self.scanning_frame.setStyleSheet('''
            QFrame {
                background-color: #e0e0e0;
                border-radius: 10px;
                border: 2px solid #ccc;
            }
        ''')
        self.rfid_icon_label.setText("🔄")
    
    def update_scanning_animation(self):
        """
        Update the scanning animation frames.
        """
        animations = ["🔄", "🔁", "🔃", "🔂"]
        self.scanning_animation_frame = (self.scanning_animation_frame + 1) % len(animations)
        self.rfid_icon_label.setText(animations[self.scanning_animation_frame])
    
    def handle_rfid_read(self, rfid_uid, student=None):
        """
        Handle RFID read event.
        
        Args:
            rfid_uid (str): The RFID UID that was read
            student (object, optional): Student object if already validated
        """
        # Stop scanning animation
        self.stop_rfid_scanning()
        
        if student:
            # Authentication successful
            self.show_success(f"Welcome, {student.name}!")
            self.student_authenticated.emit(student)
        else:
            # Authentication failed
            self.show_error("RFID card not recognized. Please try again or contact an administrator.")
    
    def show_success(self, message):
        """
        Show success message and visual feedback.
        """
        self.scanning_status_label.setText("Authenticated")
        self.scanning_status_label.setStyleSheet("font-size: 20pt; color: #4caf50;")
        self.scanning_frame.setStyleSheet('''
            QFrame {
                background-color: #e8f5e9;
                border-radius: 10px;
                border: 2px solid #4caf50;
            }
        ''')
        self.rfid_icon_label.setText("✅")
        
        # Show message in a popup
        QMessageBox.information(self, "Authentication Success", message)
    
    def show_error(self, message):
        """
        Show error message and visual feedback.
        """
        self.scanning_status_label.setText("Error")
        self.scanning_status_label.setStyleSheet("font-size: 20pt; color: #f44336;")
        self.scanning_frame.setStyleSheet('''
            QFrame {
                background-color: #ffebee;
                border-radius: 10px;
                border: 2px solid #f44336;
            }
        ''')
        self.rfid_icon_label.setText("❌")
        
        # Show error in a popup
        QMessageBox.warning(self, "Authentication Error", message)
        
        # Reset after a delay
        QTimer.singleShot(3000, self.stop_rfid_scanning)
    
    def admin_login(self):
        """
        Handle admin login button click.
        """
        self.change_window.emit("admin_login", None)
    
    def simulate_rfid_scan(self):
        """
        Simulate an RFID scan for development purposes.
        """
        # This would be connected to the RFID service's simulate_card_read method
        # and the result would be processed through the normal authentication flow
        self.start_rfid_scanning()
        
        # Simulate processing delay
        QTimer.singleShot(1500, lambda: self.handle_rfid_read("SIMULATED", None)) 