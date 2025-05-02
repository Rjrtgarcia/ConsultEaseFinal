from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import urllib.parse

# Database connection settings - should be moved to config in production
# For Raspberry Pi OS / Debian, postgres user typically uses peer authentication
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')  # Empty password for peer authentication
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')  # Default PostgreSQL port
DB_NAME = os.environ.get('DB_NAME', 'consultease')

# Create PostgreSQL connection URL
# For peer authentication on Unix systems
if DB_HOST == 'localhost' and DB_USER == 'postgres' and not DB_PASSWORD:
    # Use Unix socket connection for peer authentication
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}@/{DB_NAME}"
    print(f"Connecting to database: {DB_NAME} as {DB_USER} using peer authentication")
else:
    # Use TCP connection with password
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
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