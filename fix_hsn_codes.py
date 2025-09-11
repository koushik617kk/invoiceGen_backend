#!/usr/bin/env python3
"""
FIX HSN CODES - Remove artificial suffixes and use correct government HSN codes
The issue: We have 8517_001, 8517_002 instead of proper 8517, 8471, etc.
Solution: Use actual HSN codes and handle multiple products per HSN properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import HSNCode

def get_corrected_hsn_products():
    """
    Return products with CORRECT government HSN codes
    Multiple products can share the same HSN code - that's normal!
    """
    
    return [
        # ===== HSN 8517 - TELEPHONE EQUIPMENT =====
        {
            "code": "8517",
            "description": "Android Smartphones",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Phones",
            "keywords": "android,smartphone,mobile,phone,samsung,xiaomi,oneplus,realme",
            "tags": "mobile,smartphone,android",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "iPhones & Apple Smartphones",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Phones",
            "keywords": "iphone,apple,smartphone,ios,mobile",
            "tags": "mobile,smartphone,apple",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "Basic Feature Phones",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Phones",
            "keywords": "feature phone,basic phone,keypad phone,jio phone",
            "tags": "mobile,basic,phone",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "Mobile Phone Cases & Covers",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Accessories",
            "keywords": "mobile case,phone cover,back cover,flip cover,protection",
            "tags": "case,cover,accessory",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "Screen Protectors & Tempered Glass",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Accessories",
            "keywords": "screen protector,tempered glass,screen guard,mobile protection",
            "tags": "screen,protection,glass",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8517",
            "description": "Mobile Chargers & Power Banks",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Mobile_Accessories",
            "keywords": "mobile charger,power bank,fast charger,wireless charger,usb charger",
            "tags": "charger,power,battery",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 8471 - AUTOMATIC DATA PROCESSING MACHINES =====
        {
            "code": "8471",
            "description": "Gaming Laptops",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computers",
            "keywords": "gaming laptop,gaming computer,high performance laptop,graphics laptop",
            "tags": "laptop,gaming,computer",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Business Laptops",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computers",
            "keywords": "business laptop,office laptop,professional laptop,work laptop",
            "tags": "laptop,business,office",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Ultrabooks & Thin Laptops",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computers",
            "keywords": "ultrabook,thin laptop,lightweight laptop,portable laptop",
            "tags": "laptop,ultrabook,portable",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Desktop Computers & PCs",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computers",
            "keywords": "desktop computer,pc,desktop pc,computer system,tower pc",
            "tags": "desktop,computer,pc",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Computer Keyboards",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computer_Accessories",
            "keywords": "keyboard,computer keyboard,wireless keyboard,mechanical keyboard,gaming keyboard",
            "tags": "keyboard,input,computer",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Computer Mouse & Trackpads",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Computer_Accessories",
            "keywords": "computer mouse,wireless mouse,gaming mouse,optical mouse,trackpad",
            "tags": "mouse,input,computer",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Inkjet Printers",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Printers",
            "keywords": "inkjet printer,color printer,photo printer,home printer",
            "tags": "printer,inkjet,printing",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8471",
            "description": "Laser Printers",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Printers",
            "keywords": "laser printer,monochrome printer,office printer,fast printer",
            "tags": "printer,laser,office",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 8528 - RECEPTION APPARATUS FOR TV =====
        {
            "code": "8528",
            "description": "LED TVs",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Television",
            "keywords": "led tv,led television,flat screen tv,hd tv,full hd tv",
            "tags": "tv,led,television",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8528",
            "description": "Smart TVs",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Television",
            "keywords": "smart tv,internet tv,android tv,wifi tv,streaming tv",
            "tags": "tv,smart,internet",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8528",
            "description": "4K Ultra HD TVs",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Television",
            "keywords": "4k tv,ultra hd tv,uhd tv,high resolution tv",
            "tags": "tv,4k,uhd",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8528",
            "description": "Computer Monitors",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Monitors",
            "keywords": "computer monitor,lcd monitor,led monitor,display screen,pc monitor",
            "tags": "monitor,display,computer",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 8518 - MICROPHONES AND SPEAKERS =====
        {
            "code": "8518",
            "description": "Bluetooth Speakers",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Audio",
            "keywords": "bluetooth speaker,wireless speaker,portable speaker,music speaker",
            "tags": "speaker,bluetooth,audio",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8518",
            "description": "Wireless Headphones",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Audio",
            "keywords": "wireless headphones,bluetooth headphones,over ear headphones,noise cancelling",
            "tags": "headphones,wireless,audio",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8518",
            "description": "True Wireless Earbuds",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Audio",
            "keywords": "wireless earbuds,tws,true wireless,bluetooth earbuds,airpods",
            "tags": "earbuds,wireless,tws",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 8523 - STORAGE MEDIA =====
        {
            "code": "8523",
            "description": "USB Flash Drives",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Storage",
            "keywords": "usb drive,flash drive,pen drive,usb stick,portable storage",
            "tags": "usb,storage,flash",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8523",
            "description": "External Hard Drives",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Storage",
            "keywords": "external hard drive,portable hdd,backup drive,external storage",
            "tags": "storage,external,backup",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8523",
            "description": "Memory Cards & SD Cards",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Electronics",
            "subcategory": "Storage",
            "keywords": "memory card,sd card,micro sd,tf card,camera memory",
            "tags": "memory,card,storage",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 8708 - PARTS OF MOTOR VEHICLES =====
        {
            "code": "8708",
            "description": "Brake Pads & Brake Shoes",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Brake_System",
            "keywords": "brake pads,brake shoes,disc brake,drum brake,braking system",
            "tags": "brake,safety,parts",
            "unit": "Set",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "Clutch Plates & Clutch Assembly",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Transmission",
            "keywords": "clutch plate,clutch assembly,clutch disc,pressure plate",
            "tags": "clutch,transmission,parts",
            "unit": "Set",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "Shock Absorbers & Struts",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Suspension",
            "keywords": "shock absorber,struts,suspension,damper,car suspension",
            "tags": "suspension,shock,comfort",
            "unit": "Pair",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "Air Filters & Oil Filters",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Filters",
            "keywords": "air filter,oil filter,fuel filter,cabin filter,engine filter",
            "tags": "filter,engine,maintenance",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8708",
            "description": "Headlights & Tail Lights",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Lighting",
            "keywords": "headlight,tail light,car lights,led headlight,halogen light",
            "tags": "lights,headlight,safety",
            "unit": "Pair",
            "business_type": "product"
        },

        # ===== HSN 8507 - ELECTRIC ACCUMULATORS =====
        {
            "code": "8507",
            "description": "Car Batteries",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Electrical",
            "keywords": "car battery,automotive battery,12v battery,vehicle battery",
            "tags": "battery,electrical,power",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "8507",
            "description": "Two Wheeler Batteries",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Electrical",
            "keywords": "bike battery,motorcycle battery,scooter battery,two wheeler battery",
            "tags": "battery,bike,motorcycle",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 2710 - PETROLEUM OILS =====
        {
            "code": "2710",
            "description": "Engine Oil & Motor Oil",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Lubricants",
            "keywords": "engine oil,motor oil,synthetic oil,mineral oil,5w30,10w40",
            "tags": "oil,engine,lubricant",
            "unit": "Liters",
            "business_type": "product"
        },
        {
            "code": "2710",
            "description": "Gear Oil & Transmission Oil",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Lubricants",
            "keywords": "gear oil,transmission oil,differential oil,gearbox oil",
            "tags": "oil,gear,transmission",
            "unit": "Liters",
            "business_type": "product"
        },

        # ===== HSN 4011 - NEW PNEUMATIC TYRES =====
        {
            "code": "4011",
            "description": "Car Tyres",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Tyres",
            "keywords": "car tyre,car tire,tubeless tyre,radial tyre,passenger car tyre",
            "tags": "tyre,car,wheel",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "4011",
            "description": "Two Wheeler Tyres",
            "gst_rate": 28.0,
            "type": "HSN",
            "category": "Automotive",
            "subcategory": "Tyres",
            "keywords": "bike tyre,motorcycle tyre,scooter tyre,two wheeler tyre",
            "tags": "tyre,bike,motorcycle",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 6205 - MEN'S SHIRTS =====
        {
            "code": "6205",
            "description": "Men's Formal Shirts",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Men_Clothing",
            "keywords": "men shirt,formal shirt,office shirt,dress shirt,cotton shirt",
            "tags": "shirt,men,formal",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "6205",
            "description": "Men's Casual Shirts",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Men_Clothing",
            "keywords": "casual shirt,men casual,check shirt,printed shirt",
            "tags": "shirt,men,casual",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 6203 - MEN'S SUITS, TROUSERS =====
        {
            "code": "6203",
            "description": "Men's Formal Trousers",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Men_Clothing",
            "keywords": "formal trouser,men pant,office trouser,dress pant",
            "tags": "trouser,men,formal",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "6203",
            "description": "Men's Jeans",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Men_Clothing",
            "keywords": "men jeans,denim,casual jeans,blue jeans",
            "tags": "jeans,men,denim",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 6109 - T-SHIRTS, SINGLETS =====
        {
            "code": "6109",
            "description": "Men's T-Shirts",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Men_Clothing",
            "keywords": "t-shirt,tshirt,men tshirt,cotton tshirt,round neck,polo",
            "tags": "tshirt,men,casual",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 6204 - WOMEN'S SUITS, TROUSERS =====
        {
            "code": "6204",
            "description": "Women's Kurtis & Ethnic Wear",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Women_Clothing",
            "keywords": "kurti,women kurti,ethnic wear,indian wear,traditional",
            "tags": "kurti,women,ethnic",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "6204",
            "description": "Women's Formal Shirts & Tops",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Women_Clothing",
            "keywords": "women shirt,formal top,office wear,ladies shirt",
            "tags": "shirt,women,formal",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "6204",
            "description": "Women's Jeans & Trousers",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Women_Clothing",
            "keywords": "women jeans,ladies jeans,women trouser,denim",
            "tags": "jeans,women,trouser",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 6302 - BED LINEN, TABLE LINEN =====
        {
            "code": "6302",
            "description": "Bed Sheets & Bed Linen",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Home_Textiles",
            "keywords": "bed sheet,bed linen,double bed sheet,single bed sheet,cotton bed sheet",
            "tags": "bedsheet,home,linen",
            "unit": "Set",
            "business_type": "product"
        },
        {
            "code": "6302",
            "description": "Pillow Covers & Cushion Covers",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Home_Textiles",
            "keywords": "pillow cover,cushion cover,decorative cover,home decor",
            "tags": "pillow,cushion,home",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 5208 - WOVEN FABRICS OF COTTON =====
        {
            "code": "5208",
            "description": "Cotton Fabric & Cloth",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Textiles",
            "subcategory": "Fabrics",
            "keywords": "cotton fabric,cloth,cotton cloth,fabric material,textile",
            "tags": "fabric,cotton,cloth",
            "unit": "Meters",
            "business_type": "product"
        },

        # ===== HSN 3401 - SOAP =====
        {
            "code": "3401",
            "description": "Bath Soaps & Hand Soaps",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Personal_Care",
            "keywords": "soap,bath soap,hand soap,antibacterial soap,beauty soap",
            "tags": "soap,personal,hygiene",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "3401",
            "description": "Detergent Powder & Liquid",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Cleaning",
            "keywords": "detergent,washing powder,liquid detergent,laundry detergent",
            "tags": "detergent,cleaning,laundry",
            "unit": "Kg",
            "business_type": "product"
        },

        # ===== HSN 3305 - HAIR PREPARATIONS =====
        {
            "code": "3305",
            "description": "Shampoos & Hair Care",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Personal_Care",
            "keywords": "shampoo,hair oil,conditioner,hair care,anti dandruff",
            "tags": "shampoo,hair,care",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 3307 - SHAVING PREPARATIONS =====
        {
            "code": "3307",
            "description": "Toothpaste & Oral Care",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Personal_Care",
            "keywords": "toothpaste,toothbrush,mouthwash,oral care,dental care",
            "tags": "toothpaste,oral,dental",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 1006 - RICE =====
        {
            "code": "1006",
            "description": "Rice & Food Grains",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Food_Items",
            "keywords": "rice,basmati rice,food grain,wheat,dal,pulses",
            "tags": "rice,grain,food",
            "unit": "Kg",
            "business_type": "product"
        },

        # ===== HSN 1507 - SOYA-BEAN OIL =====
        {
            "code": "1507",
            "description": "Cooking Oil & Edible Oil",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "FMCG",
            "subcategory": "Food_Items",
            "keywords": "cooking oil,sunflower oil,mustard oil,coconut oil,edible oil",
            "tags": "oil,cooking,edible",
            "unit": "Liters",
            "business_type": "product"
        },

        # ===== HSN 3004 - MEDICAMENTS =====
        {
            "code": "3004",
            "description": "Pain Relief Medicines",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Pharmaceuticals",
            "subcategory": "Medicines",
            "keywords": "paracetamol,aspirin,pain relief,fever medicine,headache medicine",
            "tags": "medicine,pain,fever",
            "unit": "Strip",
            "business_type": "product"
        },
        {
            "code": "3004",
            "description": "Cold & Cough Medicines",
            "gst_rate": 12.0,
            "type": "HSN",
            "category": "Pharmaceuticals",
            "subcategory": "Medicines",
            "keywords": "cough syrup,cold medicine,throat medicine,respiratory medicine",
            "tags": "medicine,cough,cold",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 3005 - WADDING, GAUZE, BANDAGES =====
        {
            "code": "3005",
            "description": "Bandages & First Aid",
            "gst_rate": 12.0,
            "type": "HSN",
            "category": "Pharmaceuticals",
            "subcategory": "Medical_Supplies",
            "keywords": "bandage,first aid,cotton,gauze,medical supplies",
            "tags": "bandage,first aid,medical",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 9018 - MEDICAL INSTRUMENTS =====
        {
            "code": "9018",
            "description": "Medical Equipment",
            "gst_rate": 5.0,
            "type": "HSN",
            "category": "Pharmaceuticals",
            "subcategory": "Medical_Equipment",
            "keywords": "thermometer,bp machine,medical equipment,health monitor",
            "tags": "medical,equipment,health",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 4817 - ENVELOPES, LETTER CARDS =====
        {
            "code": "4817",
            "description": "A4 Paper & Office Paper",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Paper_Products",
            "keywords": "a4 paper,office paper,copier paper,printing paper",
            "tags": "paper,office,printing",
            "unit": "Ream",
            "business_type": "product"
        },
        {
            "code": "4817",
            "description": "Notebooks & Diaries",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Paper_Products",
            "keywords": "notebook,diary,writing pad,exercise book,spiral notebook",
            "tags": "notebook,diary,writing",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 9608 - BALL POINT PENS =====
        {
            "code": "9608",
            "description": "Ball Pens & Gel Pens",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Writing_Instruments",
            "keywords": "ball pen,gel pen,blue pen,black pen,writing pen",
            "tags": "pen,writing,office",
            "unit": "Nos",
            "business_type": "product"
        },
        {
            "code": "9608",
            "description": "Pencils & Mechanical Pencils",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Writing_Instruments",
            "keywords": "pencil,mechanical pencil,hb pencil,drawing pencil",
            "tags": "pencil,writing,drawing",
            "unit": "Nos",
            "business_type": "product"
        },

        # ===== HSN 9609 - PENCILS, CRAYONS =====
        {
            "code": "9609",
            "description": "Erasers & Sharpeners",
            "gst_rate": 18.0,
            "type": "HSN",
            "category": "Stationery",
            "subcategory": "Writing_Instruments",
            "keywords": "eraser,rubber,sharpener,pencil sharpener",
            "tags": "eraser,sharpener,stationery",
            "unit": "Nos",
            "business_type": "product"
        }
    ]

def fix_hsn_codes():
    """Clear database and rebuild with correct HSN codes"""
    
    print("🔧 FIXING HSN CODES - REMOVING ARTIFICIAL SUFFIXES")
    print("=" * 60)
    print("❌ PROBLEM: HSN codes like 8517_001, 8471_002 (WRONG!)")
    print("✅ SOLUTION: Use actual government HSN codes: 8517, 8471, 8528")
    print("💡 APPROACH: Multiple products can share same HSN - that's normal!")
    print()
    
    db = SessionLocal()
    
    try:
        # Count current problematic codes
        current_count = db.query(HSNCode).count()
        problematic_count = db.query(HSNCode).filter(HSNCode.code.like('%_%')).count()
        
        print(f"📊 Current HSN codes: {current_count}")
        print(f"⚠️  Problematic codes with suffixes: {problematic_count}")
        
        # Clear all existing HSN codes
        print(f"\n🗑️  Clearing all existing HSN codes...")
        db.query(HSNCode).delete()
        db.commit()
        print("✅ Database cleared")
        
        # Add corrected products
        products_data = get_corrected_hsn_products()
        
        added_count = 0
        
        print(f"\n🔄 Adding {len(products_data)} products with CORRECT HSN codes...")
        
        for product_data in products_data:
            try:
                product = HSNCode(**product_data)
                db.add(product)
                db.commit()
                added_count += 1
                print(f"✅ Added: {product_data['description']} (HSN: {product_data['code']})")
            except Exception as e:
                db.rollback()
                print(f"⚠️  Skipped: {product_data['description']} - {str(e)[:100]}")
                continue
        
        final_count = db.query(HSNCode).count()
        
        print(f"\n🎉 HSN CODES FIXED SUCCESSFULLY!")
        print(f"📈 Added: {added_count} products with correct HSN codes")
        print(f"📊 Total HSN codes now: {final_count}")
        
        # Verify fix - check for any remaining problematic codes
        remaining_problematic = db.query(HSNCode).filter(HSNCode.code.like('%_%')).count()
        print(f"✅ Problematic codes remaining: {remaining_problematic} (should be 0)")
        
        # Show sample corrected codes
        print(f"\n💡 SAMPLE CORRECTED HSN CODES:")
        sample_codes = db.query(HSNCode).limit(8).all()
        for hsn in sample_codes:
            print(f"   ✅ HSN {hsn.code}: {hsn.description}")
        
    except Exception as e:
        print(f"❌ Error fixing HSN codes: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_hsn_codes()
