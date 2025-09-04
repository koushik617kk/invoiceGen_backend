#!/usr/bin/env python3
"""
Database Backup Script
Creates backups of both SQLite and PostgreSQL databases
"""

import os
import subprocess
import datetime
from pathlib import Path

def backup_sqlite():
    """Backup SQLite database"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/sqlite_backup_{timestamp}.db"
    
    # Create backups directory
    os.makedirs("backups", exist_ok=True)
    
    # Copy SQLite database
    subprocess.run(["cp", "invoicegen.db", backup_file])
    print(f"✅ SQLite backup created: {backup_file}")
    return backup_file

def backup_postgresql():
    """Backup PostgreSQL database"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/postgresql_backup_{timestamp}.sql"
    
    # Create backups directory
    os.makedirs("backups", exist_ok=True)
    
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found")
        return None
    
    # Extract connection details
    # Format: postgresql://user:pass@host:port/dbname
    parts = db_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_db = parts[1].split('/')
    host_port = host_db[0].split(':')
    
    user = user_pass[0]
    password = user_pass[1]
    host = host_port[0]
    port = host_port[1] if len(host_port) > 1 else '5432'
    dbname = host_db[1]
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    # Run pg_dump
    cmd = [
        'pg_dump',
        '-h', host,
        '-p', port,
        '-U', user,
        '-d', dbname,
        '-f', backup_file
    ]
    
    try:
        subprocess.run(cmd, env=env, check=True)
        print(f"✅ PostgreSQL backup created: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"❌ PostgreSQL backup failed: {e}")
        return None

def main():
    print("🔄 Creating database backups...")
    
    # Backup SQLite
    sqlite_backup = backup_sqlite()
    
    # Backup PostgreSQL (if available)
    postgres_backup = backup_postgresql()
    
    print("\n📊 Backup Summary:")
    if sqlite_backup:
        print(f"   SQLite: {sqlite_backup}")
    if postgres_backup:
        print(f"   PostgreSQL: {postgres_backup}")

if __name__ == "__main__":
    main()
