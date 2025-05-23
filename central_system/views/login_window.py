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

        # Set up logging
        import logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing LoginWindow")

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

        # Refresh RFID service to ensure it has the latest student data
        try:
            from ..services import get_rfid_service
            rfid_service = get_rfid_service()
            rfid_service.refresh_student_data()
            self.logger.info("Refreshed RFID service student data when login window shown")
        except Exception as e:
            self.logger.error(f"Error refreshing RFID service: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

        # Start RFID scanning when the window is shown
        self.logger.info("LoginWindow shown, starting RFID scanning")
        self.start_rfid_scanning()

        # Force the keyboard to show up for manual RFID entry
        try:
            # Focus the RFID input field to trigger the keyboard
            self.rfid_input.setFocus()

            # Try to explicitly show the keyboard using DBus
            import subprocess
            import sys
            if sys.platform.startswith('linux'):
                try:
                    # Try to use dbus-send to force the keyboard
                    cmd = [
                        "dbus-send", "--type=method_call", "--dest=sm.puri.OSK0",
                        "/sm/puri/OSK0", "sm.puri.OSK0.SetVisible", "boolean:true"
                    ]
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.logger.info("Sent dbus command to show squeekboard")
                except Exception as e:
                    self.logger.error(f"Error showing keyboard: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error focusing RFID input: {str(e)}")

    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)

    def start_rfid_scanning(self):
        """
        Start the RFID scanning animation and process.
        """
        # Refresh RFID service to ensure it has the latest student data
        try:
            from ..services import get_rfid_service
            rfid_service = get_rfid_service()
            rfid_service.refresh_student_data()
            self.logger.info("Refreshed RFID service student data when starting RFID scanning")
        except Exception as e:
            self.logger.error(f"Error refreshing RFID service: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

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
        self.logger.info(f"LoginWindow.handle_rfid_read called with rfid_uid: {rfid_uid}, student: {student}")

        # Stop scanning animation
        self.stop_rfid_scanning()

        # If student is not provided, try to look it up directly
        if not student and rfid_uid:
            try:
                # First refresh the RFID service to ensure it has the latest student data
                try:
                    from ..services import get_rfid_service
                    rfid_service = get_rfid_service()
                    rfid_service.refresh_student_data()
                    self.logger.info("Refreshed RFID service student data before looking up student")
                except Exception as e:
                    self.logger.error(f"Error refreshing RFID service: {str(e)}")

                from ..models import Student, get_db
                db = get_db()

                # Try exact match first
                self.logger.info(f"Looking up student with RFID UID: {rfid_uid}")
                student = db.query(Student).filter(Student.rfid_uid == rfid_uid).first()

                # If no exact match, try case-insensitive match
                if not student:
                    self.logger.info(f"No exact match found, trying case-insensitive match for RFID: {rfid_uid}")
                    # For PostgreSQL
                    try:
                        student = db.query(Student).filter(Student.rfid_uid.ilike(rfid_uid)).first()
                    except:
                        # For SQLite
                        student = db.query(Student).filter(Student.rfid_uid.lower() == rfid_uid.lower()).first()

                if student:
                    self.logger.info(f"LoginWindow: Found student directly: {student.name} with RFID: {rfid_uid}")
                else:
                    # Log all students in the database for debugging
                    all_students = db.query(Student).all()
                    self.logger.warning(f"No student found for RFID {rfid_uid}")
                    self.logger.info(f"Available students in database: {len(all_students)}")
                    for s in all_students:
                        self.logger.info(f"  - ID: {s.id}, Name: {s.name}, RFID: {s.rfid_uid}")
            except Exception as e:
                self.logger.error(f"LoginWindow: Error looking up student: {str(e)}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")

        if student:
            # Authentication successful
            self.logger.info(f"Authentication successful for student: {student.name} with ID: {student.id}")
            self.show_success(f"Welcome, {student.name}!")

            # Log the emission of the signal
            self.logger.info(f"LoginWindow: Emitting student_authenticated signal for {student.name}")

            # Emit the signal to navigate to the dashboard
            self.student_authenticated.emit(student)

            # Also emit a change_window signal as a backup
            self.logger.info(f"LoginWindow: Emitting change_window signal for dashboard")
            self.change_window.emit("dashboard", student)

            # Force a delay to ensure the signals are processed
            QTimer.singleShot(500, lambda: self._force_dashboard_navigation(student))
        else:
            # Authentication failed
            self.logger.warning(f"Authentication failed for RFID: {rfid_uid}")
            self.show_error("RFID card not recognized. Please try again or contact an administrator.")

    def _force_dashboard_navigation(self, student):
        """
        Force navigation to dashboard as a fallback.

        Args:
            student (object): Student object
        """
        self.logger.info("Forcing dashboard navigation as fallback")
        self.change_window.emit("dashboard", student)

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
            # Try to get a real student RFID from the database
            from ..models import Student, get_db
            db = get_db()
            student = db.query(Student).first()

            if student and student.rfid_uid:
                self.logger.info(f"Simulating RFID scan with real student: {student.name}, RFID: {student.rfid_uid}")
                rfid_uid = student.rfid_uid
            else:
                self.logger.info("No students found in database, using default RFID")
                rfid_uid = "TESTCARD123"  # Use the test card we added

            from ..services import get_rfid_service
            rfid_service = get_rfid_service()

            # Refresh the RFID service to ensure it has the latest student data
            rfid_service.refresh_student_data()
            self.logger.info("Refreshed RFID service student data before simulating scan")

            # Simulate a card read - this will trigger the normal authentication flow
            # through the registered callbacks
            self.logger.info(f"Simulating RFID scan with UID: {rfid_uid}")
            rfid_service.simulate_card_read(rfid_uid)
        except Exception as e:
            self.logger.error(f"Error simulating RFID scan: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

            # If there's an error, stop the scanning animation and show an error
            QTimer.singleShot(1000, lambda: self.handle_rfid_read("TESTCARD123", None))

    def handle_manual_rfid_entry(self):
        """
        Handle manual RFID entry from the input field.
        """
        rfid_uid = self.rfid_input.text().strip()
        if rfid_uid:
            self.logger.info(f"Manual RFID entry: {rfid_uid}")
            self.rfid_input.clear()
            self.start_rfid_scanning()

            # Get the RFID service and simulate a card read with the entered UID
            try:
                from ..services import get_rfid_service
                rfid_service = get_rfid_service()

                # Refresh the RFID service to ensure it has the latest student data
                rfid_service.refresh_student_data()
                self.logger.info("Refreshed RFID service student data before manual RFID entry")

                # Use the entered RFID UID - this will trigger the normal authentication flow
                # through the registered callbacks
                self.logger.info(f"Simulating RFID scan with manually entered UID: {rfid_uid}")
                rfid_service.simulate_card_read(rfid_uid)
            except Exception as e:
                self.logger.error(f"Error processing manual RFID entry: {str(e)}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")

                # If there's an error, directly handle the RFID read
                self.logger.info(f"Directly handling RFID read due to error: {rfid_uid}")
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