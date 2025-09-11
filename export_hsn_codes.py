#!/usr/bin/env python3
"""
Script to export HSNCode table data to JSON file
"""

import json
from datetime import datetime
from database import SessionLocal
from models import HSNCode

def export_hsn_codes_to_json():
    """Export all HSNCode data to JSON file"""
    db = SessionLocal()
    
    try:
        # Get all HSN codes
        codes = db.query(HSNCode).all()
        
        # Convert to dictionary format
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
        filename = f"hsn_codes_export_{timestamp}.json"
        
        # Write to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(codes_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully exported {len(codes_data)} HSN/SAC codes to {filename}")
        
        # Also create a summary
        print(f"\n📊 Export Summary:")
        print(f"   - Total codes: {len(codes_data)}")
        print(f"   - HSN codes: {len([c for c in codes_data if c['type'] == 'HSN'])}")
        print(f"   - SAC codes: {len([c for c in codes_data if c['type'] == 'SAC'])}")
        print(f"   - Active codes: {len([c for c in codes_data if c['is_active']])}")
        
        # Show categories
        categories = list(set([c['category'] for c in codes_data if c['category']]))
        print(f"   - Categories: {', '.join(categories)}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Exporting HSNCode data to JSON...")
    filename = export_hsn_codes_to_json()
    if filename:
        print(f"🎉 Export completed! File saved as: {filename}")
    else:
        print("❌ Export failed!")
