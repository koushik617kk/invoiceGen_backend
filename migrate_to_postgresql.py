#!/usr/bin/env python3
"""
Database Migration Script: SQLite to PostgreSQL
Usage: python migrate_to_postgresql.py [options]

This script migrates all data from SQLite to PostgreSQL with proper data type conversion.
"""

import sqlite3
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv('.env.production')

def get_sqlite_connection():
    """Connect to SQLite database"""
    return sqlite3.connect('invoicegen.db')

def get_postgresql_connection():
    """Connect to PostgreSQL database"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise Exception("DATABASE_URL not found in environment")
    return create_engine(db_url)

def migrate_table_data(table_name, sqlite_conn, postgres_engine):
    """Migrate data from SQLite to PostgreSQL for a specific table"""
    print(f"📊 Migrating {table_name}...")
    
    try:
        # Read data from SQLite
        df = pd.read_sql_query(f'SELECT * FROM {table_name}', sqlite_conn)
        
        if df.empty:
            print(f"   ⚠️  No data in {table_name}")
            return
        
        # Handle data type conversions
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        if 'updated_at' in df.columns:
            df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if 'due_date' in df.columns:
            df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
        if 'paid_on' in df.columns:
            df['paid_on'] = pd.to_datetime(df['paid_on'], errors='coerce')
        if 'last_login' in df.columns:
            df['last_login'] = pd.to_datetime(df['last_login'], errors='coerce')
        
        # Handle boolean columns
        boolean_columns = ['onboarding_completed', 'reverse_charge', 'is_active', 'is_default']
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].astype('boolean')
        
        # Handle numeric columns
        numeric_columns = ['gst_rate', 'cgst', 'sgst', 'igst', 'total', 'subtotal', 'discount', 
                          'taxable_value', 'round_off', 'cgst_rate', 'cgst_amount', 'sgst_rate', 
                          'sgst_amount', 'igst_rate', 'igst_amount', 'total_amount', 'discount_percent', 
                          'discount_amount', 'base_rate', 'min_quantity', 'max_quantity', 'usage_count']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Write to PostgreSQL
        df.to_sql(table_name, postgres_engine, if_exists='append', index=False, method='multi')
        print(f"   ✅ Migrated {len(df)} records to {table_name}")
        
    except Exception as e:
        print(f"   ❌ Error migrating {table_name}: {e}")

def verify_migration(sqlite_conn, postgres_engine):
    """Verify that migration was successful"""
    print("\n🔍 Verifying migration...")
    
    tables = [
        'users', 'business_profiles', 'customers', 'invoices', 
        'invoice_items', 'master_services', 'hsn_codes',
        'service_templates', 'library_items', 'invoice_templates'
    ]
    
    for table in tables:
        try:
            # Count SQLite records
            sqlite_count = pd.read_sql_query(f'SELECT COUNT(*) as count FROM {table}', sqlite_conn)['count'][0]
            
            # Count PostgreSQL records
            postgres_count = pd.read_sql_query(f'SELECT COUNT(*) as count FROM {table}', postgres_engine)['count'][0]
            
            if sqlite_count == postgres_count:
                print(f"   ✅ {table}: {postgres_count} records (matches SQLite)")
            else:
                print(f"   ⚠️  {table}: SQLite={sqlite_count}, PostgreSQL={postgres_count}")
                
        except Exception as e:
            print(f"   ❌ Error verifying {table}: {e}")

def main():
    print("🚀 Starting Database Migration: SQLite → PostgreSQL")
    print("=" * 60)
    
    # Connect to databases
    try:
        sqlite_conn = get_sqlite_connection()
        postgres_engine = get_postgresql_connection()
        print("✅ Connected to both databases")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return
    
    # Tables to migrate (in order to respect foreign keys)
    tables = [
        'users',
        'business_profiles', 
        'customers',
        'invoices',
        'invoice_items',
        'master_services',
        'hsn_codes',
        'service_templates',
        'library_items',
        'invoice_templates'
    ]
    
    # Migrate each table
    for table in tables:
        try:
            migrate_table_data(table, sqlite_conn, postgres_engine)
        except Exception as e:
            print(f"❌ Failed to migrate {table}: {e}")
            continue
    
    # Verify migration
    verify_migration(sqlite_conn, postgres_engine)
    
    # Close connections
    sqlite_conn.close()
    postgres_engine.dispose()
    
    print("\n🎉 Migration completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
