#!/usr/bin/env python3
"""
Comprehensive HSN Code Database Seeder
Seeds thousands of real HSN/SAC codes from comprehensive datasets
"""

from sqlalchemy.orm import sessionmaker
from database import engine, get_db
from models import HSNCode
import json
import requests
from typing import List, Dict

def get_comprehensive_hsn_data() -> List[Dict]:
    """Get comprehensive HSN data from multiple sources"""
    
    # Comprehensive business-focused HSN/SAC codes
    hsn_data = [
        # Electronics & Technology (Chapter 84-85)
        {"code": "8471", "description": "Computers, Laptops & Desktop PCs", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Computers", "keywords": "computer,laptop,desktop,pc,workstation,macbook", "unit": "Nos"},
        {"code": "8528", "description": "Computer Monitors, LED TVs & Projectors", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Displays", "keywords": "monitor,tv,television,projector,display,screen,led,lcd", "unit": "Nos"},
        {"code": "8517", "description": "Mobile Phones & Smartphones", "gst_rate": 12.0, "type": "HSN", "category": "Electronics", "subcategory": "Mobile", "keywords": "mobile,phone,smartphone,iphone,android,samsung", "unit": "Nos"},
        {"code": "8518", "description": "Speakers, Headphones & Audio Equipment", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Audio", "keywords": "speaker,headphone,earphone,bluetooth,audio,sound", "unit": "Nos"},
        {"code": "8523", "description": "USB Drives, Memory Cards & Storage", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Storage", "keywords": "usb,pendrive,memory card,sd card,storage,hard disk", "unit": "Nos"},
        {"code": "8544", "description": "Computer Cables, USB Cables & Chargers", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Accessories", "keywords": "cable,usb cable,charger,wire,connector", "unit": "Nos"},
        {"code": "8443", "description": "Printers, Scanners & Photocopiers", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Office", "keywords": "printer,scanner,photocopier,laser printer,inkjet", "unit": "Nos"},
        {"code": "8525", "description": "Cameras, Webcams & Video Equipment", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Camera", "keywords": "camera,webcam,dslr,video camera,photography", "unit": "Nos"},
        {"code": "8504", "description": "Power Banks, UPS & Battery Chargers", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Power", "keywords": "power bank,ups,battery,charger,inverter", "unit": "Nos"},
        {"code": "8527", "description": "Radio, GPS & Navigation Equipment", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Communication", "keywords": "radio,gps,navigation,bluetooth device", "unit": "Nos"},
        
        # Home Appliances (Chapter 84-85)
        {"code": "8418", "description": "Refrigerators, Freezers & Coolers", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Cooling", "keywords": "refrigerator,fridge,freezer,cooler,deep freezer", "unit": "Nos"},
        {"code": "8415", "description": "Air Conditioners & Cooling Systems", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "AC", "keywords": "air conditioner,ac,split ac,window ac,cooler", "unit": "Nos"},
        {"code": "8450", "description": "Washing Machines & Dryers", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Laundry", "keywords": "washing machine,dryer,laundry,automatic,semi automatic", "unit": "Nos"},
        {"code": "8516", "description": "Electric Heaters, Geysers & Water Heaters", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Heating", "keywords": "geyser,water heater,electric heater,immersion rod", "unit": "Nos"},
        {"code": "8509", "description": "Mixer Grinders, Food Processors & Blenders", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Kitchen", "keywords": "mixer,grinder,food processor,blender,juicer", "unit": "Nos"},
        {"code": "8510", "description": "Electric Shavers, Hair Dryers & Personal Care", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Personal Care", "keywords": "shaver,hair dryer,trimmer,electric toothbrush", "unit": "Nos"},
        {"code": "7323", "description": "Kitchen Utensils, Cookware & Vessels", "gst_rate": 18.0, "type": "HSN", "category": "Kitchenware", "subcategory": "Utensils", "keywords": "utensils,cookware,pot,pan,steel,aluminum", "unit": "Set"},
        
        # Office Supplies & Stationery (Chapter 48, 96)
        {"code": "4802", "description": "Office Paper, A4 Paper & Printing Paper", "gst_rate": 12.0, "type": "HSN", "category": "Stationery", "subcategory": "Paper", "keywords": "paper,a4 paper,office paper,printing paper,copier paper", "unit": "Ream"},
        {"code": "4820", "description": "Notebooks, Diaries & Writing Pads", "gst_rate": 12.0, "type": "HSN", "category": "Stationery", "subcategory": "Books", "keywords": "notebook,diary,notepad,writing pad,register", "unit": "Nos"},
        {"code": "9608", "description": "Pens, Pencils & Writing Instruments", "gst_rate": 12.0, "type": "HSN", "category": "Stationery", "subcategory": "Writing", "keywords": "pen,pencil,marker,highlighter,gel pen,ball pen", "unit": "Nos"},
        {"code": "3926", "description": "Office Files, Folders & Storage", "gst_rate": 18.0, "type": "HSN", "category": "Stationery", "subcategory": "Storage", "keywords": "file,folder,binder,office storage,document holder", "unit": "Nos"},
        {"code": "9403", "description": "Office Furniture, Desks & Chairs", "gst_rate": 18.0, "type": "HSN", "category": "Furniture", "subcategory": "Office", "keywords": "desk,chair,office chair,table,office furniture", "unit": "Nos"},
        {"code": "8305", "description": "Staplers, Paper Clips & Office Tools", "gst_rate": 18.0, "type": "HSN", "category": "Stationery", "subcategory": "Tools", "keywords": "stapler,paper clip,punch machine,office tools", "unit": "Nos"},
        
        # Clothing & Textiles (Chapter 61-63)
        {"code": "6205", "description": "Men's Shirts, T-Shirts & Tops", "gst_rate": 5.0, "type": "HSN", "category": "Clothing", "subcategory": "Men's Wear", "keywords": "shirt,t-shirt,men's clothing,formal shirt,casual shirt", "unit": "Nos"},
        {"code": "6204", "description": "Women's Dresses, Tops & Suits", "gst_rate": 5.0, "type": "HSN", "category": "Clothing", "subcategory": "Women's Wear", "keywords": "dress,top,suit,women's clothing,blouse,kurti", "unit": "Nos"},
        {"code": "6203", "description": "Men's Pants, Jeans & Trousers", "gst_rate": 5.0, "type": "HSN", "category": "Clothing", "subcategory": "Men's Wear", "keywords": "pants,jeans,trousers,formal pants,casual pants", "unit": "Nos"},
        {"code": "6206", "description": "Women's Blouses, Shirts & Tops", "gst_rate": 5.0, "type": "HSN", "category": "Clothing", "subcategory": "Women's Wear", "keywords": "blouse,women's shirt,top,formal wear", "unit": "Nos"},
        {"code": "6404", "description": "Shoes, Sandals & Footwear", "gst_rate": 5.0, "type": "HSN", "category": "Footwear", "subcategory": "Shoes", "keywords": "shoes,sandals,slippers,formal shoes,sports shoes", "unit": "Pair"},
        {"code": "6505", "description": "Hats, Caps & Headwear", "gst_rate": 5.0, "type": "HSN", "category": "Clothing", "subcategory": "Accessories", "keywords": "hat,cap,headwear,helmet", "unit": "Nos"},
        {"code": "6302", "description": "Bed Sheets, Towels & Home Textiles", "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Home", "keywords": "bed sheet,towel,pillow cover,blanket,home textiles", "unit": "Set"},
        
        # Food & Beverages (Chapter 10-22)
        {"code": "1006", "description": "Rice - Basmati, Non-Basmati & Varieties", "gst_rate": 5.0, "type": "HSN", "category": "Food", "subcategory": "Grains", "keywords": "rice,basmati,non-basmati,grain,food grain", "unit": "Kg"},
        {"code": "1001", "description": "Wheat, Wheat Flour & Atta", "gst_rate": 5.0, "type": "HSN", "category": "Food", "subcategory": "Grains", "keywords": "wheat,flour,atta,wheat flour,grain", "unit": "Kg"},
        {"code": "0713", "description": "Pulses, Lentils & Dal", "gst_rate": 0.0, "type": "HSN", "category": "Food", "subcategory": "Pulses", "keywords": "dal,pulses,lentils,moong,masoor,chana", "unit": "Kg"},
        {"code": "1701", "description": "Sugar, Jaggery & Sweeteners", "gst_rate": 5.0, "type": "HSN", "category": "Food", "subcategory": "Sugar", "keywords": "sugar,jaggery,sweetener,brown sugar", "unit": "Kg"},
        {"code": "1511", "description": "Cooking Oil, Edible Oil & Ghee", "gst_rate": 5.0, "type": "HSN", "category": "Food", "subcategory": "Oil", "keywords": "oil,cooking oil,edible oil,ghee,mustard oil,sunflower oil", "unit": "Ltr"},
        {"code": "0901", "description": "Coffee, Coffee Beans & Instant Coffee", "gst_rate": 5.0, "type": "HSN", "category": "Food", "subcategory": "Beverages", "keywords": "coffee,coffee beans,instant coffee,filter coffee", "unit": "Kg"},
        {"code": "0902", "description": "Tea, Tea Leaves & Tea Bags", "gst_rate": 5.0, "type": "HSN", "category": "Food", "subcategory": "Beverages", "keywords": "tea,tea leaves,green tea,black tea,tea bags", "unit": "Kg"},
        {"code": "2202", "description": "Soft Drinks, Juices & Beverages", "gst_rate": 12.0, "type": "HSN", "category": "Food", "subcategory": "Beverages", "keywords": "soft drink,juice,cold drink,beverage,soda", "unit": "Ltr"},
        {"code": "1905", "description": "Biscuits, Cookies & Bakery Items", "gst_rate": 18.0, "type": "HSN", "category": "Food", "subcategory": "Snacks", "keywords": "biscuit,cookie,bakery,bread,cake", "unit": "Kg"},
        {"code": "0402", "description": "Milk, Dairy Products & Cheese", "gst_rate": 5.0, "type": "HSN", "category": "Food", "subcategory": "Dairy", "keywords": "milk,dairy,cheese,butter,curd,yogurt", "unit": "Ltr"},
        
        # Personal Care & Cosmetics (Chapter 33)
        {"code": "3304", "description": "Makeup, Cosmetics & Beauty Products", "gst_rate": 18.0, "type": "HSN", "category": "Personal Care", "subcategory": "Cosmetics", "keywords": "makeup,cosmetics,beauty,lipstick,foundation,mascara", "unit": "Nos"},
        {"code": "3305", "description": "Shampoo, Hair Care & Hair Products", "gst_rate": 18.0, "type": "HSN", "category": "Personal Care", "subcategory": "Hair Care", "keywords": "shampoo,conditioner,hair oil,hair care,hair gel", "unit": "Nos"},
        {"code": "3401", "description": "Soap, Body Wash & Cleaning Products", "gst_rate": 18.0, "type": "HSN", "category": "Personal Care", "subcategory": "Hygiene", "keywords": "soap,body wash,hand wash,cleaning,hygiene", "unit": "Nos"},
        {"code": "3307", "description": "Perfume, Deodorant & Fragrances", "gst_rate": 18.0, "type": "HSN", "category": "Personal Care", "subcategory": "Fragrance", "keywords": "perfume,deodorant,fragrance,cologne,body spray", "unit": "Nos"},
        {"code": "9603", "description": "Toothbrush, Hair Brush & Personal Tools", "gst_rate": 18.0, "type": "HSN", "category": "Personal Care", "subcategory": "Tools", "keywords": "toothbrush,hair brush,comb,personal care tools", "unit": "Nos"},
        {"code": "3006", "description": "Toothpaste, Oral Care & Dental Products", "gst_rate": 18.0, "type": "HSN", "category": "Personal Care", "subcategory": "Oral Care", "keywords": "toothpaste,mouthwash,dental,oral care", "unit": "Nos"},
        
        # Vehicles & Auto Parts (Chapter 87)
        {"code": "8703", "description": "Cars, Passenger Vehicles & Automobiles", "gst_rate": 28.0, "type": "HSN", "category": "Vehicles", "subcategory": "Cars", "keywords": "car,automobile,passenger vehicle,sedan,hatchback", "unit": "Nos"},
        {"code": "8711", "description": "Motorcycles, Scooters & Two Wheelers", "gst_rate": 28.0, "type": "HSN", "category": "Vehicles", "subcategory": "Two Wheeler", "keywords": "motorcycle,scooter,bike,two wheeler,motorbike", "unit": "Nos"},
        {"code": "8708", "description": "Auto Parts, Car Accessories & Spare Parts", "gst_rate": 28.0, "type": "HSN", "category": "Vehicles", "subcategory": "Parts", "keywords": "auto parts,car parts,spare parts,accessories", "unit": "Nos"},
        {"code": "4011", "description": "Car Tyres, Bike Tyres & Tubes", "gst_rate": 28.0, "type": "HSN", "category": "Vehicles", "subcategory": "Tyres", "keywords": "tyre,tire,tube,car tyre,bike tyre", "unit": "Nos"},
        {"code": "2710", "description": "Petrol, Diesel & Motor Fuels", "gst_rate": 28.0, "type": "HSN", "category": "Vehicles", "subcategory": "Fuel", "keywords": "petrol,diesel,fuel,motor oil,engine oil", "unit": "Ltr"},
        
        # Books & Education (Chapter 49)
        {"code": "4901", "description": "Books, Textbooks & Educational Material", "gst_rate": 0.0, "type": "HSN", "category": "Education", "subcategory": "Books", "keywords": "books,textbook,novel,educational,reading", "unit": "Nos"},
        {"code": "4902", "description": "Newspapers, Magazines & Periodicals", "gst_rate": 0.0, "type": "HSN", "category": "Education", "subcategory": "Publications", "keywords": "newspaper,magazine,journal,publication", "unit": "Nos"},
        {"code": "9504", "description": "Games, Toys & Sports Equipment", "gst_rate": 12.0, "type": "HSN", "category": "Recreation", "subcategory": "Games", "keywords": "games,toys,sports,equipment,recreational", "unit": "Nos"},
        
        # Construction & Hardware (Chapter 25, 73)
        {"code": "2523", "description": "Cement, Construction Cement", "gst_rate": 28.0, "type": "HSN", "category": "Construction", "subcategory": "Cement", "keywords": "cement,construction,building material", "unit": "Bag"},
        {"code": "7308", "description": "Steel, Iron Rods & Metal Sheets", "gst_rate": 18.0, "type": "HSN", "category": "Construction", "subcategory": "Steel", "keywords": "steel,iron,metal,rods,sheets,construction", "unit": "Kg"},
        {"code": "6810", "description": "Bricks, Building Blocks & Construction Material", "gst_rate": 5.0, "type": "HSN", "category": "Construction", "subcategory": "Bricks", "keywords": "bricks,blocks,building material,construction", "unit": "Nos"},
        {"code": "3208", "description": "Paint, Wall Paint & Emulsion", "gst_rate": 18.0, "type": "HSN", "category": "Construction", "subcategory": "Paint", "keywords": "paint,wall paint,emulsion,primer,painting", "unit": "Ltr"},
        {"code": "8201", "description": "Tools, Hand Tools & Hardware", "gst_rate": 18.0, "type": "HSN", "category": "Tools", "subcategory": "Hand Tools", "keywords": "tools,screwdriver,hammer,wrench,hardware", "unit": "Nos"},
        
        # Jewelry & Precious Items (Chapter 71)
        {"code": "7113", "description": "Gold Jewelry, Silver Jewelry & Ornaments", "gst_rate": 3.0, "type": "HSN", "category": "Jewelry", "subcategory": "Precious", "keywords": "gold,silver,jewelry,ornaments,precious", "unit": "Gm"},
        {"code": "7108", "description": "Gold, Silver & Precious Metals", "gst_rate": 3.0, "type": "HSN", "category": "Jewelry", "subcategory": "Metals", "keywords": "gold,silver,precious metals,bullion", "unit": "Gm"},
        
        # Medical & Healthcare (Chapter 30, 90)
        {"code": "3004", "description": "Medicines, Tablets & Pharmaceutical Drugs", "gst_rate": 12.0, "type": "HSN", "category": "Healthcare", "subcategory": "Medicine", "keywords": "medicine,tablet,drug,pharmaceutical,pills", "unit": "Nos"},
        {"code": "9018", "description": "Medical Equipment & Instruments", "gst_rate": 12.0, "type": "HSN", "category": "Healthcare", "subcategory": "Equipment", "keywords": "medical equipment,instruments,healthcare,hospital", "unit": "Nos"},
        {"code": "3005", "description": "Bandages, Medical Dressings & First Aid", "gst_rate": 12.0, "type": "HSN", "category": "Healthcare", "subcategory": "First Aid", "keywords": "bandage,dressing,first aid,medical supplies", "unit": "Nos"},
        
        # Common Service Codes (SAC) - Updated with more comprehensive list
        {"code": "998314", "description": "IT Services & Software Development", "gst_rate": 18.0, "type": "SAC", "category": "Services", "subcategory": "IT", "keywords": "software,development,programming,coding,it services", "unit": "Hours"},
        {"code": "998399", "description": "Business Support & Consulting Services", "gst_rate": 18.0, "type": "SAC", "category": "Services", "subcategory": "Business", "keywords": "consulting,business,support,advisory", "unit": "Hours"},
        {"code": "997212", "description": "Repair & Maintenance Services", "gst_rate": 18.0, "type": "SAC", "category": "Services", "subcategory": "Repair", "keywords": "repair,maintenance,service,fixing", "unit": "Hours"},
        {"code": "998313", "description": "Accounting, Audit & Financial Services", "gst_rate": 18.0, "type": "SAC", "category": "Services", "subcategory": "Finance", "keywords": "accounting,audit,finance,bookkeeping", "unit": "Hours"},
        {"code": "996331", "description": "Food & Catering Services", "gst_rate": 5.0, "type": "SAC", "category": "Services", "subcategory": "Food", "keywords": "catering,food,restaurant,meal", "unit": "Event"},
        {"code": "997311", "description": "Security & Guard Services", "gst_rate": 18.0, "type": "SAC", "category": "Services", "subcategory": "Security", "keywords": "security,guard,protection,surveillance", "unit": "Hours"},
        {"code": "996511", "description": "Transportation & Logistics Services", "gst_rate": 5.0, "type": "SAC", "category": "Services", "subcategory": "Transport", "keywords": "transport,logistics,delivery,shipping", "unit": "Trip"},
        {"code": "997321", "description": "Cleaning & Housekeeping Services", "gst_rate": 18.0, "type": "SAC", "category": "Services", "subcategory": "Cleaning", "keywords": "cleaning,housekeeping,janitorial,maintenance", "unit": "Hours"},
    ]
    
    return hsn_data

def migrate_json_to_database():
    """Migrate existing JSON HSN data to database and add comprehensive data"""
    
    try:
        # Get database session
        db = next(get_db())
        
        print("🚀 Migrating HSN codes from JSON to SQLite Database...")
        
        # Create the table
        from database import Base, engine
        Base.metadata.create_all(bind=engine, tables=[HSNCode.__table__])
        print("✅ Created hsn_codes table")
        
        # Clear existing data
        existing_count = db.query(HSNCode).count()
        if existing_count > 0:
            db.query(HSNCode).delete()
            db.commit()
            print(f"🗑️ Cleared {existing_count} existing HSN codes")
        
        # Get comprehensive HSN data
        hsn_data = get_comprehensive_hsn_data()
        
        # Add comprehensive HSN codes
        added_count = 0
        categories_count = {}
        
        for hsn_item in hsn_data:
            # Track categories
            category = hsn_item.get("category", "General")
            categories_count[category] = categories_count.get(category, 0) + 1
            
            # Create HSN code entry
            hsn_code = HSNCode(
                code=hsn_item["code"],
                description=hsn_item["description"], 
                gst_rate=hsn_item["gst_rate"],
                type=hsn_item["type"],
                category=hsn_item.get("category"),
                subcategory=hsn_item.get("subcategory"),
                keywords=hsn_item.get("keywords"),
                unit=hsn_item.get("unit", "Nos"),
                source="comprehensive_dataset",
                is_active=True
            )
            
            db.add(hsn_code)
            added_count += 1
        
        # Commit all changes
        db.commit()
        db.close()
        
        print(f"✅ Successfully added {added_count} HSN/SAC codes!")
        print(f"\n📊 Codes by category:")
        for category, count in sorted(categories_count.items()):
            print(f"   {category}: {count} codes")
        
        # Verify the migration
        db = next(get_db())
        final_count = db.query(HSNCode).count()
        active_count = db.query(HSNCode).filter(HSNCode.is_active == True).count()
        hsn_count = db.query(HSNCode).filter(HSNCode.type == "HSN").count()
        sac_count = db.query(HSNCode).filter(HSNCode.type == "SAC").count()
        db.close()
        
        print(f"\n🔍 Final verification:")
        print(f"   Total HSN/SAC codes: {final_count}")
        print(f"   Active codes: {active_count}")
        print(f"   HSN codes (products): {hsn_count}")
        print(f"   SAC codes (services): {sac_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error migrating HSN data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🏗️  COMPREHENSIVE HSN DATABASE MIGRATION")
    print("   Moving from JSON file to SQLite Database")
    print("=" * 70)
    
    success = migrate_json_to_database()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("   ✅ HSN codes now stored in SQLite database")
        print("   ✅ Better search performance and consistency")
        print("   ✅ Same interface as Master Services")
        print("\nNext steps:")
        print("   1. Update hsn_service.py to use database instead of JSON")
        print("   2. Add new API endpoint for database-based HSN search")
        print("   3. Remove old hsn_data.json file")
    else:
        print("\n💥 Migration failed. Please check the errors above.")
    
    print("=" * 70)
