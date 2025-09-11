#!/usr/bin/env python3
"""
Create PostgreSQL schema for local development
"""

from database import engine, Base
from models import *

print("Creating schema with PostgreSQL...")
Base.metadata.create_all(bind=engine)
print("✅ Schema created successfully!")
