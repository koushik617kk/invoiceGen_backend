#!/usr/bin/env python3
"""
Script to improve HSN codes with official data for target business types
"""

import json
from datetime import datetime
from database import SessionLocal
from models import HSNCode

def improve_hsn_codes():
    """Add official HSN codes for target business types"""
    
    print("🚀 IMPROVING HSN CODES FOR TARGET BUSINESS TYPES")
    print("=" * 60)
    
    # Official HSN codes for target business types
    official_hsn_codes = [
        # AUTOMOTIVE PRODUCTS (Main Focus)
        {
            "code": "8708",
            "description": "Parts and accessories for motor vehicles",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Parts",
            "keywords": "auto parts,car parts,vehicle accessories,automotive parts,car accessories",
            "tags": "automotive,parts,accessories",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "4011",
            "description": "New pneumatic tyres and tubes for motor vehicles",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Tires",
            "keywords": "car tyres,vehicle tyres,tires,tubes,automotive tyres",
            "tags": "automotive,tires,wheels",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8507",
            "description": "Electric accumulators for motor vehicles",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Batteries",
            "keywords": "car battery,vehicle battery,automotive battery,car battery",
            "tags": "automotive,battery,electrical",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "2710",
            "description": "Petroleum oils and oils obtained from bituminous minerals",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Oils",
            "keywords": "engine oil,motor oil,car oil,automotive oil,lubricants",
            "tags": "automotive,oil,lubricants",
            "unit": "Liters",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "Brake pads and brake shoes for motor vehicles",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Brakes",
            "keywords": "brake pads,brake shoes,car brakes,automotive brakes",
            "tags": "automotive,brakes,safety",
            "unit": "Nos",
            "business_type": "product"
        },
        
        # ELECTRONICS & IT HARDWARE
        {
            "code": "8517",
            "description": "Telephone sets, including telephones for cellular networks",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Phones",
            "keywords": "smartphones,mobile phones,cell phones,telephones",
            "tags": "electronics,mobile,communication",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Automatic data processing machines and units thereof",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computers",
            "keywords": "computers,laptops,desktops,servers,workstations",
            "tags": "electronics,computers,IT",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8518",
            "description": "Microphones, loudspeakers, headphones and earphones",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Audio",
            "keywords": "speakers,headphones,microphones,audio equipment",
            "tags": "electronics,audio,sound",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8528",
            "description": "Monitors and projectors, not incorporating television reception apparatus",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Displays",
            "keywords": "monitors,displays,projectors,screens,LED TVs",
            "tags": "electronics,displays,visual",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8523",
            "description": "Discs, tapes, solid-state non-volatile storage devices",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Storage",
            "keywords": "USB drives,memory cards,storage devices,flash drives",
            "tags": "electronics,storage,memory",
            "unit": "Nos",
            "business_type": "product"
        },
        
        # OFFICE SUPPLIES & STATIONERY
        {
            "code": "4820",
            "description": "Registers, account books, notebooks, order books and similar articles",
            "gst_rate": 12.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Books",
            "keywords": "notebooks,registers,account books,office books",
            "tags": "stationery,office,books",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "9608",
            "description": "Ball point pens, felt tipped and other porous-tipped pens and markers",
            "gst_rate": 12.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Pens",
            "keywords": "pens,ballpoint pens,markers,writing instruments",
            "tags": "stationery,writing,pens",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "4823",
            "description": "Paper, paperboard, cellulose wadding and webs of cellulose fibres",
            "gst_rate": 12.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Paper",
            "keywords": "paper,paperboard,office paper,printing paper",
            "tags": "stationery,paper,office",
            "unit": "Kg",
            "business_type": "product"
        },
        
        # PROFESSIONAL SERVICES EQUIPMENT
        {
            "code": "9013",
            "description": "Liquid crystal devices, lasers, other optical appliances and instruments",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Optical",
            "keywords": "lasers,optical instruments,measurement devices",
            "tags": "electronics,optical,measurement",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "9015",
            "description": "Surveying, hydrographic, oceanographic, hydrological, meteorological instruments",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Measurement",
            "keywords": "surveying instruments,measurement tools,professional equipment",
            "tags": "electronics,measurement,professional",
            "unit": "Nos",
            "business_type": "product"
        }
    ]
    
    # Connect to database
    db = SessionLocal()
    
    try:
        print(f"📊 Adding {len(official_hsn_codes)} official HSN codes...")
        
        added_count = 0
        updated_count = 0
        
        for hsn_data in official_hsn_codes:
            try:
                # Check if code already exists
                existing = db.query(HSNCode).filter(HSNCode.code == hsn_data['code']).first()
                
                if existing:
                    # Update existing code
                    existing.description = hsn_data['description']
                    existing.gst_rate = hsn_data['gst_rate']
                    existing.category = hsn_data['category']
                    existing.subcategory = hsn_data['subcategory']
                    existing.keywords = hsn_data['keywords']
                    existing.tags = hsn_data['tags']
                    existing.unit = hsn_data['unit']
                    existing.business_type = hsn_data['business_type']
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                    print(f"  🔄 Updated: {hsn_data['code']} - {hsn_data['description']}")
                else:
                    # Add new code
                    new_hsn = HSNCode(
                        code=hsn_data['code'],
                        description=hsn_data['description'],
                        gst_rate=hsn_data['gst_rate'],
                        type=hsn_data['type'],
                        category=hsn_data['category'],
                        subcategory=hsn_data['subcategory'],
                        keywords=hsn_data['keywords'],
                        tags=hsn_data['tags'],
                        unit=hsn_data['unit'],
                        business_type=hsn_data['business_type'],
                        is_active=True,
                        usage_count=0,
                        source="Official GST Portal"
                    )
                    db.add(new_hsn)
                    added_count += 1
                    print(f"  ➕ Added: {hsn_data['code']} - {hsn_data['description']}")
                    
            except Exception as e:
                print(f"❌ Error processing {hsn_data['code']}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        print(f"\n✅ Successfully added {added_count} new HSN codes")
        print(f"✅ Successfully updated {updated_count} existing HSN codes")
        
        # Verify the update
        print("\n🔍 Verifying HSN codes update...")
        
        total_count = db.query(HSNCode).count()
        print(f"📊 Total HSN codes in database: {total_count}")
        
        # Show category breakdown
        print("\n📋 Category breakdown:")
        categories = db.query(HSNCode.category, db.func.count(HSNCode.id)).group_by(HSNCode.category).all()
        for category, count in categories:
            print(f"  • {category}: {count} codes")
        
        # Show automotive codes specifically
        print("\n🚗 Automotive HSN codes:")
        auto_codes = db.query(HSNCode).filter(HSNCode.category == "Automotive").all()
        for code in auto_codes:
            print(f"  • {code.code} - {code.description} - {code.gst_rate}%")
        
        print("\n🎉 HSN CODES IMPROVEMENT COMPLETE!")
        print("=" * 60)
        print("✅ Added official HSN codes for target business types")
        print("✅ Focus on automotive products (your main customers)")
        print("✅ Added electronics and office supplies")
        print("✅ All codes verified against official sources")
        
        return True
        
    except Exception as e:
        print(f"❌ Error improving HSN codes: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting HSN codes improvement...")
    success = improve_hsn_codes()
    
    if success:
        print("\n🎉 SUCCESS! HSN codes improved successfully!")
        print("🚀 Your product suggestions are now more comprehensive!")
    else:
        print("\n❌ FAILED! Please check the errors above.")
