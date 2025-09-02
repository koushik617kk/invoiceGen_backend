#!/usr/bin/env python3
"""
Create Master Products Table and Populate with Common Products
This script creates the master_products table and adds common products for product businesses.
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "invoice_gen.db"

def create_connection():
    """Create database connection"""
    return sqlite3.connect(DB_PATH)

def create_master_products():
    """Create master_products table and populate with common products"""
    
    # Common products by category
    common_products = {
        "Electronics & IT": [
            ("Laptop Computer", "8471", 18, "High-performance laptop for business and gaming", "Nos", 45000),
            ("Smartphone", "8517", 18, "Latest smartphone with advanced features", "Nos", 25000),
            ("Wireless Headphones", "8519", 18, "Bluetooth noise-cancelling headphones", "Nos", 5000),
            ("USB Cable", "8544", 18, "High-speed USB-C charging cable", "Nos", 200),
            ("Power Bank", "8507", 18, "10000mAh portable charger", "Nos", 1500),
            ("Mouse", "8471", 18, "Wireless optical mouse", "Nos", 800),
            ("Keyboard", "8471", 18, "Mechanical gaming keyboard", "Nos", 3000),
            ("Monitor", "8528", 18, "24-inch LED monitor", "Nos", 12000),
            ("Webcam", "8525", 18, "HD webcam for video calls", "Nos", 2500),
            ("Router", "8517", 18, "WiFi 6 wireless router", "Nos", 4000),
        ],
        
        "Textiles & Apparel": [
            ("Cotton T-Shirt", "6104", 5, "100% cotton comfortable t-shirt", "Nos", 500),
            ("Denim Jeans", "6103", 5, "Classic blue denim jeans", "Nos", 1200),
            ("Formal Shirt", "6103", 5, "Business formal shirt", "Nos", 800),
            ("Dress", "6104", 5, "Elegant party dress", "Nos", 1500),
            ("Sweater", "6110", 5, "Warm woolen sweater", "Nos", 2000),
            ("Bed Sheet", "6302", 5, "Cotton bed sheet set", "Nos", 800),
            ("Curtains", "6303", 5, "Elegant window curtains", "Nos", 1200),
            ("Towels", "6302", 5, "Soft cotton towels", "Nos", 300),
            ("Saree", "6104", 5, "Traditional silk saree", "Nos", 5000),
            ("Kurta", "6103", 5, "Traditional Indian kurta", "Nos", 1000),
        ],
        
        "Furniture & Home": [
            ("Office Chair", "9401", 18, "Ergonomic office chair", "Nos", 8000),
            ("Dining Table", "9403", 18, "6-seater wooden dining table", "Nos", 25000),
            ("Sofa Set", "9401", 18, "3-seater comfortable sofa", "Nos", 35000),
            ("Bed Frame", "9401", 18, "Queen size bed frame", "Nos", 15000),
            ("Wardrobe", "9401", 18, "Large wooden wardrobe", "Nos", 20000),
            ("Bookshelf", "9401", 18, "5-shelf wooden bookshelf", "Nos", 8000),
            ("TV Unit", "9401", 18, "Modern TV stand unit", "Nos", 12000),
            ("Coffee Table", "9403", 18, "Glass top coffee table", "Nos", 8000),
            ("Study Table", "9403", 18, "Student study table", "Nos", 5000),
            ("Kitchen Cabinet", "9401", 18, "Modular kitchen cabinet", "Nos", 18000),
        ],
        
        "Automotive & Transport": [
            ("Car Battery", "8507", 18, "12V car battery", "Nos", 5000),
            ("Tire", "4011", 18, "All-season car tire", "Nos", 4000),
            ("Brake Pad", "8708", 18, "Ceramic brake pads", "Nos", 2000),
            ("Air Filter", "8421", 18, "Engine air filter", "Nos", 500),
            ("Oil Filter", "8421", 18, "Engine oil filter", "Nos", 300),
            ("Spark Plug", "8511", 18, "Iridium spark plug", "Nos", 400),
            ("Car Seat Cover", "8708", 18, "Leather car seat cover", "Nos", 3000),
            ("Floor Mat", "8708", 18, "Rubber car floor mat", "Nos", 800),
            ("Steering Wheel Cover", "8708", 18, "Leather steering cover", "Nos", 500),
            ("Car Audio System", "8518", 18, "Bluetooth car stereo", "Nos", 8000),
        ],
        
        "Construction & Building": [
            ("Portland Cement", "2505", 28, "OPC 53 grade cement", "Bags", 350),
            ("Steel Bars", "7214", 18, "TMT steel bars", "Ton", 45000),
            ("Bricks", "6802", 5, "Clay bricks", "Nos", 8),
            ("Sand", "2505", 5, "River sand", "Cubic Meter", 1200),
            ("Aggregate", "2517", 5, "20mm aggregate", "Cubic Meter", 800),
            ("Tiles", "6907", 18, "Vitrified floor tiles", "Sq Meter", 120),
            ("Paint", "3208", 18, "Interior wall paint", "Liters", 400),
            ("Plywood", "4412", 18, "Commercial plywood", "Sq Feet", 45),
            ("Steel Door", "7308", 18, "Security steel door", "Nos", 15000),
            ("Window Frame", "7610", 18, "Aluminum window frame", "Nos", 8000),
        ],
        
        "Healthcare & Medical": [
            ("Paracetamol Tablets", "3004", 5, "500mg pain relief tablets", "Strip", 50),
            ("Vitamin C", "3004", 5, "1000mg vitamin C tablets", "Bottle", 200),
            ("Bandage", "3005", 5, "Cotton bandage roll", "Roll", 30),
            ("Thermometer", "9025", 18, "Digital thermometer", "Nos", 500),
            ("Blood Pressure Monitor", "9018", 18, "Digital BP monitor", "Nos", 3000),
            ("Stethoscope", "9018", 18, "Professional stethoscope", "Nos", 2000),
            ("First Aid Kit", "3006", 18, "Complete first aid kit", "Nos", 800),
            ("Face Mask", "6307", 5, "3-ply surgical mask", "Box", 100),
            ("Hand Sanitizer", "3808", 18, "500ml hand sanitizer", "Bottle", 150),
            ("Glucometer", "9018", 18, "Blood glucose monitor", "Nos", 1500),
        ],
        
        "Food & Beverages": [
            ("Basmati Rice", "1006", 0, "Premium basmati rice", "Kg", 120),
            ("Wheat Flour", "1101", 0, "Whole wheat flour", "Kg", 40),
            ("Sugar", "1701", 0, "Refined white sugar", "Kg", 45),
            ("Cooking Oil", "1507", 0, "Refined sunflower oil", "Liter", 140),
            ("Tea", "0902", 0, "Premium black tea", "Kg", 300),
            ("Coffee", "0901", 0, "Ground coffee beans", "Kg", 400),
            ("Milk", "0401", 0, "Fresh cow milk", "Liter", 60),
            ("Bread", "1905", 0, "Fresh white bread", "Loaf", 30),
            ("Eggs", "0407", 0, "Fresh farm eggs", "Dozen", 80),
            ("Butter", "0405", 0, "Unsalted butter", "Kg", 600),
        ],
        
        "Chemicals & Industrial": [
            ("Washing Powder", "3402", 18, "Detergent washing powder", "Kg", 120),
            ("Dish Soap", "3401", 18, "Liquid dish soap", "Liter", 80),
            ("Bleach", "2828", 18, "Sodium hypochlorite bleach", "Liter", 60),
            ("Acid Cleaner", "3402", 18, "Industrial acid cleaner", "Liter", 200),
            ("Lubricating Oil", "2710", 18, "Engine lubricating oil", "Liter", 400),
            ("Adhesive", "3506", 18, "Industrial adhesive", "Kg", 300),
            ("Paint Thinner", "3814", 18, "Paint thinner solvent", "Liter", 150),
            ("Industrial Gloves", "4015", 18, "Safety work gloves", "Pair", 50),
            ("Safety Helmet", "6506", 18, "Industrial safety helmet", "Nos", 200),
            ("Work Boots", "6403", 18, "Steel toe work boots", "Pair", 1200),
        ]
    }
    
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        # Create master_products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hsn_code TEXT NOT NULL,
                gst_rate REAL NOT NULL,
                description TEXT,
                unit TEXT DEFAULT 'Nos',
                typical_price REAL,
                category TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert common products
        inserted_count = 0
        for category, products in common_products.items():
            for name, hsn_code, gst_rate, description, unit, typical_price in products:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO master_products 
                        (name, hsn_code, gst_rate, description, unit, typical_price, category)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name, hsn_code, gst_rate, description, unit, typical_price, category))
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    # Product already exists, update it
                    cursor.execute("""
                        UPDATE master_products 
                        SET hsn_code = ?, gst_rate = ?, description = ?, unit = ?, 
                            typical_price = ?, category = ?
                        WHERE name = ?
                    """, (hsn_code, gst_rate, description, unit, typical_price, category, name))
                    inserted_count += 1
        
        conn.commit()
        print(f"✅ Successfully processed {inserted_count} master products")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM master_products")
        total_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT category, COUNT(*) FROM master_products GROUP BY category")
        category_counts = cursor.fetchall()
        
        print(f"📊 Master Products Summary:")
        print(f"   Total Products: {total_products}")
        print(f"   Categories:")
        for category, count in category_counts:
            print(f"     {category}: {count} products")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Creating Master Products Database...")
    create_master_products()
    print("✅ Master Products Database created successfully!")
