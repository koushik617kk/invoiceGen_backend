from sqlalchemy import create_engine, Column, String, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Define the database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///invoicegen.db")

# Create a base for declarative models
Base = declarative_base()

def run_migration():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if the column already exists to prevent errors on re-run
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns("service_templates")]
        if "template_name" not in columns:
            print("Adding 'template_name' column to 'service_templates' table...")
            # Add the column with a default value
            db.execute(text("ALTER TABLE service_templates ADD COLUMN template_name VARCHAR"))
            
            # Update existing records to use description as template_name
            db.execute(text("UPDATE service_templates SET template_name = description WHERE template_name IS NULL"))
            
            # Also fix any NULL values that might exist
            db.execute(text("UPDATE service_templates SET template_name = description WHERE template_name IS NULL"))
            
            db.commit()
            print("'template_name' column added successfully.")
        else:
            print("'template_name' column already exists. Skipping migration.")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
