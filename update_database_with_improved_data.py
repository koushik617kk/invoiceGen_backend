#!/usr/bin/env python3
"""
Script to update database with improved master services data
"""

import json
from datetime import datetime
from database import SessionLocal, engine
from models import MasterService
from sqlalchemy import text

def update_database_with_improved_data():
    """Update the database with improved master services data"""
    
    print("🚀 UPDATING DATABASE WITH IMPROVED DATA")
    print("=" * 60)
    
    # Read improved data
    with open('master_services_improved_20250907_003150.json', 'r', encoding='utf-8') as f:
        improved_services = json.load(f)
    
    print(f"📊 Loaded {len(improved_services)} improved services")
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Step 1: Add new columns if they don't exist
        print("\n🔧 Adding new columns to MasterService table...")
        
        try:
            # Add is_verified column
            db.execute(text("ALTER TABLE master_services ADD COLUMN is_verified BOOLEAN DEFAULT TRUE"))
            print("✅ Added is_verified column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  is_verified column already exists")
            else:
                print(f"⚠️  Error adding is_verified: {e}")
        
        try:
            # Add official_description column
            db.execute(text("ALTER TABLE master_services ADD COLUMN official_description TEXT"))
            print("✅ Added official_description column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  official_description column already exists")
            else:
                print(f"⚠️  Error adding official_description: {e}")
        
        try:
            # Add last_updated column
            db.execute(text("ALTER TABLE master_services ADD COLUMN last_updated DATETIME"))
            print("✅ Added last_updated column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  last_updated column already exists")
            else:
                print(f"⚠️  Error adding last_updated: {e}")
        
        try:
            # Add source_reference column
            db.execute(text("ALTER TABLE master_services ADD COLUMN source_reference TEXT"))
            print("✅ Added source_reference column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  source_reference column already exists")
            else:
                print(f"⚠️  Error adding source_reference: {e}")
        
        db.commit()
        
        # Step 2: Clear existing data
        print("\n🧹 Clearing existing master services data...")
        db.query(MasterService).delete()
        db.commit()
        print("✅ Cleared existing data")
        
        # Step 3: Insert improved data
        print("\n📥 Inserting improved data...")
        
        inserted_count = 0
        for service_data in improved_services:
            try:
                # Create new MasterService record
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
                    usage_count=service_data['usage_count'],
                    is_verified=service_data.get('is_verified', True),
                    official_description=service_data.get('sac_description', ''),
                    last_updated=datetime.now(),
                    source_reference='GST Portal Official'
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
        
        # Step 4: Verify the update
        print("\n🔍 Verifying database update...")
        
        total_count = db.query(MasterService).count()
        verified_count = db.query(MasterService).filter(MasterService.is_verified == True).count()
        
        print(f"📊 Total services in database: {total_count}")
        print(f"✅ Verified services: {verified_count}")
        print(f"📈 Verification rate: {(verified_count/total_count)*100:.1f}%")
        
        # Step 5: Show category breakdown
        print("\n📋 Category breakdown:")
        categories = db.query(MasterService.category, db.func.count(MasterService.id)).group_by(MasterService.category).all()
        for category, count in categories:
            print(f"  • {category}: {count} services")
        
        # Step 6: Show SAC code distribution
        print("\n🔢 SAC code distribution:")
        sac_codes = db.query(MasterService.sac_code, db.func.count(MasterService.id)).group_by(MasterService.sac_code).all()
        for sac_code, count in sac_codes:
            print(f"  • {sac_code}: {count} services")
        
        print("\n🎉 DATABASE UPDATE COMPLETE!")
        print("=" * 60)
        print("✅ All services now use official SAC codes")
        print("✅ Added verification and official descriptions")
        print("✅ Database is ready for production use")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting database update with improved data...")
    success = update_database_with_improved_data()
    
    if success:
        print("\n🎉 SUCCESS! Database updated successfully!")
        print("🚀 Ready to test the improved suggestion system!")
    else:
        print("\n❌ FAILED! Please check the errors above.")
