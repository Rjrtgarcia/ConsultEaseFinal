from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
import hashlib
import os
from .base import Base

class Admin(Base):
    """
    Admin model.
    Represents an administrator in the system.
    """
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Admin {self.username}>"
    
    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash a password with optional salt.
        """
        if salt is None:
            salt = os.urandom(32).hex()
        
        hash_obj = hashlib.sha256()
        hash_obj.update(salt.encode('utf-8'))
        hash_obj.update(password.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        
        return password_hash, salt
    
    def check_password(self, password):
        """
        Check if a password matches the stored hash.
        """
        hash_obj = hashlib.sha256()
        hash_obj.update(self.salt.encode('utf-8'))
        hash_obj.update(password.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        
        return password_hash == self.password_hash
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        """
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 