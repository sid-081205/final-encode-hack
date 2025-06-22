import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DATABASE_URL = "sqlite:///./fire_data.db"
EXISTING_DB_PATH = "../testing/fire_data.db"  # Path to your existing database

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_database():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database and create tables"""
    from app.models.fire import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

def copy_existing_data():
    """Copy data from existing fire_data.db if it exists"""
    if os.path.exists(EXISTING_DB_PATH):
        try:
            # Connect to existing database
            existing_conn = sqlite3.connect(EXISTING_DB_PATH)
            existing_cursor = existing_conn.cursor()
            
            # Connect to new database
            new_conn = sqlite3.connect("./fire_data.db")
            new_cursor = new_conn.cursor()
            
            # Get existing data
            existing_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = existing_cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                print(f"Copying data from table: {table_name}")
                
                # Get data from existing table
                existing_cursor.execute(f"SELECT * FROM {table_name}")
                rows = existing_cursor.fetchall()
                
                # Get column info
                existing_cursor.execute(f"PRAGMA table_info({table_name})")
                columns = existing_cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                if rows:
                    placeholders = ','.join(['?' for _ in range(len(column_names))])
                    new_cursor.execute(f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})", rows[0])
            
            new_conn.commit()
            existing_conn.close()
            new_conn.close()
            print("Existing data copied successfully")
            
        except Exception as e:
            print(f"Error copying existing data: {e}")
    else:
        print("No existing database found to copy from")