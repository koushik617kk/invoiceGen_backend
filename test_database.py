#!/usr/bin/env python3
"""
Test which database the application is using
"""

from database import engine, DATABASE_URL, ENVIRONMENT
from sqlalchemy import text
import os

def test_database_connection():
    print("🔍 DATABASE CONNECTION TEST")
    print("=" * 50)
    
    # Check environment variables
    print(f"ENVIRONMENT: {ENVIRONMENT}")
    print(f"DATABASE_URL: {DATABASE_URL}")
    print()
    
    # Test database connection
    try:
        with engine.connect() as conn:
            # Check database type
            if "sqlite" in DATABASE_URL:
                print("❌ Using SQLite database")
                result = conn.execute(text("SELECT sqlite_version()")).scalar()
                print(f"SQLite version: {result}")
            elif "postgresql" in DATABASE_URL:
                print("✅ Using PostgreSQL database")
                result = conn.execute(text("SELECT version()")).scalar()
                print(f"PostgreSQL version: {result}")
            else:
                print("❓ Unknown database type")
            
            # Check if tables exist
            print("\n📊 CHECKING TABLES:")
            if "sqlite" in DATABASE_URL:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
                tables = [row[0] for row in result]
            else:
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).fetchall()
                tables = [row[0] for row in result]
            
            print(f"Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
            
            # Check data in key tables
            print("\n📋 CHECKING DATA:")
            key_tables = ['users', 'business_profiles', 'invoices', 'master_services', 'hsn_codes']
            
            for table in key_tables:
                if table in tables:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                        print(f"  {table}: {result} records")
                    except Exception as e:
                        print(f"  {table}: Error - {e}")
                else:
                    print(f"  {table}: Table not found")
                    
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_database_connection()
