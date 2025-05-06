from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QMessageBox, QLineEdit)
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

        # The left panel is no longer needed since we moved the simulate button
        # to the scanning frame

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

        # Add manual RFID input field
        manual_input_layout = QHBoxLayout()

        self.rfid_input = QLineEdit()
        self.rfid_input.setPlaceholderText("Enter RFID manually")
        self.rfid_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                font-size: 14pt;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #4a86e8;
            }
        """)
        self.rfid_input.returnPressed.connect(self.handle_manual_rfid_entry)
        manual_input_layout.addWidget(self.rfid_input, 3)

        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        submit_button.clicked.connect(self.handle_manual_rfid_entry)
        manual_input_layout.addWidget(submit_button, 1)

        scanning_layout.addLayout(manual_input_layout)

        # Add the simulate button inside the scanning frame
        self.simulate_button = QPushButton("Simulate RFID Scan")
        self.simulate_button.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
        """)
        self.simulate_button.clicked.connect(self.simulate_rfid_scan)
        scanning_layout.addWidget(self.simulate_button)

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
        """Override showEvent"""
        super().showEvent(event)

    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)

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
        # Start the scanning animation
        self.start_rfid_scanning()

        # Get the RFID service and simulate a card read
        try:
            from ..services import get_rfid_service
            rfid_service = get_rfid_service()

            # Simulate a card read - this will trigger the normal authentication flow
            # through the registered callbacks
            rfid_service.simulate_card_read("SIMULATED")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error simulating RFID scan: {str(e)}")

            # If there's an error, stop the scanning animation and show an error
            QTimer.singleShot(1000, lambda: self.handle_rfid_read("SIMULATED", None))

    def handle_manual_rfid_entry(self):
        """
        Handle manual RFID entry from the input field.
        """
        rfid_uid = self.rfid_input.text().strip()
        if rfid_uid:
            self.rfid_input.clear()
            self.start_rfid_scanning()

            # Get the RFID service and simulate a card read with the entered UID
            try:
                from ..services import get_rfid_service
                rfid_service = get_rfid_service()

                # Use the entered RFID UID - this will trigger the normal authentication flow
                # through the registered callbacks
                rfid_service.simulate_card_read(rfid_uid)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error processing manual RFID entry: {str(e)}")

                # If there's an error, stop the scanning animation and show an error
                QTimer.singleShot(1000, lambda: self.handle_rfid_read(rfid_uid, None))

# Create a script to ensure the keyboard works on Raspberry Pi
def create_keyboard_setup_script():
    """
    Create a script to set up the virtual keyboard on the Raspberry Pi.
    This should be called when deploying the application.
    """
    script_content = """#!/bin/bash
# Setup script for ConsultEase virtual keyboard
echo "Setting up ConsultEase virtual keyboard..."

# Ensure squeekboard is installed
if ! command -v squeekboard &> /dev/null; then
    echo "Squeekboard not found, attempting to install..."
    sudo apt update
    sudo apt install -y squeekboard
fi

# Ensure squeekboard service is enabled
systemctl --user enable squeekboard.service
systemctl --user restart squeekboard.service

# Set environment variables for proper keyboard operation
cat > ~/.config/environment.d/consultease.conf << EOF
# ConsultEase keyboard environment variables
GDK_BACKEND=wayland,x11
QT_QPA_PLATFORM=wayland;xcb
SQUEEKBOARD_FORCE=1
CONSULTEASE_KEYBOARD_DEBUG=true
EOF

echo "Creating keyboard trigger script..."
cat > ~/keyboard-toggle.sh << EOF
#!/bin/bash
# Toggle squeekboard visibility
if dbus-send --type=method_call --dest=sm.puri.OSK0 /sm/puri/OSK0 sm.puri.OSK0.GetVisible | grep -q "boolean true"; then
    dbus-send --type=method_call --dest=sm.puri.OSK0 /sm/puri/OSK0 sm.puri.OSK0.SetVisible boolean:false
    echo "Keyboard hidden"
else
    dbus-send --type=method_call --dest=sm.puri.OSK0 /sm/puri/OSK0 sm.puri.OSK0.SetVisible boolean:true
    echo "Keyboard shown"
fi
EOF
chmod +x ~/keyboard-toggle.sh

echo "Setup complete! Reboot your system for changes to take effect."
echo "If the keyboard still doesn't appear, run ~/keyboard-toggle.sh to manually show it"
"""

    # Create scripts directory if it doesn't exist
    script_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts")
    os.makedirs(script_dir, exist_ok=True)

    # Write the script
    script_path = os.path.join(script_dir, "setup_keyboard.sh")
    with open(script_path, "w") as f:
        f.write(script_content)

    # Make the script executable on Unix
    if os.name == "posix":
        import stat
        st = os.stat(script_path)
        os.chmod(script_path, st.st_mode | stat.S_IEXEC)

    return script_path