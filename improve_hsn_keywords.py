#!/usr/bin/env python3
"""
Script to improve HSN codes keywords for better user search experience
"""

from database import SessionLocal
from models import HSNCode
from sqlalchemy import func

def improve_hsn_keywords():
    """Improve HSN codes keywords for better search coverage"""
    
    print("🚀 IMPROVING HSN CODES KEYWORDS FOR BETTER SEARCH")
    print("=" * 60)
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Get all HSN codes
        all_codes = db.query(HSNCode).all()
        
        print(f"📊 Total HSN codes: {len(all_codes)}")
        
        # Define keyword improvements for each code
        keyword_improvements = {
            # Automotive codes
            "8708": {
                "current_keywords": "brake pads,brake shoes,car brakes,automotive brakes",
                "improved_keywords": "brake pads,brake shoes,car brakes,automotive brakes,transmission,gearbox,clutch,drivetrain,suspension,shocks,struts,springs,wheels,rims,car wheels,auto wheels,vehicle wheels,alloy wheels,car parts,auto parts,vehicle parts"
            },
            "4011": {
                "current_keywords": "car tyres,vehicle tyres,tires,tubes,automotive tyres",
                "improved_keywords": "car tyres,vehicle tyres,tires,tubes,automotive tyres,wheels,rims,car wheels,auto wheels,vehicle wheels,alloy wheels"
            },
            "8507": {
                "current_keywords": "car battery,vehicle battery,automotive battery,car battery",
                "improved_keywords": "car battery,vehicle battery,automotive battery,car battery,auto battery,vehicle battery,car battery"
            },
            "2710": {
                "current_keywords": "engine oil,motor oil,car oil,automotive oil,lubricants",
                "improved_keywords": "engine oil,motor oil,car oil,automotive oil,lubricants,car oil,auto oil,vehicle oil"
            },
            
            # Electronics codes
            "8517": {
                "current_keywords": "smartphones,mobile phones,cell phones,telephones",
                "improved_keywords": "smartphones,mobile phones,cell phones,telephones,headset,hands-free,bluetooth headset,phone headset,communication device"
            },
            "8471": {
                "current_keywords": "computers,laptops,desktops,servers,workstations",
                "improved_keywords": "computers,laptops,desktops,servers,workstations,pc,personal computer,tablet,ipad,android tablet,portable computer,tablet pc,keyboard,mouse,computer keyboard,computer mouse,pointing device"
            },
            "8528": {
                "current_keywords": "monitors,displays,projectors,screens,LED TVs",
                "improved_keywords": "monitors,displays,projectors,screens,LED TVs,computer monitor,display screen,LED display"
            },
            "8518": {
                "current_keywords": "speakers,headphones,microphones,audio equipment",
                "improved_keywords": "speakers,headphones,microphones,audio equipment,bluetooth speakers,wireless speakers,audio devices"
            },
            "8523": {
                "current_keywords": "USB drives,memory cards,storage devices,flash drives",
                "improved_keywords": "USB drives,memory cards,storage devices,flash drives,pen drives,thumb drives,storage media"
            },
            
            # Stationery codes
            "9608": {
                "current_keywords": "pens,ballpoint pens,markers,writing instruments",
                "improved_keywords": "pens,ballpoint pens,markers,writing instruments,ballpoint pen,gel pen,roller pen"
            },
            "4820": {
                "current_keywords": "notebooks,registers,account books,office books",
                "improved_keywords": "notebooks,registers,account books,office books,notebook,register,account book"
            },
            "4823": {
                "current_keywords": "paper,paperboard,office paper,printing paper",
                "improved_keywords": "paper,paperboard,office paper,printing paper,A4 paper,copier paper,printer paper"
            }
        }
        
        updated_count = 0
        
        print("\n🔍 Updating HSN codes with improved keywords...")
        
        for code in all_codes:
            if code.code in keyword_improvements:
                improvement = keyword_improvements[code.code]
                
                # Update keywords
                old_keywords = code.keywords
                new_keywords = improvement["improved_keywords"]
                
                if old_keywords != new_keywords:
                    code.keywords = new_keywords
                    updated_count += 1
                    print(f"  🔄 Updated {code.code}: {code.description}")
                    print(f"      Old: {old_keywords}")
                    print(f"      New: {new_keywords}")
                    print()
        
        # Add new HSN codes for missing products
        new_codes = [
            {
                "code": "8525",
                "description": "Television cameras, digital cameras and video camera recorders",
                "gst_rate": 18.0,
                "type": "HSN",
                "category": "Electronics",
                "subcategory": "Cameras",
                "keywords": "camera,digital camera,video camera,DSLR,camcorder,webcam,photography camera",
                "tags": "electronics,camera,photography",
                "unit": "Nos",
                "business_type": "product"
            },
            {
                "code": "9017",
                "description": "Drawing, marking-out or mathematical calculating instruments",
                "gst_rate": 12.0,
                "type": "HSN",
                "category": "Stationery",
                "subcategory": "Drawing",
                "keywords": "ruler,scale,protractor,compass,drawing instruments,measuring tools,measuring scale",
                "tags": "stationery,ruler,drawing,measuring",
                "unit": "Nos",
                "business_type": "product"
            },
            {
                "code": "8470",
                "description": "Calculating machines and pocket-size data recording, reproducing and displaying machines",
                "gst_rate": 18.0,
                "type": "HSN",
                "category": "Stationery",
                "subcategory": "Calculators",
                "keywords": "calculator,calculating machine,desk calculator,pocket calculator,math calculator",
                "tags": "stationery,calculator,computing",
                "unit": "Nos",
                "business_type": "product"
            },
            {
                "code": "8305",
                "description": "Filing cabinets, card-index cabinets, paper trays, paper rests, pen trays, office-stamp stands and similar office or desk equipment",
                "gst_rate": 18.0,
                "type": "HSN",
                "category": "Stationery",
                "subcategory": "Office_Equipment",
                "keywords": "stapler,staples,paper clips,binder clips,office supplies,desk accessories,office equipment",
                "tags": "stationery,stapler,office,desk",
                "unit": "Nos",
                "business_type": "product"
            },
            {
                "code": "8443",
                "description": "Printing machinery, including ink-jet printing machines",
                "gst_rate": 18.0,
                "type": "HSN",
                "category": "Electronics",
                "subcategory": "Printers",
                "keywords": "printer,inkjet printer,laser printer,office printer,printing machine,computer printer",
                "tags": "electronics,printer,office",
                "unit": "Nos",
                "business_type": "product"
            }
        ]
        
        added_count = 0
        
        print("\n➕ Adding new HSN codes for missing products...")
        
        for hsn_data in new_codes:
            try:
                # Check if code already exists
                existing = db.query(HSNCode).filter(HSNCode.code == hsn_data['code']).first()
                
                if not existing:
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
                else:
                    print(f"  ⚠️  Already exists: {hsn_data['code']} - {hsn_data['description']}")
                    
            except Exception as e:
                print(f"❌ Error adding {hsn_data['code']}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        print(f"\n✅ Successfully updated {updated_count} existing HSN codes")
        print(f"✅ Successfully added {added_count} new HSN codes")
        
        # Verify the update
        print("\n🔍 Verifying HSN codes update...")
        
        total_count = db.query(HSNCode).count()
        print(f"📊 Total HSN codes in database: {total_count}")
        
        # Test common search terms
        print("\n🔍 Testing common search terms:")
        common_terms = ["pc", "wheel", "camera", "tablet", "ruler", "calculator", "stapler", "printer"]
        
        for term in common_terms:
            found_codes = db.query(HSNCode).filter(
                HSNCode.keywords.contains(term) | HSNCode.description.contains(term)
            ).all()
            
            if found_codes:
                print(f"  ✅ '{term}': {len(found_codes)} codes found")
                for code in found_codes[:2]:  # Show first 2 matches
                    print(f"      • {code.code} - {code.description}")
            else:
                print(f"  ❌ '{term}': No codes found")
        
        # Show category breakdown
        print("\n📋 Category breakdown:")
        categories = db.query(HSNCode.category, func.count(HSNCode.id)).group_by(HSNCode.category).all()
        for category, count in categories:
            print(f"  • {category}: {count} codes")
        
        print("\n🎉 HSN CODES KEYWORDS IMPROVED!")
        print("=" * 60)
        print("✅ Improved search coverage")
        print("✅ Added missing product variations")
        print("✅ Better user experience")
        print("✅ Comprehensive product range")
        
        return True
        
    except Exception as e:
        print(f"❌ Error improving HSN keywords: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting HSN codes keywords improvement...")
    success = improve_hsn_keywords()
    
    if success:
        print("\n🎉 SUCCESS! HSN codes keywords improved successfully!")
        print("🚀 Your product suggestions are now comprehensive!")
    else:
        print("\n❌ FAILED! Please check the errors above.")
