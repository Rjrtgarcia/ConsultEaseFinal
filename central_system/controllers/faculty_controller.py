import logging
import datetime
from sqlalchemy import or_
from ..services import get_mqtt_service
from ..models import Faculty, get_db

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FacultyController:
    """
    Controller for managing faculty data and status.
    """
    
    def __init__(self):
        """
        Initialize the faculty controller.
        """
        self.mqtt_service = get_mqtt_service()
        self.callbacks = []
    
    def start(self):
        """
        Start the faculty controller and subscribe to faculty status updates.
        """
        logger.info("Starting Faculty controller")
        
        # Subscribe to faculty status updates
        self.mqtt_service.register_topic_handler(
            "consultease/faculty/+/status", 
            self.handle_faculty_status_update
        )
        
        # Connect MQTT service
        if not self.mqtt_service.is_connected:
            self.mqtt_service.connect()
    
    def stop(self):
        """
        Stop the faculty controller.
        """
        logger.info("Stopping Faculty controller")
    
    def register_callback(self, callback):
        """
        Register a callback to be called when faculty status changes.
        
        Args:
            callback (callable): Function that takes a Faculty object as argument
        """
        self.callbacks.append(callback)
        logger.info(f"Registered Faculty controller callback: {callback.__name__}")
    
    def _notify_callbacks(self, faculty):
        """
        Notify all registered callbacks with the updated faculty information.
        
        Args:
            faculty (Faculty): Updated faculty object
        """
        for callback in self.callbacks:
            try:
                callback(faculty)
            except Exception as e:
                logger.error(f"Error in Faculty controller callback: {str(e)}")
    
    def handle_faculty_status_update(self, topic, data):
        """
        Handle faculty status update from MQTT.
        
        Args:
            topic (str): MQTT topic
            data (dict): Status update data
        """
        # Extract faculty ID from topic (e.g., "consultease/faculty/123/status")
        parts = topic.split('/')
        if len(parts) != 4:
            logger.error(f"Invalid topic format: {topic}")
            return
        
        faculty_id = int(parts[2])
        
        # Get status from data
        status = data.get('status', False)
        
        logger.info(f"Received status update for faculty {faculty_id}: {status}")
        
        # Update faculty status in database
        faculty = self.update_faculty_status(faculty_id, status)
        
        if faculty:
            # Notify callbacks
            self._notify_callbacks(faculty)
    
    def update_faculty_status(self, faculty_id, status):
        """
        Update faculty status in the database.
        
        Args:
            faculty_id (int): Faculty ID
            status (bool): New status (True = Available, False = Unavailable)
            
        Returns:
            Faculty: Updated faculty object or None if not found
        """
        try:
            db = get_db()
            faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
            
            if not faculty:
                logger.error(f"Faculty not found: {faculty_id}")
                return None
            
            faculty.status = status
            faculty.last_seen = datetime.datetime.now()
            
            db.commit()
            
            logger.info(f"Updated status for faculty {faculty.name} (ID: {faculty.id}): {status}")
            
            return faculty
        except Exception as e:
            logger.error(f"Error updating faculty status: {str(e)}")
            return None
    
    def get_all_faculty(self, filter_available=None, search_term=None):
        """
        Get all faculty, optionally filtered by availability or search term.
        
        Args:
            filter_available (bool, optional): Filter by availability status
            search_term (str, optional): Search term for name or department
            
        Returns:
            list: List of Faculty objects
        """
        try:
            db = get_db()
            query = db.query(Faculty)
            
            # Apply filters
            if filter_available is not None:
                query = query.filter(Faculty.status == filter_available)
            
            if search_term:
                search_term = f"%{search_term}%"
                query = query.filter(
                    or_(
                        Faculty.name.ilike(search_term),
                        Faculty.department.ilike(search_term)
                    )
                )
            
            # Execute query
            faculties = query.all()
            
            return faculties
        except Exception as e:
            logger.error(f"Error getting faculty list: {str(e)}")
            return []
    
    def get_faculty_by_id(self, faculty_id):
        """
        Get a faculty member by ID.
        
        Args:
            faculty_id (int): Faculty ID
            
        Returns:
            Faculty: Faculty object or None if not found
        """
        try:
            db = get_db()
            faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
            return faculty
        except Exception as e:
            logger.error(f"Error getting faculty by ID: {str(e)}")
            return None
    
    def add_faculty(self, name, department, email, ble_id):
        """
        Add a new faculty member.
        
        Args:
            name (str): Faculty name
            department (str): Faculty department
            email (str): Faculty email
            ble_id (str): Faculty BLE beacon ID
            
        Returns:
            Faculty: New faculty object or None if error
        """
        try:
            db = get_db()
            
            # Check if email or BLE ID already exists
            existing = db.query(Faculty).filter(
                or_(
                    Faculty.email == email,
                    Faculty.ble_id == ble_id
                )
            ).first()
            
            if existing:
                logger.error(f"Faculty with email {email} or BLE ID {ble_id} already exists")
                return None
            
            # Create new faculty
            faculty = Faculty(
                name=name,
                department=department,
                email=email,
                ble_id=ble_id,
                status=False
            )
            
            db.add(faculty)
            db.commit()
            
            logger.info(f"Added new faculty: {faculty.name} (ID: {faculty.id})")
            
            return faculty
        except Exception as e:
            logger.error(f"Error adding faculty: {str(e)}")
            return None
    
    def update_faculty(self, faculty_id, name=None, department=None, email=None, ble_id=None):
        """
        Update an existing faculty member.
        
        Args:
            faculty_id (int): Faculty ID
            name (str, optional): New faculty name
            department (str, optional): New faculty department
            email (str, optional): New faculty email
            ble_id (str, optional): New faculty BLE beacon ID
            
        Returns:
            Faculty: Updated faculty object or None if error
        """
        try:
            db = get_db()
            faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
            
            if not faculty:
                logger.error(f"Faculty not found: {faculty_id}")
                return None
            
            # Update fields if provided
            if name is not None:
                faculty.name = name
            
            if department is not None:
                faculty.department = department
            
            if email is not None and email != faculty.email:
                # Check if email already exists
                existing = db.query(Faculty).filter(Faculty.email == email).first()
                if existing and existing.id != faculty_id:
                    logger.error(f"Faculty with email {email} already exists")
                    return None
                faculty.email = email
            
            if ble_id is not None and ble_id != faculty.ble_id:
                # Check if BLE ID already exists
                existing = db.query(Faculty).filter(Faculty.ble_id == ble_id).first()
                if existing and existing.id != faculty_id:
                    logger.error(f"Faculty with BLE ID {ble_id} already exists")
                    return None
                faculty.ble_id = ble_id
            
            db.commit()
            
            logger.info(f"Updated faculty: {faculty.name} (ID: {faculty.id})")
            
            return faculty
        except Exception as e:
            logger.error(f"Error updating faculty: {str(e)}")
            return None
    
    def delete_faculty(self, faculty_id):
        """
        Delete a faculty member.
        
        Args:
            faculty_id (int): Faculty ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            db = get_db()
            faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
            
            if not faculty:
                logger.error(f"Faculty not found: {faculty_id}")
                return False
            
            db.delete(faculty)
            db.commit()
            
            logger.info(f"Deleted faculty: {faculty.name} (ID: {faculty.id})")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting faculty: {str(e)}")
            return False 