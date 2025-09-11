#!/usr/bin/env python3
"""
Migrate data from SQLite to PostgreSQL
Run this on EC2 after copying invoicegen.db
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

# Database connections
SQLITE_DB = "invoicegen.db"  # SQLite database file
POSTGRES_CONFIG = {
    'host': 'localhost',
    'database': 'invoicegen_prod',
    'user': 'postgres',
    'password': 'koushik123'  # Update with your password
}

def get_sqlite_connection():
    """Connect to SQLite database"""
    return sqlite3.connect(SQLITE_DB)

def get_postgres_connection():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(**POSTGRES_CONFIG)

def convert_boolean_values(row, table_name, sqlite_conn):
    """Convert SQLite boolean values (0/1) to PostgreSQL boolean (False/True)"""
    converted_row = list(row)
    
    # Define boolean columns for each table
    boolean_columns = {
        'users': ['onboarding_completed'],
        'service_templates': ['is_active', 'is_default'],
        'master_services': ['is_active'],
        'hsn_codes': ['is_active'],
        'invoices': ['reverse_charge'],
        'invoice_items': ['is_active'],
        'library_items': ['is_active'],
        'business_profiles': ['accepts_cash']
    }
    
    if table_name in boolean_columns:
        cursor_sqlite = sqlite_conn.cursor()
        cursor_sqlite.execute(f"PRAGMA table_info({table_name})")
        column_info = cursor_sqlite.fetchall()
        column_names = [col[1] for col in column_info]
        
        for boolean_col in boolean_columns[table_name]:
            if boolean_col in column_names:
                col_index = column_names.index(boolean_col)
                if col_index < len(converted_row) and converted_row[col_index] is not None:
                    # Convert 0/1 to False/True
                    converted_row[col_index] = bool(converted_row[col_index])
    
    return tuple(converted_row)

def migrate_table(table_name, sqlite_conn, postgres_conn):
    """Migrate data from SQLite table to PostgreSQL"""
    print(f"🔄 Migrating {table_name}...")
    
    # Get data from SQLite
    cursor_sqlite = sqlite_conn.cursor()
    cursor_sqlite.execute(f"SELECT * FROM {table_name}")
    rows = cursor_sqlite.fetchall()
    
    if not rows:
        print(f"  ⚠️  No data in {table_name}")
        return
    
    # Get column names
    cursor_sqlite.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor_sqlite.fetchall()]
    
    # Insert into PostgreSQL
    cursor_postgres = postgres_conn.cursor()
    
    # Create placeholders for SQL
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join(columns)
    
    try:
        # Convert and insert data row by row
        converted_rows = []
        for row in rows:
            converted_row = convert_boolean_values(row, table_name, sqlite_conn)
            converted_rows.append(converted_row)
        
        # Insert data with conflict handling
        if table_name == 'hsn_codes':
            insert_sql = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT (code) DO NOTHING
            """
        elif table_name == 'users':
            insert_sql = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET
                    cognito_sub = EXCLUDED.cognito_sub,
                    email = EXCLUDED.email,
                    full_name = EXCLUDED.full_name,
                    phone = EXCLUDED.phone,
                    profile_picture = EXCLUDED.profile_picture,
                    onboarding_completed = EXCLUDED.onboarding_completed,
                    business_type = EXCLUDED.business_type,
                    onboarding_step = EXCLUDED.onboarding_step,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    last_login = EXCLUDED.last_login
            """
        elif table_name == 'business_profiles':
            insert_sql = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    business_name = EXCLUDED.business_name,
                    gstin = EXCLUDED.gstin,
                    pan = EXCLUDED.pan,
                    address = EXCLUDED.address,
                    state_code = EXCLUDED.state_code,
                    phone = EXCLUDED.phone,
                    email = EXCLUDED.email,
                    turnover_category = EXCLUDED.turnover_category,
                    current_financial_year = EXCLUDED.current_financial_year,
                    next_invoice_seq = EXCLUDED.next_invoice_seq,
                    invoice_prefix = EXCLUDED.invoice_prefix,
                    logo_path = EXCLUDED.logo_path,
                    signature_path = EXCLUDED.signature_path,
                    primary_color = EXCLUDED.primary_color,
                    bank_account_name = EXCLUDED.bank_account_name,
                    bank_name = EXCLUDED.bank_name,
                    bank_branch = EXCLUDED.bank_branch,
                    bank_account_number = EXCLUDED.bank_account_number,
                    bank_ifsc = EXCLUDED.bank_ifsc,
                    upi_id = EXCLUDED.upi_id,
                    default_terms = EXCLUDED.default_terms,
                    accepts_cash = EXCLUDED.accepts_cash,
                    cash_note = EXCLUDED.cash_note
            """
        elif table_name == 'customers':
            insert_sql = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    gstin = EXCLUDED.gstin,
                    address = EXCLUDED.address,
                    state_code = EXCLUDED.state_code
            """
        elif table_name == 'invoices':
            insert_sql = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    buyer_id = EXCLUDED.buyer_id,
                    invoice_number = EXCLUDED.invoice_number,
                    date = EXCLUDED.date,
                    due_date = EXCLUDED.due_date,
                    total = EXCLUDED.total,
                    status = EXCLUDED.status,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at
            """
        else:
            insert_sql = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT (id) DO NOTHING
            """
        
        cursor_postgres.executemany(insert_sql, converted_rows)
        
        postgres_conn.commit()
        print(f"  ✅ {table_name}: {len(rows)} records migrated")
        
    except Exception as e:
        print(f"  ❌ {table_name}: Error - {e}")
        postgres_conn.rollback()
    
    cursor_sqlite.close()
    cursor_postgres.close()

def main():
    """Main migration function"""
    print("🚀 Starting SQLite to PostgreSQL migration...")
    
    # Connect to databases
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()
    
    try:
        # Define table migration order to handle foreign key constraints
        # Tables with no dependencies first, then dependent tables
        migration_order = [
            'users',                    # No dependencies
            'master_services',          # No dependencies  
            'hsn_codes',               # No dependencies
            'business_profiles',       # Depends on users
            'customers',               # Depends on users
            'invoices',                # Depends on users, business_profiles, customers
            'invoice_items',           # Depends on invoices
            'service_templates',       # Depends on users, business_profiles
            'library_items',           # Depends on users
            'payments',                # Depends on invoices
            'invoice_templates'        # Depends on users
        ]
        
        print(f"📊 Migrating {len(migration_order)} tables in correct order...")
        
        # Migrate each table in order
        for table in migration_order:
            migrate_table(table, sqlite_conn, postgres_conn)
        
        print("🎉 Migration completed!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        sqlite_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    main()
