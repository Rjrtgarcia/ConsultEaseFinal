import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add parent directory to path to help with imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('consultease.log')
    ]
)
logger = logging.getLogger(__name__)

# Import models and controllers
from central_system.models import init_db
from central_system.controllers import (
    RFIDController,
    FacultyController,
    ConsultationController,
    AdminController
)

# Import views
from central_system.views import (
    LoginWindow,
    DashboardWindow,
    AdminLoginWindow,
    AdminDashboardWindow
)

# Import the keyboard setup script generator
from central_system.views.login_window import create_keyboard_setup_script

# Import utilities
from central_system.utils import (
    install_keyboard_handler,
    apply_stylesheet
)
# Import icons module separately to avoid early QPixmap creation
from central_system.utils import icons

class ConsultEaseApp:
    """
    Main application class for ConsultEase.
    """

    def __init__(self, fullscreen=False):
        """
        Initialize the ConsultEase application.
        """
        logger.info("Initializing ConsultEase application")

        # Create QApplication instance
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("ConsultEase")

        # Set up icons and modern UI (after QApplication is created)
        icons.initialize()
        logger.info("Initialized icons")

        # Apply modern stylesheet (dark theme by default)
        theme = self._get_theme_preference()
        apply_stylesheet(self.app, theme)
        logger.info(f"Applied {theme} theme stylesheet")

        # Create keyboard setup script for Raspberry Pi
        try:
            script_path = create_keyboard_setup_script()
            logger.info(f"Created keyboard setup script at {script_path}")
        except Exception as e:
            logger.error(f"Failed to create keyboard setup script: {e}")

        # Install keyboard handler for touch input
        try:
            self.keyboard_handler = install_keyboard_handler(self.app)
            logger.info("Installed virtual keyboard handler")
        except Exception as e:
            logger.error(f"Failed to install virtual keyboard handler: {e}")
            self.keyboard_handler = None

        # Initialize database
        init_db()

        # Initialize controllers
        self.rfid_controller = RFIDController()
        self.faculty_controller = FacultyController()
        self.consultation_controller = ConsultationController()
        self.admin_controller = AdminController()

        # Ensure default admin exists
        self.admin_controller.ensure_default_admin()

        # Make Dr. John Smith available for testing
        self._ensure_dr_john_smith_available()

        # Initialize windows
        self.login_window = None
        self.dashboard_window = None
        self.admin_login_window = None
        self.admin_dashboard_window = None

        # Current student
        self.current_student = None

        # Start controllers
        logger.info("Starting RFID controller")
        self.rfid_controller.start()
        self.rfid_controller.register_callback(self.handle_rfid_scan)

        # Verify RFID controller is properly initialized
        try:
            from .services import get_rfid_service
            rfid_service = get_rfid_service()
            logger.info(f"RFID service initialized: {rfid_service}, simulation mode: {rfid_service.simulation_mode}")

            # Log registered callbacks
            logger.info(f"RFID service callbacks: {len(rfid_service.callbacks)}")
            for i, callback in enumerate(rfid_service.callbacks):
                callback_name = getattr(callback, '__name__', str(callback))
                logger.info(f"  Callback {i}: {callback_name}")
        except Exception as e:
            logger.error(f"Error verifying RFID service: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

        logger.info("Starting faculty controller")
        self.faculty_controller.start()

        logger.info("Starting consultation controller")
        self.consultation_controller.start()

        # Connect cleanup method
        self.app.aboutToQuit.connect(self.cleanup)

        # Show login window
        self.show_login_window()

        # Store fullscreen preference for use in window creation
        self.fullscreen = fullscreen

    def _get_theme_preference(self):
        """
        Get the user's theme preference.

        Returns:
            str: Theme name ('light' or 'dark')
        """
        # Default to light theme as per the technical context document
        theme = "light"

        # Check for environment variable
        if "CONSULTEASE_THEME" in os.environ:
            env_theme = os.environ["CONSULTEASE_THEME"].lower()
            if env_theme in ["light", "dark"]:
                theme = env_theme

        # Log the theme being used
        logger.info(f"Using {theme} theme based on preference")

        return theme

    def _ensure_dr_john_smith_available(self):
        """
        Make sure Dr. John Smith is available for testing.
        """
        try:
            from central_system.models import Faculty, get_db

            db = get_db()
            # Find Dr. John Smith by name
            faculty = db.query(Faculty).filter(Faculty.name == "Dr. John Smith").first()

            if faculty:
                logger.info(f"Found Dr. John Smith (ID: {faculty.id}), setting status to available")
                faculty.status = True
                db.commit()
                logger.info("Dr. John Smith is now available for testing")
            else:
                logger.warning("Dr. John Smith not found in the database")
        except Exception as e:
            logger.error(f"Error making Dr. John Smith available: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def run(self):
        """
        Run the application.
        """
        logger.info("Starting ConsultEase application")
        return self.app.exec_()

    def cleanup(self):
        """
        Clean up resources before exiting.
        """
        logger.info("Cleaning up ConsultEase application")

        # Stop controllers
        self.rfid_controller.stop()
        self.faculty_controller.stop()
        self.consultation_controller.stop()

    def show_login_window(self):
        """
        Show the login window.
        """
        if self.login_window is None:
            self.login_window = LoginWindow()
            self.login_window.student_authenticated.connect(self.handle_student_authenticated)
            self.login_window.change_window.connect(self.handle_window_change)

        if self.dashboard_window:
            self.dashboard_window.hide()

        if self.admin_login_window:
            self.admin_login_window.hide()

        if self.admin_dashboard_window:
            self.admin_dashboard_window.hide()

        # Ensure proper display
        self.login_window.show()
        self.login_window.showFullScreen()  # Force fullscreen again to ensure it takes effect

    def show_dashboard_window(self, student=None):
        """
        Show the dashboard window.
        """
        self.current_student = student

        if self.dashboard_window is None:
            self.dashboard_window = DashboardWindow(student)
            self.dashboard_window.change_window.connect(self.handle_window_change)
            self.dashboard_window.consultation_requested.connect(self.handle_consultation_request)
        else:
            # Update student info if needed
            self.dashboard_window.student = student

        # Populate faculty grid
        faculties = self.faculty_controller.get_all_faculty()
        self.dashboard_window.populate_faculty_grid(faculties)

        if self.login_window:
            self.login_window.hide()

        if self.admin_login_window:
            self.admin_login_window.hide()

        # Ensure proper display
        self.dashboard_window.show()
        self.dashboard_window.showFullScreen()  # Force fullscreen to ensure it takes effect

        # Log that we've shown the dashboard
        logger.info(f"Showing dashboard for student: {student.name if student else 'Unknown'}")

    def show_admin_login_window(self):
        """
        Show the admin login window.
        """
        if self.admin_login_window is None:
            self.admin_login_window = AdminLoginWindow()
            self.admin_login_window.admin_authenticated.connect(self.handle_admin_authenticated)
            self.admin_login_window.change_window.connect(self.handle_window_change)

        if self.login_window:
            self.login_window.hide()

        if self.dashboard_window:
            self.dashboard_window.hide()

        if self.admin_dashboard_window:
            self.admin_dashboard_window.hide()

        # Ensure proper display
        self.admin_login_window.show()
        self.admin_login_window.showFullScreen()  # Force fullscreen

    def show_admin_dashboard_window(self, admin=None):
        """
        Show the admin dashboard window.
        """
        if self.admin_dashboard_window is None:
            self.admin_dashboard_window = AdminDashboardWindow(admin)
            self.admin_dashboard_window.change_window.connect(self.handle_window_change)
            self.admin_dashboard_window.faculty_updated.connect(self.handle_faculty_updated)
            self.admin_dashboard_window.student_updated.connect(self.handle_student_updated)

        if self.login_window:
            self.login_window.hide()

        if self.dashboard_window:
            self.dashboard_window.hide()

        if self.admin_login_window:
            self.admin_login_window.hide()

        # Ensure proper display
        self.admin_dashboard_window.show()
        self.admin_dashboard_window.showFullScreen()  # Force fullscreen

    def handle_rfid_scan(self, student, rfid_uid):
        """
        Handle RFID scan event.

        Args:
            student (Student): Verified student or None if not verified
            rfid_uid (str): RFID UID that was scanned
        """
        logger.info(f"Main.handle_rfid_scan called with student: {student}, rfid_uid: {rfid_uid}")

        # If login window is active and visible
        if self.login_window and self.login_window.isVisible():
            logger.info(f"Forwarding RFID scan to login window: {rfid_uid}")
            self.login_window.handle_rfid_read(rfid_uid, student)
        else:
            logger.info(f"Login window not visible, RFID scan not forwarded: {rfid_uid}")

    def handle_student_authenticated(self, student):
        """
        Handle student authentication event.

        Args:
            student (Student): Authenticated student
        """
        logger.info(f"Student authenticated: {student.name if student else 'Unknown'}")

        # Store the current student
        self.current_student = student

        # Show the dashboard window
        self.show_dashboard_window(student)

    def handle_admin_authenticated(self, credentials):
        """
        Handle admin authentication event.

        Args:
            credentials (tuple): Admin credentials (username, password)
        """
        # Unpack credentials from tuple
        username, password = credentials

        # Authenticate admin
        admin = self.admin_controller.authenticate(username, password)

        if admin:
            logger.info(f"Admin authenticated: {username}")
            # Create admin info to pass to dashboard
            admin_info = {
                'id': admin.id,
                'username': admin.username
            }
            self.show_admin_dashboard_window(admin_info)
        else:
            logger.warning(f"Admin authentication failed: {username}")
            if self.admin_login_window:
                self.admin_login_window.show_login_error("Invalid username or password")

    def handle_consultation_request(self, faculty, message, course_code):
        """
        Handle consultation request event.

        Args:
            faculty (dict): Faculty information
            message (str): Consultation message
            course_code (str): Course code
        """
        if not self.current_student:
            logger.error("Cannot request consultation: no student authenticated")
            return

        logger.info(f"Consultation requested with: {faculty['name']}")

        # Create consultation request
        consultation = {
            'student_id': self.current_student.id,
            'faculty_id': faculty['id'],
            'message': message,
            'course_code': course_code,
            'status': 'pending'
        }

        # Add to database
        success = self.consultation_controller.add_consultation(consultation)

        # Show success/error message
        if success:
            self.dashboard_window.show_notification(
                f"Consultation request sent to {faculty['name']}",
                "success"
            )
        else:
            self.dashboard_window.show_notification(
                "Failed to send consultation request. Please try again.",
                "error"
            )

    def handle_faculty_updated(self):
        """
        Handle faculty data updated event.
        """
        # Refresh faculty grid if dashboard is active
        if self.dashboard_window and self.dashboard_window.isVisible():
            faculties = self.faculty_controller.get_all_faculty()
            self.dashboard_window.populate_faculty_grid(faculties)

    def handle_student_updated(self):
        """
        Handle student data updated event.
        """
        logger.info("Student data updated, refreshing RFID service and controller")

        # Refresh RFID service and controller's student data
        try:
            # First, refresh the RFID service directly
            from central_system.services import get_rfid_service
            rfid_service = get_rfid_service()
            rfid_service.refresh_student_data()

            # Then refresh the RFID controller
            students = self.rfid_controller.refresh_student_data()

            # Log all students for debugging
            for student in students:
                logger.info(f"Student: ID={student.id}, Name={student.name}, RFID={student.rfid_uid}")

            # If login window is active, make sure it's ready for scanning
            if self.login_window and self.login_window.isVisible():
                logger.info("Login window is active, ensuring RFID scanning is active")
                self.login_window.start_rfid_scanning()

            logger.info("Student data refresh complete")
        except Exception as e:
            logger.error(f"Error refreshing student data: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def handle_window_change(self, window_name, data=None):
        """
        Handle window change event.

        Args:
            window_name (str): Name of window to show
            data (any): Optional data to pass to the window
        """
        if window_name == "login":
            self.show_login_window()
        elif window_name == "dashboard":
            self.show_dashboard_window(data)
        elif window_name == "admin_login":
            self.show_admin_login_window()
        elif window_name == "admin_dashboard":
            self.show_admin_dashboard_window(data)
        else:
            logger.warning(f"Unknown window: {window_name}")

if __name__ == "__main__":
    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("consultease.log")
        ]
    )

    # Enable debug logging for RFID service
    rfid_logger = logging.getLogger('central_system.services.rfid_service')
    rfid_logger.setLevel(logging.DEBUG)

    # Set environment variables if needed
    import os

    # Configure RFID - enable simulation mode since we're on Raspberry Pi
    os.environ['RFID_SIMULATION_MODE'] = 'true'  # Enable if no RFID reader available

    # Set the theme to light as per the technical context document
    os.environ['CONSULTEASE_THEME'] = 'light'

    # Use PostgreSQL for production
    os.environ['DB_TYPE'] = 'postgresql'
    os.environ['DB_USER'] = 'piuser'  # Update with your PostgreSQL username
    os.environ['DB_PASSWORD'] = 'password'  # Update with your PostgreSQL password
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_NAME'] = 'consultease'

    # Check if we're running in fullscreen mode
    fullscreen = os.environ.get('CONSULTEASE_FULLSCREEN', 'false').lower() == 'true'

    # Start the application
    app = ConsultEaseApp(fullscreen=fullscreen)
    sys.exit(app.run())