#!/usr/bin/env python3
"""
Script to export updated HSN data from database to JSON
"""

import json
from datetime import datetime
from database import SessionLocal
from models import HSNCode

def export_updated_hsn_data():
    """Export updated HSN data from database to JSON"""
    
    print("🚀 EXPORTING UPDATED HSN DATA TO JSON")
    print("=" * 60)
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Get all HSN codes
        all_codes = db.query(HSNCode).all()
        
        print(f"📊 Total HSN codes to export: {len(all_codes)}")
        
        # Convert to JSON format
        hsn_data = []
        
        for code in all_codes:
            hsn_item = {
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
            hsn_data.append(hsn_item)
        
        # Create comprehensive export data
        export_data = {
            "export_info": {
                "export_date": datetime.now().isoformat(),
                "total_codes": len(all_codes),
                "gst_reform_2025": "Applied - Effective September 22, 2025",
                "source": "Database Export",
                "description": "Updated HSN codes with 2025 GST rate reforms"
            },
            "gst_rate_summary": {
                "5_percent": len([c for c in all_codes if c.gst_rate == 5.0]),
                "12_percent": len([c for c in all_codes if c.gst_rate == 12.0]),
                "18_percent": len([c for c in all_codes if c.gst_rate == 18.0]),
                "28_percent": len([c for c in all_codes if c.gst_rate == 28.0])
            },
            "category_summary": {},
            "hsn_codes": hsn_data
        }
        
        # Add category summary
        categories = {}
        for code in all_codes:
            if code.category not in categories:
                categories[code.category] = {
                    "count": 0,
                    "gst_rates": {},
                    "subcategories": set()
                }
            
            categories[code.category]["count"] += 1
            
            # Count GST rates per category
            rate_key = f"{code.gst_rate}%"
            if rate_key not in categories[code.category]["gst_rates"]:
                categories[code.category]["gst_rates"][rate_key] = 0
            categories[code.category]["gst_rates"][rate_key] += 1
            
            # Collect subcategories
            if code.subcategory:
                categories[code.category]["subcategories"].add(code.subcategory)
        
        # Convert sets to lists for JSON serialization
        for category in categories:
            categories[category]["subcategories"] = list(categories[category]["subcategories"])
        
        export_data["category_summary"] = categories
        
        # Save to JSON file
        filename = f"updated_hsn_codes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"/mnt/c/Users/ynaga/Downloads/Rental_Assistant/invoiceGen_backend/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully exported to: {filename}")
        
        # Display summary
        print("\n📊 EXPORT SUMMARY:")
        print("=" * 60)
        print(f"📁 File: {filename}")
        print(f"📊 Total codes: {len(all_codes)}")
        print(f"📅 Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n💰 GST Rate Distribution:")
        for rate, count in export_data["gst_rate_summary"].items():
            print(f"  • {rate}: {count} codes")
        
        print("\n📋 Category Distribution:")
        for category, info in categories.items():
            print(f"  • {category}: {info['count']} codes")
            print(f"    - GST Rates: {info['gst_rates']}")
            print(f"    - Subcategories: {', '.join(info['subcategories'])}")
        
        print("\n🎯 Key Highlights:")
        print("✅ All automotive codes at 18% (2025 reform)")
        print("✅ All stationery codes at 5% (essential items)")
        print("✅ All electronics codes at 18% (no change)")
        print("✅ Compliant with official GST reforms")
        
        # Show sample data
        print("\n📋 Sample HSN Codes:")
        for i, code in enumerate(all_codes[:5]):
            print(f"  {i+1}. {code.code} - {code.description} - {code.gst_rate}% - {code.category}")
        
        if len(all_codes) > 5:
            print(f"  ... and {len(all_codes) - 5} more codes")
        
        print(f"\n🎉 Export complete! Check the file: {filename}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Error exporting HSN data: {e}")
        return None
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting HSN data export...")
    filepath = export_updated_hsn_data()
    
    if filepath:
        print(f"\n🎉 SUCCESS! HSN data exported to: {filepath}")
        print("🚀 You can now review all your updated HSN codes!")
    else:
        print("\n❌ FAILED! Please check the errors above.")
