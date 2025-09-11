#!/usr/bin/env python3
"""
Script to export MasterService table data to JSON file
"""

import json
from datetime import datetime
from database import SessionLocal
from models import MasterService

def export_master_services_to_json():
    """Export all MasterService data to JSON file"""
    db = SessionLocal()
    
    try:
        # Get all master services
        services = db.query(MasterService).all()
        
        # Convert to dictionary format
        services_data = []
        for service in services:
            service_dict = {
                "id": service.id,
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
                "unit": service.unit,
                "is_active": service.is_active,
                "usage_count": service.usage_count,
                "created_at": service.created_at.isoformat() if service.created_at else None,
                "updated_at": service.updated_at.isoformat() if service.updated_at else None
            }
            services_data.append(service_dict)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"master_services_export_{timestamp}.json"
        
        # Write to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(services_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully exported {len(services_data)} master services to {filename}")
        
        # Also create a summary
        print(f"\n📊 Export Summary:")
        print(f"   - Total services: {len(services_data)}")
        print(f"   - Active services: {len([s for s in services_data if s['is_active']])}")
        print(f"   - Inactive services: {len([s for s in services_data if not s['is_active']])}")
        
        # Show categories
        categories = list(set([s['category'] for s in services_data if s['category']]))
        print(f"   - Categories: {', '.join(categories)}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Exporting MasterService data to JSON...")
    filename = export_master_services_to_json()
    if filename:
        print(f"🎉 Export completed! File saved as: {filename}")
    else:
        print("❌ Export failed!")
