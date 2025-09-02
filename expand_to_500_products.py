#!/usr/bin/env python3
"""
Expand to 500 High-Quality HSN Product Codes
This script adds more products to reach the full 500 count
"""

import sqlite3
from datetime import datetime

# Database path
DB_PATH = "invoiceGen.db"

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def add_more_products():
    """Add more products to reach 500"""
    
    # Additional high-quality products
    additional_products = [
        # More Electronics & IT
        {"code": "8471", "description": "Gaming computers, gaming laptops", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Gaming"},
        {"code": "8471", "description": "Workstations, server computers", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Servers"},
        {"code": "8471", "description": "All-in-one computers", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Computers"},
        {"code": "8528", "description": "4K monitors, ultra-wide displays", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Displays"},
        {"code": "8528", "description": "Projectors, home theater projectors", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Projectors"},
        {"code": "8518", "description": "Bluetooth speakers, wireless speakers", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Audio"},
        {"code": "8518", "description": "Soundbars, home theater systems", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Audio"},
        {"code": "8519", "description": "Wireless headphones, earbuds", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Audio"},
        {"code": "8519", "description": "Gaming headsets, studio headphones", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Audio"},
        {"code": "8521", "description": "Action cameras, GoPro cameras", "gst_rate": 18.0, "category": "Electronics", "subcategory": "Cameras"},
        
        # More Textiles & Clothing
        {"code": "6204", "description": "Business suits, formal wear", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Formal Wear"},
        {"code": "6204", "description": "Party wear, evening dresses", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Party Wear"},
        {"code": "6205", "description": "Casual shirts, polo shirts", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Casual Wear"},
        {"code": "6205", "description": "Dress shirts, formal shirts", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Formal Wear"},
        {"code": "6206", "description": "Casual blouses, tunic tops", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Casual Wear"},
        {"code": "6208", "description": "Cocktail dresses, party dresses", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Party Wear"},
        {"code": "6208", "description": "Bridal wear, wedding dresses", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Bridal Wear"},
        {"code": "6104", "description": "Kurtis, ethnic wear", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Ethnic Wear"},
        {"code": "6104", "description": "Sarees, traditional wear", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Traditional Wear"},
        {"code": "6105", "description": "Kurtas, ethnic shirts", "gst_rate": 5.0, "category": "Textiles", "subcategory": "Ethnic Wear"},
        
        # More Food & Beverages
        {"code": "1006", "description": "Brown rice, organic rice", "gst_rate": 5.0, "category": "Food", "subcategory": "Organic Foods"},
        {"code": "1001", "description": "Organic wheat, whole wheat", "gst_rate": 0.0, "category": "Food", "subcategory": "Organic Foods"},
        {"code": "1005", "description": "Sweet corn, baby corn", "gst_rate": 0.0, "category": "Food", "subcategory": "Vegetables"},
        {"code": "1101", "description": "Whole wheat flour, multigrain flour", "gst_rate": 0.0, "category": "Food", "subcategory": "Health Foods"},
        {"code": "1102", "description": "Brown rice flour, organic flour", "gst_rate": 5.0, "category": "Food", "subcategory": "Organic Foods"},
        {"code": "2008", "description": "Dry fruits, raisins, dates", "gst_rate": 5.0, "category": "Food", "subcategory": "Dry Fruits"},
        {"code": "2008", "description": "Seeds, sunflower seeds, pumpkin seeds", "gst_rate": 5.0, "category": "Food", "subcategory": "Seeds"},
        {"code": "2009", "description": "Fresh fruit juices, smoothies", "gst_rate": 12.0, "category": "Food", "subcategory": "Fresh Juices"},
        {"code": "2009", "description": "Energy drinks, sports drinks", "gst_rate": 28.0, "category": "Food", "subcategory": "Energy Drinks"},
        {"code": "2202", "description": "Mineral water, packaged water", "gst_rate": 18.0, "category": "Food", "subcategory": "Bottled Water"},
        
        # More Automotive
        {"code": "8708", "description": "Car audio systems, stereos", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Audio Systems"},
        {"code": "8708", "description": "GPS navigation, car GPS", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Navigation"},
        {"code": "8708", "description": "Car covers, seat covers", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Accessories"},
        {"code": "8708", "description": "Car perfumes, air fresheners", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Accessories"},
        {"code": "8708", "description": "Car chargers, phone holders", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Accessories"},
        {"code": "8708", "description": "Dash cameras, rear view cameras", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Cameras"},
        {"code": "8708", "description": "Car alarms, security systems", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Security"},
        {"code": "8708", "description": "Car wash products, cleaners", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Cleaning"},
        {"code": "8708", "description": "Car tools, emergency kits", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Tools"},
        {"code": "8708", "description": "Car lighting, LED lights", "gst_rate": 28.0, "category": "Automotive", "subcategory": "Lighting"},
        
        # More Construction
        {"code": "2505", "description": "White cement, colored cement", "gst_rate": 28.0, "category": "Construction", "subcategory": "Specialty Cement"},
        {"code": "2506", "description": "Hydrated lime, slaked lime", "gst_rate": 18.0, "category": "Construction", "subcategory": "Lime"},
        {"code": "2517", "description": "River sand, manufactured sand", "gst_rate": 5.0, "category": "Construction", "subcategory": "Sand"},
        {"code": "2515", "description": "Tiles, ceramic tiles", "gst_rate": 18.0, "category": "Construction", "subcategory": "Tiles"},
        {"code": "2515", "description": "Vitrified tiles, porcelain tiles", "gst_rate": 18.0, "category": "Construction", "subcategory": "Tiles"},
        {"code": "2516", "description": "Construction sand, fine sand", "gst_rate": 5.0, "category": "Construction", "subcategory": "Sand"},
        {"code": "2517", "description": "Coarse aggregate, fine aggregate", "gst_rate": 5.0, "category": "Construction", "subcategory": "Aggregates"},
        {"code": "2518", "description": "Building stones, construction stones", "gst_rate": 18.0, "category": "Construction", "subcategory": "Stones"},
        {"code": "2520", "description": "Plaster of Paris, POP", "gst_rate": 18.0, "category": "Construction", "subcategory": "Plaster"},
        {"code": "2523", "description": "Portland cement clinker", "gst_rate": 28.0, "category": "Construction", "subcategory": "Cement"},
        
        # More Healthcare
        {"code": "3004", "description": "Antibiotics, painkillers", "gst_rate": 12.0, "category": "Healthcare", "subcategory": "Medicines"},
        {"code": "3004", "description": "Vitamins, supplements", "gst_rate": 12.0, "category": "Healthcare", "subcategory": "Supplements"},
        {"code": "3004", "description": "First aid kits, medical kits", "gst_rate": 12.0, "category": "Healthcare", "subcategory": "First Aid"},
        {"code": "3004", "description": "Disposable gloves, masks", "gst_rate": 12.0, "category": "Healthcare", "subcategory": "Medical Supplies"},
        {"code": "3004", "description": "Digital thermometers, infrared thermometers", "gst_rate": 18.0, "category": "Healthcare", "subcategory": "Medical Devices"},
        {"code": "3004", "description": "Blood pressure monitors, pulse oximeters", "gst_rate": 18.0, "category": "Healthcare", "subcategory": "Medical Devices"},
        {"code": "3004", "description": "Weighing scales, body composition analyzers", "gst_rate": 18.0, "category": "Healthcare", "subcategory": "Medical Devices"},
        {"code": "3004", "description": "Walking sticks, canes", "gst_rate": 18.0, "category": "Healthcare", "subcategory": "Mobility Aids"},
        {"code": "3004", "description": "Patient monitors, ECG machines", "gst_rate": 18.0, "category": "Healthcare", "subcategory": "Medical Devices"},
        {"code": "3004", "description": "Oxygen concentrators, nebulizers", "gst_rate": 18.0, "category": "Healthcare", "subcategory": "Medical Devices"},
        
        # More Chemicals
        {"code": "2815", "description": "Ammonium hydroxide, ammonia", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Ammonia"},
        {"code": "2815", "description": "Calcium hydroxide, slaked lime", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Alkalis"},
        {"code": "2811", "description": "Phosphoric acid, orthophosphoric acid", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Acids"},
        {"code": "2811", "description": "Acetic acid, glacial acetic acid", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Acids"},
        {"code": "2811", "description": "Citric acid, food grade citric acid", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Acids"},
        {"code": "2825", "description": "Aluminum sulfate, alum", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Salts"},
        {"code": "2825", "description": "Magnesium sulfate, Epsom salt", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Salts"},
        {"code": "2825", "description": "Sodium chloride, table salt", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Salts"},
        {"code": "2833", "description": "Sodium bicarbonate, baking soda", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Carbonates"},
        {"code": "2833", "description": "Potassium carbonate, potash", "gst_rate": 18.0, "category": "Chemicals", "subcategory": "Carbonates"},
        
        # More Machinery
        {"code": "8429", "description": "Loaders, backhoe loaders", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Construction Equipment"},
        {"code": "8429", "description": "Motor graders, road graders", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Road Equipment"},
        {"code": "8429", "description": "Rollers, compactors", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Compaction Equipment"},
        {"code": "8430", "description": "Pile drivers, foundation equipment", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Foundation Equipment"},
        {"code": "8430", "description": "Tunnel boring machines, TBMs", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Tunneling Equipment"},
        {"code": "8431", "description": "Submersible pumps, deep well pumps", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Pumps"},
        {"code": "8431", "description": "Screw compressors, reciprocating compressors", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Compressors"},
        {"code": "8431", "description": "Centrifugal fans, axial fans", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Ventilation"},
        {"code": "8431", "description": "Bag filters, cartridge filters", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Filtration"},
        {"code": "8431", "description": "Ball valves, gate valves, butterfly valves", "gst_rate": 18.0, "category": "Machinery", "subcategory": "Valves"},
        
        # More Others
        {"code": "4819", "description": "Gift boxes, luxury packaging", "gst_rate": 18.0, "category": "Packaging", "subcategory": "Luxury Packaging"},
        {"code": "4819", "description": "Corrugated boxes, shipping boxes", "gst_rate": 18.0, "category": "Packaging", "subcategory": "Shipping"},
        {"code": "4819", "description": "Bubble wrap, packing materials", "gst_rate": 18.0, "category": "Packaging", "subcategory": "Protective Materials"},
        {"code": "4820", "description": "Art supplies, painting materials", "gst_rate": 18.0, "category": "Stationery", "subcategory": "Art Supplies"},
        {"code": "4820", "description": "Office supplies, desk organizers", "gst_rate": 18.0, "category": "Stationery", "subcategory": "Office Supplies"},
        {"code": "4820", "description": "Educational materials, charts", "gst_rate": 18.0, "category": "Stationery", "subcategory": "Educational"},
        {"code": "4820", "description": "Craft supplies, DIY materials", "gst_rate": 18.0, "category": "Stationery", "subcategory": "Craft Supplies"},
        {"code": "4820", "description": "Drawing instruments, rulers", "gst_rate": 18.0, "category": "Stationery", "subcategory": "Drawing Tools"},
        {"code": "4820", "description": "Storage solutions, cabinets", "gst_rate": 18.0, "category": "Stationery", "subcategory": "Storage"},
        {"code": "4820", "description": "Presentation materials, boards", "gst_rate": 18.0, "category": "Stationery", "subcategory": "Presentation"}
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    added_count = 0
    
    for product in additional_products:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO hsn_codes 
                (code, description, gst_rate, type, category, subcategory, unit, business_type, is_active, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product["code"],
                product["description"],
                product["gst_rate"],
                "HSN",
                product["category"],
                product["subcategory"],
                "Nos",
                "B2C",
                1,
                "expand_to_500_products",
                datetime.now(),
                datetime.now()
            ))
            added_count += 1
        except Exception as e:
            print(f"Error adding product {product['description']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"Successfully added {added_count} additional products!")
    return added_count

if __name__ == "__main__":
    print("Expanding to 500 high-quality HSN product codes...")
    count = add_more_products()
    print(f"Completed! Added {count} additional products.")
