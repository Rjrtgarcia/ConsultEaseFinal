from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import urllib.parse

# Database connection settings - should be moved to config in production
# Temporarily using postgres user to bypass permissions issues
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')  # Change this if your postgres user has a different password
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')  # Default PostgreSQL port
DB_NAME = os.environ.get('DB_NAME', 'consultease')

# Ensure password is properly encoded for URL
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

# Create SQLAlchemy engine with explicit port
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"Connecting to database: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Get database session.
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables.
    """
    Base.metadata.create_all(bind=engine) 