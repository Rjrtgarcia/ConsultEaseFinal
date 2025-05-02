import logging
from ..services import get_rfid_service
from ..models import Student, get_db

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RFIDController:
    """
    Controller for handling RFID card scanning and student verification.
    """
    
    def __init__(self):
        """
        Initialize the RFID controller.
        """
        self.rfid_service = get_rfid_service()
        self.callbacks = []
    
    def start(self):
        """
        Start the RFID service and register callback.
        """
        logger.info("Starting RFID controller")
        self.rfid_service.register_callback(self.handle_rfid_scan)
        self.rfid_service.start()
    
    def stop(self):
        """
        Stop the RFID service.
        """
        logger.info("Stopping RFID controller")
        self.rfid_service.stop()
    
    def register_callback(self, callback):
        """
        Register a callback to be called when a student is verified.
        
        Args:
            callback (callable): Function that takes a Student object as argument
        """
        self.callbacks.append(callback)
        logger.info(f"Registered RFID controller callback: {callback.__name__}")
    
    def _notify_callbacks(self, student=None, rfid_uid=None):
        """
        Notify all registered callbacks with the student information.
        
        Args:
            student (Student, optional): Verified student or None if not verified
            rfid_uid (str, optional): RFID UID that was scanned
        """
        for callback in self.callbacks:
            try:
                callback(student, rfid_uid)
            except Exception as e:
                logger.error(f"Error in RFID controller callback: {str(e)}")
    
    def handle_rfid_scan(self, rfid_uid):
        """
        Handle RFID scan event by verifying the student.
        
        Args:
            rfid_uid (str): RFID UID that was scanned
        """
        logger.info(f"RFID scan received: {rfid_uid}")
        
        # Verify student in database
        student = self.verify_student(rfid_uid)
        
        if student:
            logger.info(f"Student verified: {student.name} (ID: {student.id})")
        else:
            logger.warning(f"Unrecognized RFID: {rfid_uid}")
        
        # Notify callbacks with student (or None if not verified)
        self._notify_callbacks(student, rfid_uid)
    
    def verify_student(self, rfid_uid):
        """
        Verify a student by RFID UID.
        
        Args:
            rfid_uid (str): RFID UID to verify
            
        Returns:
            Student: Student object if verified, None otherwise
        """
        try:
            db = get_db()
            student = db.query(Student).filter(Student.rfid_uid == rfid_uid).first()
            return student
        except Exception as e:
            logger.error(f"Error verifying student: {str(e)}")
            return None
    
    def simulate_scan(self, rfid_uid=None):
        """
        Simulate an RFID scan for development purposes.
        
        Args:
            rfid_uid (str, optional): RFID UID to simulate. If None, a random UID is generated.
        
        Returns:
            str: The simulated RFID UID
        """
        return self.rfid_service.simulate_card_read(rfid_uid) 