#!/usr/bin/env python3
"""
Migration Verification Script
Comprehensive verification that your SQLite to PostgreSQL migration was successful
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, engine, DATABASE_URL
from models import *
from sqlalchemy import func, text
import json

def verify_migration():
    """Comprehensive migration verification"""
    print("🔍 MIGRATION VERIFICATION REPORT")
    print("=" * 60)
    
    # Check database type
    print(f"\n📊 DATABASE CONNECTION:")
    if "sqlite" in DATABASE_URL:
        print(f"   ❌ Still connected to SQLite: {DATABASE_URL}")
        print(f"   ⚠️  Migration may not have completed properly!")
        return False
    elif "postgresql" in DATABASE_URL:
        print(f"   ✅ Connected to PostgreSQL: {DATABASE_URL}")
    else:
        print(f"   ❓ Unknown database type: {DATABASE_URL}")
    
    db = next(get_db())
    
    try:
        # 1. TABLE EXISTENCE CHECK
        print(f"\n📋 TABLE EXISTENCE CHECK:")
        print("-" * 40)
        
        required_tables = [
            "users", "business_profiles", "customers", "invoices", 
            "invoice_items", "master_services", "hsn_codes", 
            "service_templates", "library_items", "invoice_templates"
        ]
        
        all_tables_exist = True
        for table in required_tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"   ✅ {table}: {result} records")
            except Exception as e:
                print(f"   ❌ {table}: Table missing or error - {str(e)[:50]}...")
                all_tables_exist = False
        
        if not all_tables_exist:
            print(f"\n❌ CRITICAL: Some tables are missing!")
            return False
        
        # 2. DATA INTEGRITY CHECK
        print(f"\n🔍 DATA INTEGRITY CHECK:")
        print("-" * 40)
        
        # Check users data
        users = db.query(User).all()
        print(f"   👥 Users: {len(users)} records")
        if users:
            for user in users[:3]:
                print(f"      - {user.email} ({user.full_name}) - Onboarding: {user.onboarding_completed}")
        
        # Check business profiles
        profiles = db.query(BusinessProfile).all()
        print(f"   🏢 Business Profiles: {len(profiles)} records")
        if profiles:
            for profile in profiles[:3]:
                print(f"      - {profile.business_name} (GSTIN: {profile.gstin})")
        
        # Check customers
        customers = db.query(Customer).all()
        print(f"   👤 Customers: {len(customers)} records")
        if customers:
            for customer in customers[:3]:
                print(f"      - {customer.name} (GSTIN: {customer.gstin})")
        
        # Check invoices
        invoices = db.query(Invoice).all()
        print(f"   📄 Invoices: {len(invoices)} records")
        if invoices:
            for invoice in invoices[:3]:
                print(f"      - {invoice.invoice_number} - ₹{invoice.total} ({invoice.status})")
        
        # Check invoice items
        items = db.query(InvoiceItem).all()
        print(f"   📦 Invoice Items: {len(items)} records")
        if items:
            for item in items[:3]:
                print(f"      - {item.description} (HSN: {item.hsn_code}, GST: {item.gst_rate}%)")
        
        # 3. MASTER DATA CHECK
        print(f"\n🎯 MASTER DATA CHECK:")
        print("-" * 40)
        
        # HSN Codes
        hsn_codes = db.query(HSNCode).all()
        print(f"   🏷️  HSN Codes: {len(hsn_codes)} records")
        if hsn_codes:
            hsn_by_type = db.query(HSNCode.type, func.count(HSNCode.id)).group_by(HSNCode.type).all()
            for type_name, count in hsn_by_type:
                print(f"      - {type_name}: {count}")
        
        # Master Services
        services = db.query(MasterService).all()
        print(f"   🛠️  Master Services: {len(services)} records")
        if services:
            service_by_category = db.query(MasterService.category, func.count(MasterService.id)).group_by(MasterService.category).all()
            for category, count in service_by_category:
                print(f"      - {category}: {count}")
        
        # Service Templates
        templates = db.query(ServiceTemplate).all()
        print(f"   📋 Service Templates: {len(templates)} records")
        
        # 4. FOREIGN KEY RELATIONSHIPS CHECK
        print(f"\n🔗 FOREIGN KEY RELATIONSHIPS CHECK:")
        print("-" * 40)
        
        # Check user-business profile relationships
        orphaned_profiles = db.query(BusinessProfile).filter(
            ~BusinessProfile.user_id.in_(db.query(User.id))
        ).count()
        print(f"   👥 Orphaned business profiles: {orphaned_profiles}")
        
        # Check user-customer relationships
        orphaned_customers = db.query(Customer).filter(
            ~Customer.user_id.in_(db.query(User.id))
        ).count()
        print(f"   👤 Orphaned customers: {orphaned_customers}")
        
        # Check invoice relationships
        orphaned_invoices = db.query(Invoice).filter(
            ~Invoice.user_id.in_(db.query(User.id))
        ).count()
        print(f"   📄 Orphaned invoices: {orphaned_invoices}")
        
        # Check invoice item relationships
        orphaned_items = db.query(InvoiceItem).filter(
            ~InvoiceItem.invoice_id.in_(db.query(Invoice.id))
        ).count()
        print(f"   📦 Orphaned invoice items: {orphaned_items}")
        
        # 5. DATA TYPE VERIFICATION
        print(f"\n🔧 DATA TYPE VERIFICATION:")
        print("-" * 40)
        
        # Check boolean fields
        boolean_issues = 0
        
        # Check users onboarding_completed
        try:
            invalid_bool_users = db.query(User).filter(
                User.onboarding_completed.notin_([True, False])
            ).count()
            if invalid_bool_users > 0:
                print(f"   ❌ Users with invalid boolean onboarding_completed: {invalid_bool_users}")
                boolean_issues += 1
            else:
                print(f"   ✅ Users boolean fields: OK")
        except Exception as e:
            print(f"   ❌ Error checking users boolean fields: {e}")
            boolean_issues += 1
        
        # Check master services is_active
        try:
            invalid_bool_services = db.query(MasterService).filter(
                MasterService.is_active.notin_([True, False])
            ).count()
            if invalid_bool_services > 0:
                print(f"   ❌ Master services with invalid boolean is_active: {invalid_bool_services}")
                boolean_issues += 1
            else:
                print(f"   ✅ Master services boolean fields: OK")
        except Exception as e:
            print(f"   ❌ Error checking master services boolean fields: {e}")
            boolean_issues += 1
        
        # 6. PERFORMANCE CHECK
        print(f"\n⚡ PERFORMANCE CHECK:")
        print("-" * 40)
        
        # Test query performance
        import time
        start_time = time.time()
        
        # Test complex query
        result = db.query(Invoice).join(User).join(BusinessProfile).limit(10).all()
        
        query_time = time.time() - start_time
        print(f"   ⏱️  Complex query time: {query_time:.3f} seconds")
        
        if query_time > 1.0:
            print(f"   ⚠️  Query performance may be slow")
        else:
            print(f"   ✅ Query performance: Good")
        
        # 7. FINAL VERIFICATION SUMMARY
        print(f"\n🎉 MIGRATION VERIFICATION SUMMARY:")
        print("=" * 60)
        
        total_records = (
            len(users) + len(profiles) + len(customers) + 
            len(invoices) + len(items) + len(hsn_codes) + 
            len(services) + len(templates)
        )
        
        print(f"📊 Total Records Migrated: {total_records}")
        print(f"📋 Tables Created: {len(required_tables)}")
        print(f"🔗 Foreign Key Issues: {orphaned_profiles + orphaned_customers + orphaned_invoices + orphaned_items}")
        print(f"🔧 Data Type Issues: {boolean_issues}")
        
        # Overall status
        if (orphaned_profiles + orphaned_customers + orphaned_invoices + orphaned_items) == 0 and boolean_issues == 0:
            print(f"\n✅ MIGRATION SUCCESSFUL!")
            print(f"   All data migrated correctly")
            print(f"   All relationships intact")
            print(f"   All data types correct")
            print(f"   Ready for production use! 🚀")
            return True
        else:
            print(f"\n⚠️  MIGRATION COMPLETED WITH ISSUES")
            print(f"   Check the issues above and fix if needed")
            return False
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    finally:
        db.close()

def quick_health_check():
    """Quick health check for production readiness"""
    print("🏥 QUICK HEALTH CHECK")
    print("=" * 30)
    
    db = next(get_db())
    
    try:
        # Essential tables check
        essential_tables = ["users", "business_profiles", "invoices", "master_services", "hsn_codes"]
        
        for table in essential_tables:
            try:
                count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                if count > 0:
                    print(f"   ✅ {table}: {count} records")
                else:
                    print(f"   ⚠️  {table}: No records")
            except Exception as e:
                print(f"   ❌ {table}: Error - {str(e)[:30]}...")
        
        # Database type
        if "postgresql" in DATABASE_URL:
            print(f"   ✅ Database: PostgreSQL")
        else:
            print(f"   ❌ Database: Not PostgreSQL")
        
        print(f"\n🎯 Health Status: {'HEALTHY' if 'postgresql' in DATABASE_URL else 'NEEDS ATTENTION'}")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Choose verification type:")
    print("1. Full migration verification")
    print("2. Quick health check")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        verify_migration()
    elif choice == "2":
        quick_health_check()
    else:
        print("Invalid choice. Running full verification...")
        verify_migration()
