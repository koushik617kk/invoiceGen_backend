#!/usr/bin/env python3
"""
FIX HSN MODEL - Remove the UNIQUE constraint on HSN code field
The problem: HSN codes have unique=True constraint, but multiple products can share same HSN code
Solution: Remove unique constraint and allow multiple products per HSN code
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, engine

def fix_hsn_unique_constraint():
    """Remove the unique constraint on HSN code field"""
    
    print("🔧 FIXING HSN MODEL - REMOVING UNIQUE CONSTRAINT")
    print("=" * 60)
    print("❌ PROBLEM: HSN codes table has unique=True constraint")
    print("✅ SOLUTION: Remove unique constraint - multiple products can share HSN codes")
    print()
    
    db = SessionLocal()
    
    try:
        # Check current constraint
        print("📊 Checking current database structure...")
        
        # Get table info
        result = db.execute(text("PRAGMA table_info(hsn_codes)")).fetchall()
        print("Current hsn_codes table structure:")
        for row in result:
            print(f"   {row}")
        
        print("\n🔄 Recreating table without unique constraint...")
        
        # Since SQLite doesn't support dropping constraints easily,
        # we'll recreate the table
        
        # Step 1: Create backup of data
        backup_data = db.execute(text("""
            SELECT * FROM hsn_codes
        """)).fetchall()
        
        print(f"📦 Backed up {len(backup_data)} records")
        
        # Step 2: Drop the old table
        db.execute(text("DROP TABLE IF EXISTS hsn_codes"))
        db.commit()
        print("🗑️  Dropped old table")
        
        # Step 3: Create new table without unique constraint
        db.execute(text("""
            CREATE TABLE hsn_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR NOT NULL,
                description VARCHAR NOT NULL,
                gst_rate FLOAT NOT NULL,
                type VARCHAR NOT NULL,
                category VARCHAR,
                subcategory VARCHAR,
                keywords TEXT,
                tags TEXT,
                unit VARCHAR DEFAULT 'Nos',
                business_type VARCHAR,
                is_active BOOLEAN DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                source VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create index on code (but not unique)
        db.execute(text("CREATE INDEX ix_hsn_codes_code ON hsn_codes (code)"))
        db.execute(text("CREATE INDEX ix_hsn_codes_id ON hsn_codes (id)"))
        
        db.commit()
        print("✅ Created new table without unique constraint")
        
        # Step 4: Restore data (if any)
        if backup_data:
            print(f"🔄 Restoring {len(backup_data)} records...")
            for row in backup_data:
                # Insert with proper column mapping
                db.execute(text("""
                    INSERT INTO hsn_codes 
                    (code, description, gst_rate, type, category, subcategory, 
                     keywords, tags, unit, business_type, is_active, usage_count, 
                     source, created_at, updated_at)
                    VALUES 
                    (:code, :description, :gst_rate, :type, :category, :subcategory,
                     :keywords, :tags, :unit, :business_type, :is_active, :usage_count,
                     :source, :created_at, :updated_at)
                """), {
                    'code': row[1],  # code
                    'description': row[2],  # description  
                    'gst_rate': row[3],  # gst_rate
                    'type': row[4],  # type
                    'category': row[5],  # category
                    'subcategory': row[6],  # subcategory
                    'keywords': row[7],  # keywords
                    'tags': row[8],  # tags
                    'unit': row[9],  # unit
                    'business_type': row[10],  # business_type
                    'is_active': row[11],  # is_active
                    'usage_count': row[12],  # usage_count
                    'source': row[13],  # source
                    'created_at': row[14],  # created_at
                    'updated_at': row[15]   # updated_at
                })
            db.commit()
            print("✅ Data restored successfully")
        
        # Verify the fix
        final_count = db.execute(text("SELECT COUNT(*) FROM hsn_codes")).fetchone()[0]
        print(f"\n🎉 HSN MODEL FIXED SUCCESSFULLY!")
        print(f"📊 Total records: {final_count}")
        print("✅ Multiple products can now share the same HSN code")
        
        # Show table structure
        print("\n💡 NEW TABLE STRUCTURE:")
        result = db.execute(text("PRAGMA table_info(hsn_codes)")).fetchall()
        for row in result:
            if 'code' in str(row):
                print(f"   ✅ {row} (No unique constraint!)")
        
    except Exception as e:
        print(f"❌ Error fixing HSN model: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_hsn_unique_constraint()
