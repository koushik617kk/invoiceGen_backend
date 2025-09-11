#!/usr/bin/env python3
"""
Enhanced product seeding script - Creates SPECIFIC products instead of HSN categories
This addresses the user's concern about getting generic HSN descriptions instead of specific products
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import HSNCode

def get_specific_products_data():
    """
    Return comprehensive list of SPECIFIC products (not HSN categories)
    Each product is actionable and can be directly used in invoices
    Based on user's provided list + additional products for completeness
    """
    
    return [
        # ===== ELECTRONICS & IT HARDWARE =====
        
        # Mobile Phones & Accessories (HSN 8517)
        {
            "code": "8517",
            "description": "Samsung Galaxy A54 Smartphone",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Phones",
            "keywords": "samsung,galaxy,smartphone,mobile,phone,android",
            "tags": "mobile,smartphone,samsung",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "iPhone 15 Pro Max",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Phones",
            "keywords": "iphone,apple,smartphone,mobile,phone,ios",
            "tags": "mobile,smartphone,apple",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "OnePlus 11 5G Smartphone",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics", 
            "subcategory": "Mobile_Phones",
            "keywords": "oneplus,smartphone,mobile,5g,android",
            "tags": "mobile,smartphone,oneplus",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "Mobile Phone Tempered Glass Screen Protector",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Accessories",
            "keywords": "screen protector,tempered glass,mobile accessory,protection",
            "tags": "accessory,protection,screen",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "Leather Mobile Phone Back Cover Case",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Accessories",
            "keywords": "mobile case,phone cover,leather case,back cover,protection",
            "tags": "case,cover,protection",
            "unit": "Nos", 
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "Fast Charging USB Type-C Mobile Charger",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Accessories",
            "keywords": "mobile charger,usb type-c,fast charging,adapter",
            "tags": "charger,usb,charging",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "USB Data Cable Type-C to Lightning",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Accessories",
            "keywords": "data cable,usb cable,type-c,lightning,charging cable",
            "tags": "cable,usb,data",
            "unit": "Nos",
            "business_type": "product"
        },

        # Computers & Laptops (HSN 8471)
        {
            "code": "8471",
            "description": "Dell Inspiron 15 3000 Laptop",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computers",
            "keywords": "dell,laptop,inspiron,computer,notebook",
            "tags": "laptop,computer,dell",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "HP Pavilion Gaming Laptop",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computers",
            "keywords": "hp,laptop,gaming,pavilion,computer",
            "tags": "laptop,gaming,hp",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Lenovo ThinkPad E14 Business Laptop",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computers",
            "keywords": "lenovo,thinkpad,business laptop,computer",
            "tags": "laptop,business,lenovo",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Desktop Computer Intel Core i5",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computers",
            "keywords": "desktop,computer,intel,core i5,pc",
            "tags": "desktop,computer,intel",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Logitech MX Master 3 Wireless Mouse",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computer_Accessories",
            "keywords": "mouse,logitech,wireless,computer mouse,mx master",
            "tags": "mouse,wireless,logitech",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Mechanical Gaming Keyboard RGB Backlit",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computer_Accessories",
            "keywords": "keyboard,mechanical,gaming,rgb,backlit",
            "tags": "keyboard,gaming,mechanical",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "HP LaserJet Pro MFP Printer",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Printers",
            "keywords": "printer,hp,laserjet,mfp,scanner,office printer",
            "tags": "printer,hp,office",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Canon PIXMA Inkjet Printer",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Printers",
            "keywords": "printer,canon,pixma,inkjet,home printer",
            "tags": "printer,canon,inkjet",
            "unit": "Nos",
            "business_type": "product"
        },

        # TVs & Monitors (HSN 8528)
        {
            "code": "8528",
            "description": "Samsung 55-inch 4K Smart LED TV",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Television",
            "keywords": "samsung,smart tv,led tv,4k,55 inch,television",
            "tags": "tv,smart,samsung",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8528",
            "description": "LG OLED 65-inch Smart TV",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Television",
            "keywords": "lg,oled tv,smart tv,65 inch,television",
            "tags": "tv,oled,lg",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8528",
            "description": "Dell 27-inch 4K Computer Monitor",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Monitors",
            "keywords": "monitor,dell,4k,27 inch,computer monitor,display",
            "tags": "monitor,display,dell",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8528",
            "description": "Epson PowerLite Projector",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Projectors",
            "keywords": "projector,epson,powerlite,presentation,display",
            "tags": "projector,epson,presentation",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== AUTOMOTIVE PARTS =====
        
        # Brake System (HSN 8708)
        {
            "code": "8708",
            "description": "Maruti Suzuki Swift Brake Pads",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Brake_Parts",
            "keywords": "brake pads,maruti suzuki,swift,car parts,braking",
            "tags": "brake,maruti,swift",
            "unit": "Set",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "Hyundai i20 Brake Shoes",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Brake_Parts",
            "keywords": "brake shoes,hyundai,i20,car parts,braking",
            "tags": "brake,hyundai,i20",
            "unit": "Set",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "Honda City Clutch Plate Assembly",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Engine_Parts",
            "keywords": "clutch plate,honda city,car parts,transmission",
            "tags": "clutch,honda,city",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "Toyota Innova Shock Absorber",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Suspension_Parts",
            "keywords": "shock absorber,toyota innova,car parts,suspension",
            "tags": "shock,toyota,innova",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "Car Air Filter Universal",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Filters",
            "keywords": "air filter,car filter,universal,engine filter",
            "tags": "filter,air,car",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "LED Headlight Bulbs H4",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Lighting",
            "keywords": "headlight,led bulbs,h4,car lights,automotive lighting",
            "tags": "headlight,led,lighting",
            "unit": "Pair",
            "business_type": "product"
        },

        # Car Batteries & Fluids
        {
            "code": "8507",
            "description": "Exide Car Battery 55Ah",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Batteries",
            "keywords": "car battery,exide,55ah,automotive battery",
            "tags": "battery,exide,car",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "2710",
            "description": "Castrol GTX Engine Oil 5W-30",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Lubricants",
            "keywords": "engine oil,castrol,5w-30,motor oil,car oil",
            "tags": "oil,castrol,engine",
            "unit": "Liters",
            "business_type": "product"
        },
        {
            "code": "4011",
            "description": "MRF ZLX Car Tyre 185/65 R15",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Tyres",
            "keywords": "car tyre,mrf,zlx,185/65 r15,car tire",
            "tags": "tyre,mrf,car",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== TEXTILES & GARMENTS =====
        
        # Men's Clothing (HSN 6205, 6203)
        {
            "code": "6205",
            "description": "Men's Cotton Formal Shirt White",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Men_Clothing",
            "keywords": "men shirt,cotton shirt,formal shirt,white shirt",
            "tags": "shirt,men,formal",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "6205",
            "description": "Men's Casual Check Shirt",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Men_Clothing",
            "keywords": "men shirt,casual shirt,check shirt,cotton shirt",
            "tags": "shirt,men,casual",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "6203",
            "description": "Men's Formal Trouser Black",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Men_Clothing",
            "keywords": "men trouser,formal pant,black trouser,office wear",
            "tags": "trouser,men,formal",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "6109",
            "description": "Men's Cotton Round Neck T-Shirt",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Men_Clothing",
            "keywords": "t-shirt,cotton t-shirt,round neck,men tshirt",
            "tags": "tshirt,men,cotton",
            "unit": "Nos",
            "business_type": "product"
        },

        # Women's Clothing (HSN 6204)
        {
            "code": "6204",
            "description": "Women's Cotton Kurti Ethnic Wear",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Women_Clothing",
            "keywords": "kurti,women kurti,cotton kurti,ethnic wear,indian wear",
            "tags": "kurti,women,ethnic",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "6204",
            "description": "Women's Formal Shirt Office Wear",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Women_Clothing",
            "keywords": "women shirt,formal shirt,office wear,ladies shirt",
            "tags": "shirt,women,formal",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "6204",
            "description": "Women's Denim Jeans Blue",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Women_Clothing",
            "keywords": "jeans,women jeans,denim,blue jeans,ladies jeans",
            "tags": "jeans,women,denim",
            "unit": "Nos",
            "business_type": "product"
        },

        # Home Textiles (HSN 6302, 5208)
        {
            "code": "6302",
            "description": "Cotton Double Bed Sheet Set with Pillow Covers",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Home_Textiles",
            "keywords": "bed sheet,cotton bed sheet,double bed,pillow cover,bedding",
            "tags": "bedsheet,cotton,home",
            "unit": "Set",
            "business_type": "product"
        },
        {
            "code": "5208",
            "description": "Pure Cotton Fabric 44-inch Width",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Fabrics",
            "keywords": "cotton fabric,pure cotton,cloth,fabric material",
            "tags": "fabric,cotton,cloth",
            "unit": "Meters",
            "business_type": "product"
        },

        # ===== FMCG & DAILY USE ITEMS =====
        
        # Personal Care (HSN 3401, 3305, 3307, 3304)
        {
            "code": "3401",
            "description": "Dettol Antibacterial Hand Soap 125g",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Personal_Care",
            "keywords": "soap,dettol,antibacterial,hand soap,personal care",
            "tags": "soap,dettol,personal",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "3305",
            "description": "L'Oreal Paris Shampoo 340ml",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Personal_Care",
            "keywords": "shampoo,loreal,hair care,340ml,personal care",
            "tags": "shampoo,loreal,hair",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "3401",
            "description": "Ariel Detergent Powder 1kg",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Cleaning",
            "keywords": "detergent,ariel,washing powder,1kg,laundry",
            "tags": "detergent,ariel,cleaning",
            "unit": "Kg",
            "business_type": "product"
        },
        {
            "code": "3307",
            "description": "Colgate Total Toothpaste 150g",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Personal_Care",
            "keywords": "toothpaste,colgate,total,150g,oral care",
            "tags": "toothpaste,colgate,oral",
            "unit": "Nos",
            "business_type": "product"
        },

        # Food Items (HSN 2106, 1701, 1006, 1507)
        {
            "code": "2106",
            "description": "Maggi 2-Minute Noodles Masala 70g",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Food_Items",
            "keywords": "maggi,noodles,instant noodles,masala,ready to eat",
            "tags": "noodles,maggi,food",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "1006",
            "description": "Basmati Rice Premium Quality 5kg",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Food_Items",
            "keywords": "basmati rice,premium rice,5kg,rice,food grain",
            "tags": "rice,basmati,food",
            "unit": "Kg",
            "business_type": "product"
        },
        {
            "code": "1507",
            "description": "Fortune Sunflower Cooking Oil 1L",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Food_Items",
            "keywords": "cooking oil,sunflower oil,fortune,1 liter,edible oil",
            "tags": "oil,fortune,cooking",
            "unit": "Liters",
            "business_type": "product"
        },

        # ===== PHARMACEUTICALS & MEDICAL =====
        
        # Medicines (HSN 3004, 3005)
        {
            "code": "3004",
            "description": "Paracetamol 650mg Tablets Strip of 10",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Pharmaceuticals",
            "subcategory": "Medicines",
            "keywords": "paracetamol,tablets,650mg,fever,pain relief,medicine",
            "tags": "medicine,paracetamol,tablets",
            "unit": "Strip",
            "business_type": "product"
        },
        {
            "code": "3004",
            "description": "Crocin Advance Tablet 500mg",
            "gst_rate": 12.0,
            "type": "HSN",
            "category": "Pharmaceuticals",
            "subcategory": "Medicines",
            "keywords": "crocin,tablets,500mg,fever,headache,medicine",
            "tags": "medicine,crocin,tablets",
            "unit": "Strip",
            "business_type": "product"
        },
        {
            "code": "3005",
            "description": "Cotton Bandage Roll 6cm x 4m",
            "gst_rate": 12.0,
            "type": "HSN",
            "category": "Pharmaceuticals",
            "subcategory": "Medical_Supplies",
            "keywords": "bandage,cotton bandage,medical,first aid,6cm",
            "tags": "bandage,medical,cotton",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "9018",
            "description": "Digital Thermometer Medical Grade",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Pharmaceuticals",
            "subcategory": "Medical_Equipment",
            "keywords": "thermometer,digital,medical,fever,temperature",
            "tags": "thermometer,medical,digital",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== STATIONERY & OFFICE SUPPLIES =====
        
        # Paper Products (HSN 4817)
        {
            "code": "4817",
            "description": "A4 Size Copier Paper 500 Sheets",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Paper_Products",
            "keywords": "a4 paper,copier paper,500 sheets,office paper,printing paper",
            "tags": "paper,a4,office",
            "unit": "Ream",
            "business_type": "product"
        },
        {
            "code": "4817",
            "description": "Spiral Notebook 200 Pages Single Line",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Paper_Products",
            "keywords": "notebook,spiral,200 pages,single line,writing pad",
            "tags": "notebook,spiral,writing",
            "unit": "Nos",
            "business_type": "product"
        },

        # Writing Instruments (HSN 9608, 9609)
        {
            "code": "9608",
            "description": "Reynolds Ball Pen Blue Ink",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Writing_Instruments",
            "keywords": "ball pen,reynolds,blue ink,pen,writing",
            "tags": "pen,reynolds,writing",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "9608",
            "description": "Faber-Castell Pencil HB Grade",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Writing_Instruments",
            "keywords": "pencil,faber castell,hb grade,writing,drawing",
            "tags": "pencil,faber,writing",
            "unit": "Nos",
            "business_type": "product"
        }
    ]

def seed_specific_products():
    """Seed the database with specific, actionable products"""
    
    print("🚀 SEEDING SPECIFIC PRODUCTS (Not HSN Categories!)")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Check current HSN codes count
        existing_hsn = db.query(HSNCode).count()
        print(f"📊 Current HSN codes in database: {existing_hsn}")
        
        products_data = get_specific_products_data()
        
        added_count = 0
        updated_count = 0
        
        for product_data in products_data:
            # Check if product already exists by description
            existing = db.query(HSNCode).filter(
                HSNCode.description == product_data["description"]
            ).first()
            
            if existing:
                # Update existing product
                for key, value in product_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                updated_count += 1
                print(f"✏️  Updated: {product_data['description']}")
            else:
                # Create new product - but handle unique constraint on code field
                # Generate a unique code by appending a suffix if needed
                base_code = product_data["code"]
                unique_code = base_code
                suffix = 1
                
                # Check if this exact code already exists
                while db.query(HSNCode).filter(HSNCode.code == unique_code).first():
                    unique_code = f"{base_code}_{suffix:03d}"
                    suffix += 1
                    if suffix > 999:  # Safety limit
                        break
                
                # Use the unique code
                product_data_copy = product_data.copy()
                product_data_copy["code"] = unique_code
                
                try:
                    product = HSNCode(**product_data_copy)
                    db.add(product)
                    db.commit()  # Commit each product individually
                    added_count += 1
                    
                    if unique_code != base_code:
                        print(f"✅ Added: {product_data['description']} (Code: {unique_code})")
                    else:
                        print(f"✅ Added: {product_data['description']}")
                except Exception as e:
                    db.rollback()
                    print(f"⚠️  Skipped: {product_data['description']} - {str(e)[:100]}")
                    continue
        
        print(f"\n🎉 PRODUCT SEEDING COMPLETE!")
        print(f"📈 Added: {added_count} new products")
        print(f"🔄 Updated: {updated_count} existing products")
        print(f"📊 Total HSN codes now: {db.query(HSNCode).count()}")
        
        # Show some examples by category
        print(f"\n💡 EXAMPLE SPECIFIC PRODUCTS BY CATEGORY:")
        
        categories = ["Electronics", "Automotive", "Textiles", "FMCG", "Pharmaceuticals"]
        for category in categories:
            sample_products = db.query(HSNCode).filter(
                HSNCode.category == category,
                HSNCode.type == "HSN"
            ).limit(3).all()
            
            if sample_products:
                print(f"\n📱 {category.upper()}:")
                for product in sample_products:
                    print(f"   • {product.description}")
                    print(f"     HSN: {product.code} | GST: {product.gst_rate}% | Unit: {product.unit}")
        
    except Exception as e:
        print(f"❌ Error seeding products: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_specific_products()
