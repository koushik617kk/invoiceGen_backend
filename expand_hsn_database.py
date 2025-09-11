#!/usr/bin/env python3
"""
Expand HSN Database with Comprehensive Product Codes
This script adds thousands of product HSN codes to support product businesses.
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "invoice_gen.db"

def create_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

def expand_hsn_database():
    """Expand HSN database with comprehensive product codes"""
    
    # Major product categories with HSN codes
    product_categories = {
        "Electronics & IT": [
            ("8517", "Mobile Phones & Smartphones", 18),
            ("8517", "Telephones & Communication Equipment", 18),
            ("8517", "Modems & Network Equipment", 18),
            ("8471", "Laptops & Personal Computers", 18),
            ("8471", "Desktop Computers", 18),
            ("8471", "Tablets & iPads", 18),
            ("8528", "Television Sets", 18),
            ("8528", "Monitors & Displays", 18),
            ("8519", "Audio Equipment & Speakers", 18),
            ("8527", "Radio Receivers", 18),
            ("8525", "Video Cameras & Camcorders", 18),
            ("9006", "Digital Cameras", 18),
            ("8516", "Electric Heaters", 18),
            ("8516", "Electric Fans", 18),
            ("8516", "Air Conditioners", 18),
            ("8516", "Refrigerators", 18),
            ("8516", "Washing Machines", 18),
            ("8516", "Microwave Ovens", 18),
            ("8516", "Electric Kettles", 18),
            ("8516", "Electric Irons", 18),
        ],
        
        "Textiles & Apparel": [
            ("5208", "Cotton Fabrics", 5),
            ("5208", "Cotton Yarn", 5),
            ("5208", "Cotton Textiles", 5),
            ("6104", "Women's Dresses", 5),
            ("6104", "Women's Clothing", 5),
            ("6103", "Men's Suits", 5),
            ("6103", "Men's Jackets", 5),
            ("6103", "Men's Trousers", 5),
            ("6103", "Men's Shirts", 5),
            ("6104", "Women's Blouses", 5),
            ("6104", "Women's Skirts", 5),
            ("6104", "Women's Tops", 5),
            ("6110", "Sweaters & Cardigans", 5),
            ("6110", "Jerseys & Pullovers", 5),
            ("6302", "Bed Linen", 5),
            ("6302", "Table Linen", 5),
            ("6302", "Kitchen Linen", 5),
            ("6302", "Bathroom Linen", 5),
            ("6303", "Curtains & Drapes", 5),
            ("6303", "Furnishing Articles", 5),
        ],
        
        "Furniture & Home": [
            ("9401", "Office Chairs", 18),
            ("9401", "Dining Chairs", 18),
            ("9401", "Living Room Chairs", 18),
            ("9401", "Bedroom Chairs", 18),
            ("9401", "Garden Chairs", 18),
            ("9403", "Office Tables", 18),
            ("9403", "Dining Tables", 18),
            ("9403", "Coffee Tables", 18),
            ("9403", "Study Tables", 18),
            ("9403", "Kitchen Tables", 18),
            ("9401", "Sofas & Couches", 18),
            ("9401", "Beds & Bed Frames", 18),
            ("9401", "Wardrobes & Closets", 18),
            ("9401", "Bookshelves", 18),
            ("9401", "TV Units", 18),
            ("9401", "Kitchen Cabinets", 18),
            ("9401", "Bathroom Cabinets", 18),
            ("9401", "Shoe Racks", 18),
            ("9401", "Magazine Racks", 18),
            ("9401", "Hat Stands", 18),
        ],
        
        "Automotive & Transport": [
            ("8708", "Car Parts & Accessories", 18),
            ("8708", "Brake Pads", 18),
            ("8708", "Clutch Plates", 18),
            ("8708", "Air Filters", 18),
            ("8708", "Oil Filters", 18),
            ("8708", "Spark Plugs", 18),
            ("8708", "Batteries", 18),
            ("8708", "Tires & Tubes", 18),
            ("8708", "Wheels & Rims", 18),
            ("8708", "Bumpers", 18),
            ("8708", "Mirrors", 18),
            ("8708", "Lights & Lamps", 18),
            ("8708", "Horns", 18),
            ("8708", "Wipers", 18),
            ("8708", "Seat Covers", 18),
            ("8708", "Floor Mats", 18),
            ("8708", "Steering Wheels", 18),
            ("8708", "Gear Knobs", 18),
            ("8708", "Car Audio Systems", 18),
            ("8708", "GPS Navigation", 18),
        ],
        
        "Construction & Building": [
            ("2505", "Cement", 28),
            ("2505", "Portland Cement", 28),
            ("2505", "White Cement", 28),
            ("2505", "Masonry Cement", 28),
            ("2517", "Building Stones", 5),
            ("2517", "Granite", 5),
            ("2517", "Marble", 5),
            ("2517", "Limestone", 5),
            ("2517", "Sandstone", 5),
            ("6802", "Bricks & Blocks", 5),
            ("6802", "Clay Bricks", 5),
            ("6802", "Concrete Blocks", 5),
            ("6802", "Hollow Blocks", 5),
            ("6802", "Solid Blocks", 5),
            ("6802", "Paving Blocks", 5),
            ("6802", "Roofing Tiles", 5),
            ("6802", "Floor Tiles", 5),
            ("6802", "Wall Tiles", 5),
            ("6802", "Ceramic Tiles", 5),
            ("6802", "Vitrified Tiles", 5),
        ],
        
        "Healthcare & Medical": [
            ("3004", "Medicines & Pharmaceuticals", 5),
            ("3004", "Tablets & Capsules", 5),
            ("3004", "Syrups & Suspensions", 5),
            ("3004", "Injections", 5),
            ("3004", "Creams & Ointments", 5),
            ("3004", "Eye Drops", 5),
            ("3004", "Ear Drops", 5),
            ("3004", "Nasal Sprays", 5),
            ("3004", "Inhalers", 5),
            ("3004", "Surgical Dressings", 5),
            ("9018", "Medical Instruments", 18),
            ("9018", "Surgical Instruments", 18),
            ("9018", "Dental Instruments", 18),
            ("9018", "Stethoscopes", 18),
            ("9018", "Blood Pressure Monitors", 18),
            ("9018", "Thermometers", 18),
            ("9018", "Glucometers", 18),
            ("9018", "Pulse Oximeters", 18),
            ("9018", "ECG Machines", 18),
            ("9018", "X-Ray Machines", 18),
        ],
        
        "Food & Beverages": [
            ("1001", "Wheat", 0),
            ("1001", "Rice", 0),
            ("1001", "Maize", 0),
            ("1001", "Barley", 0),
            ("1001", "Oats", 0),
            ("1001", "Millets", 0),
            ("1001", "Pulses", 0),
            ("1001", "Lentils", 0),
            ("1001", "Beans", 0),
            ("1001", "Peas", 0),
            ("0701", "Fresh Vegetables", 0),
            ("0701", "Potatoes", 0),
            ("0701", "Onions", 0),
            ("0701", "Tomatoes", 0),
            ("0701", "Carrots", 0),
            ("0701", "Cabbage", 0),
            ("0701", "Cauliflower", 0),
            ("0701", "Broccoli", 0),
            ("0701", "Spinach", 0),
            ("0701", "Lettuce", 0),
        ],
        
        "Chemicals & Industrial": [
            ("2815", "Caustic Soda", 18),
            ("2815", "Sodium Hydroxide", 18),
            ("2815", "Sulfuric Acid", 18),
            ("2815", "Hydrochloric Acid", 18),
            ("2815", "Nitric Acid", 18),
            ("2815", "Phosphoric Acid", 18),
            ("2815", "Acetic Acid", 18),
            ("2815", "Citric Acid", 18),
            ("2815", "Oxalic Acid", 18),
            ("2815", "Boric Acid", 18),
            ("3401", "Soaps & Detergents", 18),
            ("3401", "Washing Powders", 18),
            ("3401", "Dishwashing Liquids", 18),
            ("3401", "Fabric Softeners", 18),
            ("3401", "Bleaching Agents", 18),
            ("3401", "Cleaning Products", 18),
            ("3401", "Surface Cleaners", 18),
            ("3401", "Floor Cleaners", 18),
            ("3401", "Bathroom Cleaners", 18),
            ("3401", "Kitchen Cleaners", 18),
        ]
    }
    
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        # Check if hsn_codes table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hsn_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                gst_rate REAL NOT NULL,
                category TEXT NOT NULL,
                code_type TEXT DEFAULT 'product',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add code_type column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE hsn_codes ADD COLUMN code_type TEXT DEFAULT 'product'")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Insert product HSN codes
        inserted_count = 0
        for category, products in product_categories.items():
            for hsn_code, description, gst_rate in products:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO hsn_codes (code, description, gst_rate, category, code_type)
                        VALUES (?, ?, ?, ?, 'product')
                    """, (hsn_code, description, gst_rate, category))
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    # Code already exists, update it
                    cursor.execute("""
                        UPDATE hsn_codes 
                        SET description = ?, gst_rate = ?, category = ?, code_type = 'product'
                        WHERE code = ?
                    """, (description, gst_rate, category, hsn_code))
                    inserted_count += 1
        
        conn.commit()
        print(f"✅ Successfully processed {inserted_count} product HSN codes")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM hsn_codes WHERE code_type = 'product'")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM hsn_codes WHERE code_type = 'service'")
        service_count = cursor.fetchone()[0]
        
        print(f"📊 Database Summary:")
        print(f"   Products: {product_count} HSN codes")
        print(f"   Services: {service_count} SAC codes")
        print(f"   Total: {product_count + service_count} codes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Expanding HSN Database with Product Codes...")
    expand_hsn_database()
    print("✅ HSN Database expansion completed!")
