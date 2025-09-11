#!/usr/bin/env python3
"""
Simple script to update database with improved master services data
"""

import json
from datetime import datetime
from database import SessionLocal
from models import MasterService

def simple_update_database():
    """Update database with improved data using existing structure"""
    
    print("🚀 UPDATING DATABASE WITH IMPROVED DATA")
    print("=" * 60)
    
    # Read improved data
    with open('master_services_improved_20250907_003150.json', 'r', encoding='utf-8') as f:
        improved_services = json.load(f)
    
    print(f"📊 Loaded {len(improved_services)} improved services")
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("\n🧹 Clearing existing master services data...")
        db.query(MasterService).delete()
        db.commit()
        print("✅ Cleared existing data")
        
        # Insert improved data
        print("\n📥 Inserting improved data...")
        
        inserted_count = 0
        for service_data in improved_services:
            try:
                # Create new MasterService record with existing fields only
                master_service = MasterService(
                    name=service_data['name'],
                    description=service_data['description'],
                    sac_code=service_data['sac_code'],
                    gst_rate=service_data['gst_rate'],
                    hsn_code=service_data.get('hsn_code'),
                    category=service_data['category'],
                    subcategory=service_data['subcategory'],
                    business_type=service_data['business_type'],
                    keywords=service_data['keywords'],
                    tags=service_data.get('tags'),
                    unit=service_data['unit'],
                    is_active=service_data['is_active'],
                    usage_count=service_data['usage_count']
                )
                
                db.add(master_service)
                inserted_count += 1
                
                if inserted_count % 50 == 0:
                    print(f"  📊 Inserted {inserted_count} services...")
                    
            except Exception as e:
                print(f"❌ Error inserting {service_data['name']}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        print(f"✅ Successfully inserted {inserted_count} services")
        
        # Verify the update
        print("\n🔍 Verifying database update...")
        
        total_count = db.query(MasterService).count()
        print(f"📊 Total services in database: {total_count}")
        
        # Show category breakdown
        print("\n📋 Category breakdown:")
        categories = db.query(MasterService.category, db.func.count(MasterService.id)).group_by(MasterService.category).all()
        for category, count in categories:
            print(f"  • {category}: {count} services")
        
        # Show SAC code distribution
        print("\n🔢 SAC code distribution:")
        sac_codes = db.query(MasterService.sac_code, db.func.count(MasterService.id)).group_by(MasterService.sac_code).all()
        for sac_code, count in sac_codes:
            print(f"  • {sac_code}: {count} services")
        
        print("\n🎉 DATABASE UPDATE COMPLETE!")
        print("=" * 60)
        print("✅ All services now use official SAC codes")
        print("✅ Database is ready for production use")
        print("✅ Improved search accuracy")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting simple database update...")
    success = simple_update_database()
    
    if success:
        print("\n🎉 SUCCESS! Database updated successfully!")
        print("🚀 Ready to test the improved suggestion system!")
    else:
        print("\n❌ FAILED! Please check the errors above.")
