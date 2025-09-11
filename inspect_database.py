#!/usr/bin/env python3
"""
Database Inspection Script
Shows detailed information about what's currently in your database
"""

from database import get_db, engine
from models import *
from sqlalchemy import func, text
import json

def inspect_database():
    """Comprehensive database inspection"""
    db = next(get_db())
    
    try:
        print("🔍 DATABASE INSPECTION REPORT")
        print("=" * 50)
        
        # Check if tables exist
        print("\n📊 TABLE STATUS:")
        tables = [
            "users", "business_profiles", "customers", "invoices", 
            "invoice_items", "master_services", "hsn_codes", 
            "service_templates", "library_items", "invoice_templates"
        ]
        
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"   ✅ {table}: {result} records")
            except Exception as e:
                print(f"   ❌ {table}: Table doesn't exist or error - {str(e)[:50]}...")
        
        # Detailed inspection of each table
        print("\n" + "=" * 50)
        print("📋 DETAILED TABLE INSPECTION")
        print("=" * 50)
        
        # Users
        print("\n👥 USERS TABLE:")
        try:
            users = db.query(User).all()
            print(f"   Total Users: {len(users)}")
            if users:
                for user in users[:3]:  # Show first 3 users
                    print(f"   - ID: {user.id}, Email: {user.email}, Name: {user.full_name}")
                    print(f"     Onboarding: {user.onboarding_completed}, Business Type: {user.business_type}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Business Profiles
        print("\n🏢 BUSINESS PROFILES TABLE:")
        try:
            profiles = db.query(BusinessProfile).all()
            print(f"   Total Profiles: {len(profiles)}")
            if profiles:
                for profile in profiles[:3]:
                    print(f"   - ID: {profile.id}, Business: {profile.business_name}")
                    print(f"     GSTIN: {profile.gstin}, PAN: {profile.pan}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Customers
        print("\n👤 CUSTOMERS TABLE:")
        try:
            customers = db.query(Customer).all()
            print(f"   Total Customers: {len(customers)}")
            if customers:
                for customer in customers[:3]:
                    print(f"   - ID: {customer.id}, Name: {customer.name}, GSTIN: {customer.gstin}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Invoices
        print("\n📄 INVOICES TABLE:")
        try:
            invoices = db.query(Invoice).all()
            print(f"   Total Invoices: {len(invoices)}")
            if invoices:
                for invoice in invoices[:3]:
                    print(f"   - ID: {invoice.id}, Number: {invoice.invoice_number}")
                    print(f"     Amount: ₹{invoice.total_amount}, Status: {invoice.status}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Invoice Items
        print("\n📦 INVOICE ITEMS TABLE:")
        try:
            items = db.query(InvoiceItem).all()
            print(f"   Total Invoice Items: {len(items)}")
            if items:
                for item in items[:3]:
                    print(f"   - ID: {item.id}, Description: {item.description}")
                    print(f"     HSN: {item.hsn_code}, SAC: {item.sac_code}, GST: {item.gst_rate}%")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Master Services
        print("\n🛠️ MASTER SERVICES TABLE:")
        try:
            services = db.query(MasterService).all()
            print(f"   Total Master Services: {len(services)}")
            if services:
                for service in services[:5]:  # Show first 5
                    print(f"   - ID: {service.id}, Name: {service.name}")
                    print(f"     SAC: {service.sac_code}, GST: {service.gst_rate}%, Category: {service.category}")
            else:
                print("   ⚠️  No master services found!")
        except Exception as e:
            print(f"   Error: {e}")
        
        # HSN Codes
        print("\n🏷️ HSN CODES TABLE:")
        try:
            hsn_codes = db.query(HSNCode).all()
            print(f"   Total HSN Codes: {len(hsn_codes)}")
            if hsn_codes:
                for hsn in hsn_codes[:5]:  # Show first 5
                    print(f"   - ID: {hsn.id}, Code: {hsn.code}, Type: {hsn.type}")
                    print(f"     Description: {hsn.description[:50]}...")
                    print(f"     GST: {hsn.gst_rate}%, Category: {hsn.category}")
            else:
                print("   ⚠️  No HSN codes found!")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Service Templates
        print("\n📋 SERVICE TEMPLATES TABLE:")
        try:
            templates = db.query(ServiceTemplate).all()
            print(f"   Total Service Templates: {len(templates)}")
            if templates:
                for template in templates[:3]:
                    print(f"   - ID: {template.id}, Name: {template.description}")
                    print(f"     SAC: {template.sac_code}, GST: {template.gst_rate}%")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Library Items
        print("\n📚 LIBRARY ITEMS TABLE:")
        try:
            library_items = db.query(LibraryItem).all()
            print(f"   Total Library Items: {len(library_items)}")
            if library_items:
                for item in library_items[:3]:
                    print(f"   - ID: {item.id}, Description: {item.description}")
                    print(f"     HSN: {item.hsn_code}, SAC: {item.sac_code}, GST: {item.gst_rate}%")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Database Schema Info
        print("\n" + "=" * 50)
        print("🏗️ DATABASE SCHEMA INFO")
        print("=" * 50)
        
        # Check database type
        db_url = str(engine.url)
        if "sqlite" in db_url:
            print("   Database Type: SQLite")
            print(f"   Database File: {db_url.split('///')[-1]}")
        elif "postgresql" in db_url:
            print("   Database Type: PostgreSQL")
            print(f"   Database URL: {db_url}")
        else:
            print(f"   Database Type: Unknown - {db_url}")
        
        # Check table columns for key tables
        print("\n📊 TABLE COLUMNS INFO:")
        key_tables = ["users", "business_profiles", "invoices", "master_services", "hsn_codes"]
        
        for table in key_tables:
            try:
                result = db.execute(text(f"PRAGMA table_info({table})")).fetchall()
                if result:
                    print(f"\n   {table.upper()} columns:")
                    for col in result:
                        print(f"     - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
                else:
                    print(f"   {table}: No column info available (might be PostgreSQL)")
            except Exception as e:
                print(f"   {table}: Error getting columns - {str(e)[:50]}...")
        
        print("\n" + "=" * 50)
        print("✅ DATABASE INSPECTION COMPLETED")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during inspection: {e}")
    finally:
        db.close()

def check_master_data_status():
    """Check specifically master data status"""
    db = next(get_db())
    
    try:
        print("\n🎯 MASTER DATA STATUS CHECK")
        print("=" * 30)
        
        # HSN Codes
        hsn_count = db.query(func.count(HSNCode.id)).scalar()
        print(f"HSN Codes: {hsn_count}")
        
        if hsn_count > 0:
            hsn_by_type = db.query(HSNCode.type, func.count(HSNCode.id)).group_by(HSNCode.type).all()
            for type_name, count in hsn_by_type:
                print(f"  - {type_name}: {count}")
            
            hsn_by_gst = db.query(HSNCode.gst_rate, func.count(HSNCode.id)).group_by(HSNCode.gst_rate).all()
            print("  GST Rate Distribution:")
            for gst_rate, count in hsn_by_gst:
                print(f"    - {gst_rate}%: {count}")
        
        # Master Services
        service_count = db.query(func.count(MasterService.id)).scalar()
        print(f"\nMaster Services: {service_count}")
        
        if service_count > 0:
            service_by_category = db.query(MasterService.category, func.count(MasterService.id)).group_by(MasterService.category).all()
            for category, count in service_by_category:
                print(f"  - {category}: {count}")
        
        # Check if data exists in hsn_service.py
        from hsn_service import HSN_CODES
        print(f"\nHSN codes in code: {len(HSN_CODES)}")
        
        if hsn_count == 0 and len(HSN_CODES) > 0:
            print("⚠️  WARNING: You have HSN codes in code but none in database!")
            print("   Run: python manage_master_data.py populate")
        
    except Exception as e:
        print(f"❌ Error checking master data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Choose inspection type:")
    print("1. Full database inspection")
    print("2. Master data status only")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        inspect_database()
    elif choice == "2":
        check_master_data_status()
    else:
        print("Invalid choice. Running full inspection...")
        inspect_database()
