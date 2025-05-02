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
        super().init_ui()
        
        # Set window properties
        self.setWindowTitle('ConsultEase - Admin Login')
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Add logo or title
        title_label = QLabel('Admin Login')
        title_label.setStyleSheet('font-size: 24pt; font-weight: bold; color: #4a86e8;')
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Add spacer
        main_layout.addSpacing(30)
        
        # Create form layout for inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter username')
        self.username_input.setMinimumHeight(50)  # Make touch-friendly
        form_layout.addRow('Username:', self.username_input)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(50)  # Make touch-friendly
        form_layout.addRow('Password:', self.password_input)
        
        # Add form layout to main layout
        main_layout.addLayout(form_layout)
        
        # Add error message label (hidden by default)
        self.error_label = QLabel('')
        self.error_label.setStyleSheet('color: red; font-weight: bold;')
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)
        main_layout.addWidget(self.error_label)
        
        # Add button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # Back button
        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.back_to_login)
        button_layout.addWidget(self.back_button)
        
        # Login button
        self.login_button = QPushButton('Login')
        self.login_button.setStyleSheet('background-color: #4CAF50; font-weight: bold;')
        self.login_button.clicked.connect(self.login)
        button_layout.addWidget(self.login_button)
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
        
        # Add spacer at the bottom to push content up
        main_layout.addStretch()
        
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
        
        # Emit the signal with the credentials
        self.admin_authenticated.emit((username, password))
    
    def back_to_login(self):
        """
        Go back to the login screen.
        """
        self.change_window.emit('login', None) 