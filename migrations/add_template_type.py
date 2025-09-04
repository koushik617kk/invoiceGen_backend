#!/usr/bin/env python3
"""
Database migration to add template_type field to service_templates table
This migration is safe and backward compatible.
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add template_type column to service_templates table"""
    
    # Database path
    db_path = "invoicegen.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Skipping migration.")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(service_templates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'template_type' in columns:
            print("Column 'template_type' already exists. Skipping migration.")
            return
        
        # Add the new column with default value
        print("Adding template_type column to service_templates table...")
        cursor.execute("""
            ALTER TABLE service_templates 
            ADD COLUMN template_type VARCHAR DEFAULT 'service'
        """)
        
        # Update existing records to have 'service' as default
        cursor.execute("""
            UPDATE service_templates 
            SET template_type = 'service' 
            WHERE template_type IS NULL
        """)
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM service_templates")
        count = cursor.fetchone()[0]
        print(f"Total service templates: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM service_templates WHERE template_type = 'service'")
        service_count = cursor.fetchone()[0]
        print(f"Service templates: {service_count}")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
