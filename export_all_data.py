#!/usr/bin/env python3
"""
Script to export both MasterService and HSNCode table data to JSON files
"""

import json
from datetime import datetime
from database import SessionLocal
from models import MasterService, HSNCode

def export_all_data_to_json():
    """Export both MasterService and HSNCode data to JSON files"""
    db = SessionLocal()
    
    try:
        # Get all master services
        services = db.query(MasterService).all()
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
        
        # Get all HSN codes
        codes = db.query(HSNCode).all()
        codes_data = []
        for code in codes:
            code_dict = {
                "id": code.id,
                "code": code.code,
                "description": code.description,
                "gst_rate": code.gst_rate,
                "type": code.type,
                "category": code.category,
                "subcategory": code.subcategory,
                "keywords": code.keywords,
                "tags": code.tags,
                "unit": code.unit,
                "business_type": code.business_type,
                "is_active": code.is_active,
                "usage_count": code.usage_count,
                "source": code.source,
                "created_at": code.created_at.isoformat() if code.created_at else None,
                "updated_at": code.updated_at.isoformat() if code.updated_at else None
            }
            codes_data.append(code_dict)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export MasterService data
        services_filename = f"master_services_export_{timestamp}.json"
        with open(services_filename, 'w', encoding='utf-8') as f:
            json.dump(services_data, f, indent=2, ensure_ascii=False)
        
        # Export HSNCode data
        codes_filename = f"hsn_codes_export_{timestamp}.json"
        with open(codes_filename, 'w', encoding='utf-8') as f:
            json.dump(codes_data, f, indent=2, ensure_ascii=False)
        
        # Create combined export
        combined_data = {
            "export_info": {
                "timestamp": timestamp,
                "exported_at": datetime.now().isoformat(),
                "total_services": len(services_data),
                "total_codes": len(codes_data)
            },
            "master_services": services_data,
            "hsn_codes": codes_data
        }
        
        combined_filename = f"all_data_export_{timestamp}.json"
        with open(combined_filename, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully exported data to JSON files:")
        print(f"   - Master Services: {services_filename} ({len(services_data)} records)")
        print(f"   - HSN/SAC Codes: {codes_filename} ({len(codes_data)} records)")
        print(f"   - Combined Data: {combined_filename}")
        
        # Summary
        print(f"\n📊 Export Summary:")
        print(f"   - Master Services: {len(services_data)}")
        print(f"     * Active: {len([s for s in services_data if s['is_active']])}")
        print(f"     * Inactive: {len([s for s in services_data if not s['is_active']])}")
        
        print(f"   - HSN/SAC Codes: {len(codes_data)}")
        print(f"     * HSN: {len([c for c in codes_data if c['type'] == 'HSN'])}")
        print(f"     * SAC: {len([c for c in codes_data if c['type'] == 'SAC'])}")
        print(f"     * Active: {len([c for c in codes_data if c['is_active']])}")
        
        return {
            "services_file": services_filename,
            "codes_file": codes_filename,
            "combined_file": combined_filename
        }
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Exporting all database data to JSON...")
    result = export_all_data_to_json()
    if result:
        print(f"🎉 Export completed!")
        print(f"📁 Files created:")
        for key, filename in result.items():
            print(f"   - {key}: {filename}")
    else:
        print("❌ Export failed!")
