#!/usr/bin/env python3
"""
Master Data Management Script
Usage: python manage_master_data.py [command] [options]

Commands:
  populate    - Populate master data from hsn_service.py
  clear       - Clear all master data
  update      - Update master data (clear + populate)
  export      - Export master data to JSON
  import      - Import master data from JSON
  status      - Show current master data status
"""

import sys
import json
from pathlib import Path
from database import get_db, engine, Base
from models import MasterService, HSNCode
from hsn_service import HSN_CODES
from sqlalchemy import func
import argparse

def clear_master_data():
    """Clear all master data"""
    db = next(get_db())
    try:
        print("🗑️  Clearing master data...")
        
        # Clear in order to respect foreign keys
        db.query(MasterService).delete()
        db.query(HSNCode).delete()
        
        db.commit()
        print("✅ Master data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing master data: {e}")
        db.rollback()
    finally:
        db.close()

def populate_hsn_codes():
    """Populate HSN codes from hsn_service.py"""
    db = next(get_db())
    try:
        print("📊 Populating HSN codes...")
        
        hsn_objects = []
        for item in HSN_CODES:
            hsn_obj = HSNCode(
                code=item["code"],
                description=item["desc"],
                gst_rate=item["gst"],
                type=item["type"],
                category=item.get("category", "General"),
                subcategory=item.get("subcategory"),
                keywords=item.get("keywords", ""),
                tags=item.get("tags", ""),
                unit=item.get("unit", "Nos")
            )
            hsn_objects.append(hsn_obj)
        
        db.add_all(hsn_objects)
        db.commit()
        print(f"✅ Added {len(hsn_objects)} HSN codes!")
        
    except Exception as e:
        print(f"❌ Error populating HSN codes: {e}")
        db.rollback()
    finally:
        db.close()

def populate_master_services():
    """Populate master services"""
    db = next(get_db())
    try:
        print("🛠️  Populating master services...")
        
        # Sample master services - you can expand this
        master_services = [
            {
                "name": "Website Development",
                "description": "Custom website development and design",
                "sac_code": "998314",
                "gst_rate": 18.0,
                "hsn_code": None,
                "category": "IT Services",
                "subcategory": "Web Development",
                "business_type": "service",
                "keywords": "website, web, development, design, coding",
                "tags": "IT, Technology, Digital",
                "unit": "Project"
            },
            {
                "name": "Mobile App Development",
                "description": "iOS and Android mobile application development",
                "sac_code": "998314",
                "gst_rate": 18.0,
                "hsn_code": None,
                "category": "IT Services",
                "subcategory": "Mobile Development",
                "business_type": "service",
                "keywords": "mobile, app, ios, android, development",
                "tags": "IT, Technology, Mobile",
                "unit": "Project"
            },
            {
                "name": "Digital Marketing",
                "description": "Social media marketing and SEO services",
                "sac_code": "998314",
                "gst_rate": 18.0,
                "hsn_code": None,
                "category": "Marketing Services",
                "subcategory": "Digital Marketing",
                "business_type": "service",
                "keywords": "marketing, digital, seo, social media, advertising",
                "tags": "Marketing, Digital, Advertising",
                "unit": "Month"
            },
            {
                "name": "Consulting Services",
                "description": "Business and technical consulting",
                "sac_code": "998314",
                "gst_rate": 18.0,
                "hsn_code": None,
                "category": "Professional Services",
                "subcategory": "Consulting",
                "business_type": "service",
                "keywords": "consulting, advice, business, strategy",
                "tags": "Professional, Business, Strategy",
                "unit": "Hour"
            },
            {
                "name": "Graphic Design",
                "description": "Logo design, branding, and graphic design services",
                "sac_code": "998314",
                "gst_rate": 18.0,
                "hsn_code": None,
                "category": "Creative Services",
                "subcategory": "Graphic Design",
                "business_type": "service",
                "keywords": "design, graphic, logo, branding, creative",
                "tags": "Creative, Design, Branding",
                "unit": "Project"
            }
        ]
        
        service_objects = []
        for item in master_services:
            service_obj = MasterService(
                name=item["name"],
                description=item["description"],
                sac_code=item["sac_code"],
                gst_rate=item["gst_rate"],
                hsn_code=item["hsn_code"],
                category=item["category"],
                subcategory=item["subcategory"],
                business_type=item["business_type"],
                keywords=item["keywords"],
                tags=item["tags"],
                unit=item["unit"]
            )
            service_objects.append(service_obj)
        
        db.add_all(service_objects)
        db.commit()
        print(f"✅ Added {len(service_objects)} master services!")
        
    except Exception as e:
        print(f"❌ Error populating master services: {e}")
        db.rollback()
    finally:
        db.close()

def populate_master_data():
    """Populate all master data"""
    print("🚀 Starting master data population...")
    populate_hsn_codes()
    populate_master_services()
    print("✅ Master data population completed!")

def show_status():
    """Show current master data status"""
    db = next(get_db())
    try:
        hsn_count = db.query(func.count(HSNCode.id)).scalar()
        service_count = db.query(func.count(MasterService.id)).scalar()
        
        print(f"📊 Master Data Status:")
        print(f"   HSN Codes: {hsn_count}")
        print(f"   Master Services: {service_count}")
        
        if hsn_count > 0:
            print(f"\n📋 Sample HSN Codes:")
            sample_hsn = db.query(HSNCode.code, HSNCode.description, HSNCode.gst_rate).limit(3).all()
            for code, desc, gst in sample_hsn:
                print(f"   {code} - {desc} - {gst}%")
        
        if service_count > 0:
            print(f"\n🛠️  Sample Master Services:")
            sample_services = db.query(MasterService.name, MasterService.sac_code, MasterService.gst_rate).limit(3).all()
            for name, sac, gst in sample_services:
                print(f"   {name} - SAC: {sac} - {gst}%")
                
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    finally:
        db.close()

def export_master_data():
    """Export master data to JSON files"""
    db = next(get_db())
    try:
        print("📤 Exporting master data...")
        
        # Export HSN codes
        hsn_codes = db.query(HSNCode).all()
        hsn_data = []
        for hsn in hsn_codes:
            hsn_data.append({
                "code": hsn.code,
                "description": hsn.description,
                "gst_rate": hsn.gst_rate,
                "type": hsn.type,
                "category": hsn.category,
                "subcategory": hsn.subcategory,
                "keywords": hsn.keywords,
                "tags": hsn.tags,
                "unit": hsn.unit
            })
        
        with open("hsn_codes_export.json", "w") as f:
            json.dump(hsn_data, f, indent=2)
        
        # Export master services
        services = db.query(MasterService).all()
        service_data = []
        for service in services:
            service_data.append({
                "name": service.name,
                "description": service.description,
                "sac_code": service.sac_code,
                "gst_rate": service.gst_rate,
                "hsn_code": service.hsn_code,
                "category": service.category,
                "subcategory": service.subcategory,
                "business_type": service.business_type,
                "keywords": service.keywords,
                "tags": service.tags,
                "unit": service.unit
            })
        
        with open("master_services_export.json", "w") as f:
            json.dump(service_data, f, indent=2)
        
        print(f"✅ Exported {len(hsn_data)} HSN codes and {len(service_data)} services!")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Master Data Management")
    parser.add_argument("command", choices=["populate", "clear", "update", "export", "status"])
    
    args = parser.parse_args()
    
    if args.command == "populate":
        populate_master_data()
    elif args.command == "clear":
        clear_master_data()
    elif args.command == "update":
        clear_master_data()
        populate_master_data()
    elif args.command == "export":
        export_master_data()
    elif args.command == "status":
        show_status()

if __name__ == "__main__":
    main()
