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
    
    def __init__(self):
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
        
        # Install keyboard handler for touch input
        self.keyboard_handler = install_keyboard_handler(self.app)
        logger.info("Installed virtual keyboard handler")
        
        # Initialize database
        init_db()
        
        # Initialize controllers
        self.rfid_controller = RFIDController()
        self.faculty_controller = FacultyController()
        self.consultation_controller = ConsultationController()
        self.admin_controller = AdminController()
        
        # Ensure default admin exists
        self.admin_controller.ensure_default_admin()
        
        # Initialize windows
        self.login_window = None
        self.dashboard_window = None
        self.admin_login_window = None
        self.admin_dashboard_window = None
        
        # Current student
        self.current_student = None
        
        # Start controllers
        self.rfid_controller.start()
        self.rfid_controller.register_callback(self.handle_rfid_scan)
        
        self.faculty_controller.start()
        self.consultation_controller.start()
        
        # Show login window
        self.show_login_window()
    
    def _get_theme_preference(self):
        """
        Get the user's theme preference.
        
        Returns:
            str: Theme name ('light' or 'dark')
        """
        # Default to dark theme
        theme = "dark"
        
        # Check for environment variable
        if "CONSULTEASE_THEME" in os.environ:
            env_theme = os.environ["CONSULTEASE_THEME"].lower()
            if env_theme in ["light", "dark"]:
                theme = env_theme
        
        # TODO: Add settings file check for theme preference
        
        return theme
    
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
        
        self.login_window.show()
    
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
        
        self.dashboard_window.show()
    
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
        
        self.admin_login_window.show()
    
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
        
        self.admin_dashboard_window.show()
    
    def handle_rfid_scan(self, student, rfid_uid):
        """
        Handle RFID scan event.
        
        Args:
            student (Student): Verified student or None if not verified
            rfid_uid (str): RFID UID that was scanned
        """
        # If login window is active and visible
        if self.login_window and self.login_window.isVisible():
            self.login_window.handle_rfid_read(rfid_uid, student)
    
    def handle_student_authenticated(self, student):
        """
        Handle student authentication event.
        
        Args:
            student (Student): Authenticated student
        """
        logger.info(f"Student authenticated: {student.name}")
        self.show_dashboard_window(student)
    
    def handle_admin_authenticated(self, credentials):
        """
        Handle admin authentication event.
        
        Args:
            credentials (dict): Admin credentials (id, username)
        """
        logger.info(f"Admin authenticated: {credentials['username']}")
        self.show_admin_dashboard_window(credentials)
    
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
        # TODO: Update student data in dashboard if needed
        pass
    
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
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and run application
    app = ConsultEaseApp()
    
    try:
        exit_code = app.run()
    except Exception as e:
        logger.exception("Unhandled exception in main application")
        exit_code = 1
    finally:
        app.cleanup()
    
    sys.exit(exit_code) 