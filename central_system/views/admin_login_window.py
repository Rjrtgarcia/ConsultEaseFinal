from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QLineEdit, QFrame, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

import os
from .base_window import BaseWindow

class AdminLoginWindow(BaseWindow):
    """
    Admin login window for secure access to the admin interface.
    """
    # Signal to notify when an admin is authenticated
    admin_authenticated = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """
        Initialize the UI components.
        """
        # Set window properties
        self.setWindowTitle('ConsultEase - Admin Login')

        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Dark header background
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #232323; color: white;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel('Admin Login')
        title_label.setStyleSheet('font-size: 36pt; font-weight: bold; color: white;')
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        # Add header to main layout
        main_layout.addWidget(header_frame, 0)

        # Content area - white background
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #f5f5f5;")
        content_frame_layout = QVBoxLayout(content_frame)
        content_frame_layout.setContentsMargins(50, 50, 50, 50)

        # Create form layout for inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Username input
        username_label = QLabel('Username:')
        username_label.setStyleSheet('font-size: 16pt; font-weight: bold;')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter username')
        self.username_input.setMinimumHeight(50)  # Make touch-friendly
        self.username_input.setProperty("keyboardOnFocus", True)  # Custom property to help keyboard handler
        self.username_input.setStyleSheet('''
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14pt;
            }
            QLineEdit:focus {
                border: 2px solid #4a86e8;
            }
        ''')
        form_layout.addRow(username_label, self.username_input)

        # Password input
        password_label = QLabel('Password:')
        password_label.setStyleSheet('font-size: 16pt; font-weight: bold;')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(50)  # Make touch-friendly
        self.password_input.setProperty("keyboardOnFocus", True)  # Custom property to help keyboard handler
        self.password_input.setStyleSheet('''
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14pt;
            }
            QLineEdit:focus {
                border: 2px solid #4a86e8;
            }
        ''')
        form_layout.addRow(password_label, self.password_input)

        # Add form layout to content layout
        content_frame_layout.addLayout(form_layout)

        # Add error message label (hidden by default)
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: #f44336; font-weight: bold; font-size: 14pt;')
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)
        content_frame_layout.addWidget(self.error_label)

        # Add spacer
        content_frame_layout.addStretch()

        # Add content to main layout
        main_layout.addWidget(content_frame, 1)

        # Footer with buttons
        footer_frame = QFrame()
        footer_frame.setStyleSheet("background-color: #232323;")
        footer_frame.setMinimumHeight(80)
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(50, 10, 50, 10)

        # Back button
        self.back_button = QPushButton('Back')
        self.back_button.setStyleSheet('''
            QPushButton {
                background-color: #808080;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14pt;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #909090;
            }
        ''')
        self.back_button.clicked.connect(self.back_to_login)

        # Login button
        self.login_button = QPushButton('Login')
        self.login_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14pt;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        self.login_button.clicked.connect(self.login)

        footer_layout.addWidget(self.back_button)
        footer_layout.addStretch()
        footer_layout.addWidget(self.login_button)

        # Add footer to main layout
        main_layout.addWidget(footer_frame, 0)

        # Set central widget
        self.setCentralWidget(central_widget)

        # Set up keyboard shortcuts
        self.password_input.returnPressed.connect(self.login)
        self.username_input.returnPressed.connect(self.focus_password)

        # Configure tab order for better keyboard navigation
        self.setTabOrder(self.username_input, self.password_input)
        self.setTabOrder(self.password_input, self.login_button)
        self.setTabOrder(self.login_button, self.back_button)

    def focus_password(self):
        """
        Focus on the password input field.
        """
        self.password_input.setFocus()

    def show_login_error(self, message):
        """
        Show an error message on the login form.

        Args:
            message (str): The error message to display.
        """
        self.error_label.setText(message)
        self.error_label.setVisible(True)

        # Clear the password field for security
        self.password_input.clear()

    def login(self):
        """
        Handle login button click.
        """
        # Hide any previous error message
        self.error_label.setVisible(False)

        # Get username and password
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # Validate inputs
        if not username:
            self.show_login_error('Please enter a username')
            self.username_input.setFocus()
            return

        if not password:
            self.show_login_error('Please enter a password')
            self.password_input.setFocus()
            return

        # Emit the signal with the credentials as a tuple
        self.admin_authenticated.emit((username, password))

    def back_to_login(self):
        """
        Go back to the login screen.
        """
        self.change_window.emit('login', None)

    def showEvent(self, event):
        """
        Override showEvent to trigger the keyboard when the window is shown.
        """
        super().showEvent(event)

        # Import necessary modules
        import logging
        import subprocess
        import sys

        logger = logging.getLogger(__name__)
        logger.info("AdminLoginWindow shown, triggering keyboard")

        # Focus the username input to trigger the keyboard
        self.username_input.setFocus()

        # Try to explicitly show the keyboard using DBus
        try:
            if sys.platform.startswith('linux'):
                # Try to use dbus-send to force the keyboard
                cmd = [
                    "dbus-send", "--type=method_call", "--dest=sm.puri.OSK0",
                    "/sm/puri/OSK0", "sm.puri.OSK0.SetVisible", "boolean:true"
                ]
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info("Sent dbus command to show squeekboard")
        except Exception as e:
            logger.error(f"Error showing keyboard: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")