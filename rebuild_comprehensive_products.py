#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCT DATABASE REBUILD
Creates a complete product catalog with SMART SPECIFICITY
- Not too generic (like "Electronic Equipment") 
- Not too specific (like "iPhone 14 Pro Max 256GB Purple")
- Just right (like "Smartphones", "Gaming Laptops", "LED TVs")
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import HSNCode

def get_comprehensive_products_data():
    """
    COMPREHENSIVE product database with SMART SPECIFICITY
    Each category has ALL major subcategories/product types
    """
    
    return [
        # ===== ELECTRONICS & IT HARDWARE =====
        
        # Mobile Phones & Communication (HSN 8517)
        {
            "code": "8517_001", "description": "Android Smartphones",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Mobile_Phones",
            "keywords": "android,smartphone,mobile,phone,samsung,xiaomi,oneplus,realme", "tags": "mobile,smartphone,android",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8517_002", "description": "iPhones & Apple Smartphones", 
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Mobile_Phones",
            "keywords": "iphone,apple,smartphone,ios,mobile", "tags": "mobile,smartphone,apple",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8517_003", "description": "Basic Feature Phones",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Mobile_Phones", 
            "keywords": "feature phone,basic phone,keypad phone,jio phone", "tags": "mobile,basic,phone",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8517_004", "description": "Mobile Phone Cases & Covers",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Mobile_Accessories",
            "keywords": "mobile case,phone cover,back cover,flip cover,protection", "tags": "case,cover,accessory",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8517_005", "description": "Screen Protectors & Tempered Glass",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Mobile_Accessories",
            "keywords": "screen protector,tempered glass,screen guard,mobile protection", "tags": "screen,protection,glass",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8517_006", "description": "Mobile Chargers & Power Banks",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Mobile_Accessories",
            "keywords": "mobile charger,power bank,fast charger,wireless charger,usb charger", "tags": "charger,power,battery",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8517_007", "description": "Earphones & Mobile Headsets",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Audio_Accessories",
            "keywords": "earphones,headphones,mobile headset,wired earphones,bluetooth earphones", "tags": "earphones,audio,headset",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8517_008", "description": "Data Cables & USB Cables",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Mobile_Accessories",
            "keywords": "data cable,usb cable,type-c cable,lightning cable,micro usb", "tags": "cable,usb,data",
            "unit": "Nos", "business_type": "product"
        },

        # Computers & Laptops (HSN 8471)
        {
            "code": "8471_001", "description": "Gaming Laptops",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Computers",
            "keywords": "gaming laptop,gaming computer,high performance laptop,graphics laptop", "tags": "laptop,gaming,computer",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_002", "description": "Business Laptops",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Computers",
            "keywords": "business laptop,office laptop,professional laptop,work laptop", "tags": "laptop,business,office",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_003", "description": "Ultrabooks & Thin Laptops",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Computers",
            "keywords": "ultrabook,thin laptop,lightweight laptop,portable laptop", "tags": "laptop,ultrabook,portable",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_004", "description": "2-in-1 Convertible Laptops",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Computers",
            "keywords": "2-in-1 laptop,convertible laptop,touchscreen laptop,hybrid laptop", "tags": "laptop,convertible,touchscreen",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_005", "description": "Desktop Computers & PCs",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Computers",
            "keywords": "desktop computer,pc,desktop pc,computer system,tower pc", "tags": "desktop,computer,pc",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_006", "description": "All-in-One Computers",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Computers",
            "keywords": "all-in-one computer,aio pc,integrated computer,space saving computer", "tags": "computer,aio,integrated",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_007", "description": "Computer Keyboards",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Computer_Accessories",
            "keywords": "keyboard,computer keyboard,wireless keyboard,mechanical keyboard,gaming keyboard", "tags": "keyboard,input,computer",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_008", "description": "Computer Mouse & Trackpads",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Computer_Accessories",
            "keywords": "computer mouse,wireless mouse,gaming mouse,optical mouse,trackpad", "tags": "mouse,input,computer",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_009", "description": "Inkjet Printers",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Printers",
            "keywords": "inkjet printer,color printer,photo printer,home printer", "tags": "printer,inkjet,printing",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_010", "description": "Laser Printers",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Printers",
            "keywords": "laser printer,monochrome printer,office printer,fast printer", "tags": "printer,laser,office",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_011", "description": "Multifunction Printers (MFP)",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Printers",
            "keywords": "mfp,multifunction printer,all-in-one printer,printer scanner copier", "tags": "printer,mfp,scanner",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8471_012", "description": "Document Scanners",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Office_Equipment",
            "keywords": "scanner,document scanner,flatbed scanner,sheet fed scanner", "tags": "scanner,document,office",
            "unit": "Nos", "business_type": "product"
        },

        # TVs & Displays (HSN 8528)
        {
            "code": "8528_001", "description": "LED TVs",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Television",
            "keywords": "led tv,led television,flat screen tv,hd tv,full hd tv", "tags": "tv,led,television",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8528_002", "description": "Smart TVs",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Television",
            "keywords": "smart tv,internet tv,android tv,wifi tv,streaming tv", "tags": "tv,smart,internet",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8528_003", "description": "4K Ultra HD TVs",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Television",
            "keywords": "4k tv,ultra hd tv,uhd tv,high resolution tv", "tags": "tv,4k,uhd",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8528_004", "description": "OLED TVs",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Television",
            "keywords": "oled tv,organic led tv,premium tv,high contrast tv", "tags": "tv,oled,premium",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8528_005", "description": "Computer Monitors",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Monitors",
            "keywords": "computer monitor,lcd monitor,led monitor,display screen,pc monitor", "tags": "monitor,display,computer",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8528_006", "description": "Gaming Monitors",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Monitors",
            "keywords": "gaming monitor,high refresh monitor,gaming display,144hz monitor", "tags": "monitor,gaming,display",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8528_007", "description": "Projectors",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Projectors",
            "keywords": "projector,presentation projector,home theater projector,lcd projector", "tags": "projector,display,presentation",
            "unit": "Nos", "business_type": "product"
        },

        # Audio & Entertainment (HSN 8518)
        {
            "code": "8518_001", "description": "Bluetooth Speakers",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Audio",
            "keywords": "bluetooth speaker,wireless speaker,portable speaker,music speaker", "tags": "speaker,bluetooth,audio",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8518_002", "description": "Home Theater Systems",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Audio",
            "keywords": "home theater,surround sound,5.1 speaker,audio system", "tags": "theater,audio,surround",
            "unit": "Set", "business_type": "product"
        },
        {
            "code": "8518_003", "description": "Soundbars",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Audio",
            "keywords": "soundbar,tv speaker,audio bar,sound system", "tags": "soundbar,tv,audio",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8518_004", "description": "Wireless Headphones",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Audio",
            "keywords": "wireless headphones,bluetooth headphones,over ear headphones,noise cancelling", "tags": "headphones,wireless,audio",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8518_005", "description": "True Wireless Earbuds",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Audio",
            "keywords": "wireless earbuds,tws,true wireless,bluetooth earbuds,airpods", "tags": "earbuds,wireless,tws",
            "unit": "Nos", "business_type": "product"
        },

        # Storage & Memory (HSN 8523)
        {
            "code": "8523_001", "description": "USB Flash Drives",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Storage",
            "keywords": "usb drive,flash drive,pen drive,usb stick,portable storage", "tags": "usb,storage,flash",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8523_002", "description": "External Hard Drives",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Storage",
            "keywords": "external hard drive,portable hdd,backup drive,external storage", "tags": "storage,external,backup",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8523_003", "description": "SSD Drives",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Storage",
            "keywords": "ssd,solid state drive,fast storage,internal ssd,external ssd", "tags": "ssd,storage,fast",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8523_004", "description": "Memory Cards & SD Cards",
            "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Storage",
            "keywords": "memory card,sd card,micro sd,tf card,camera memory", "tags": "memory,card,storage",
            "unit": "Nos", "business_type": "product"
        },

        # ===== AUTOMOTIVE PARTS =====
        
        # Engine Parts (HSN 8708)
        {
            "code": "8708_001", "description": "Brake Pads & Brake Shoes",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Brake_System",
            "keywords": "brake pads,brake shoes,disc brake,drum brake,braking system", "tags": "brake,safety,parts",
            "unit": "Set", "business_type": "product"
        },
        {
            "code": "8708_002", "description": "Clutch Plates & Clutch Assembly",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Transmission",
            "keywords": "clutch plate,clutch assembly,clutch disc,pressure plate", "tags": "clutch,transmission,parts",
            "unit": "Set", "business_type": "product"
        },
        {
            "code": "8708_003", "description": "Shock Absorbers & Struts",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Suspension",
            "keywords": "shock absorber,struts,suspension,damper,car suspension", "tags": "suspension,shock,comfort",
            "unit": "Pair", "business_type": "product"
        },
        {
            "code": "8708_004", "description": "Air Filters & Oil Filters",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Filters",
            "keywords": "air filter,oil filter,fuel filter,cabin filter,engine filter", "tags": "filter,engine,maintenance",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8708_005", "description": "Headlights & Tail Lights",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Lighting",
            "keywords": "headlight,tail light,car lights,led headlight,halogen light", "tags": "lights,headlight,safety",
            "unit": "Pair", "business_type": "product"
        },
        {
            "code": "8708_006", "description": "Bumpers & Body Parts",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Body_Parts",
            "keywords": "bumper,body parts,car body,front bumper,rear bumper", "tags": "body,bumper,exterior",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8708_007", "description": "Seat Covers & Interior Accessories",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Interior",
            "keywords": "seat cover,floor mat,dashboard cover,interior accessories", "tags": "interior,seat,accessories",
            "unit": "Set", "business_type": "product"
        },
        {
            "code": "8708_008", "description": "Side Mirrors & Door Handles",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Exterior_Parts",
            "keywords": "side mirror,door handle,exterior mirror,car mirror", "tags": "mirror,door,exterior",
            "unit": "Nos", "business_type": "product"
        },

        # Batteries & Fluids
        {
            "code": "8507_001", "description": "Car Batteries",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Electrical",
            "keywords": "car battery,automotive battery,12v battery,vehicle battery", "tags": "battery,electrical,power",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8507_002", "description": "Two Wheeler Batteries",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Electrical",
            "keywords": "bike battery,motorcycle battery,scooter battery,two wheeler battery", "tags": "battery,bike,motorcycle",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "2710_001", "description": "Engine Oil & Motor Oil",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Lubricants",
            "keywords": "engine oil,motor oil,synthetic oil,mineral oil,5w30,10w40", "tags": "oil,engine,lubricant",
            "unit": "Liters", "business_type": "product"
        },
        {
            "code": "2710_002", "description": "Gear Oil & Transmission Oil",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Lubricants",
            "keywords": "gear oil,transmission oil,differential oil,gearbox oil", "tags": "oil,gear,transmission",
            "unit": "Liters", "business_type": "product"
        },
        {
            "code": "2710_003", "description": "Brake Oil & Coolant",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Fluids",
            "keywords": "brake oil,brake fluid,coolant,radiator coolant,dot 3,dot 4", "tags": "fluid,brake,coolant",
            "unit": "Liters", "business_type": "product"
        },
        {
            "code": "4011_001", "description": "Car Tyres",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Tyres",
            "keywords": "car tyre,car tire,tubeless tyre,radial tyre,passenger car tyre", "tags": "tyre,car,wheel",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "4011_002", "description": "Two Wheeler Tyres",
            "gst_rate": 28.0, "type": "HSN", "category": "Automotive", "subcategory": "Tyres",
            "keywords": "bike tyre,motorcycle tyre,scooter tyre,two wheeler tyre", "tags": "tyre,bike,motorcycle",
            "unit": "Nos", "business_type": "product"
        },

        # ===== TEXTILES & GARMENTS =====
        
        # Men's Clothing
        {
            "code": "6205_001", "description": "Men's Formal Shirts",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Men_Clothing",
            "keywords": "men shirt,formal shirt,office shirt,dress shirt,cotton shirt", "tags": "shirt,men,formal",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "6205_002", "description": "Men's Casual Shirts",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Men_Clothing",
            "keywords": "casual shirt,men casual,check shirt,printed shirt", "tags": "shirt,men,casual",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "6203_001", "description": "Men's Formal Trousers",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Men_Clothing",
            "keywords": "formal trouser,men pant,office trouser,dress pant", "tags": "trouser,men,formal",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "6203_002", "description": "Men's Jeans",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Men_Clothing",
            "keywords": "men jeans,denim,casual jeans,blue jeans", "tags": "jeans,men,denim",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "6109_001", "description": "Men's T-Shirts",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Men_Clothing",
            "keywords": "t-shirt,tshirt,men tshirt,cotton tshirt,round neck,polo", "tags": "tshirt,men,casual",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "6110_001", "description": "Men's Sweaters & Pullovers",
            "gst_rate": 12.0, "type": "HSN", "category": "Textiles", "subcategory": "Men_Clothing",
            "keywords": "sweater,pullover,men sweater,woolen,cardigan", "tags": "sweater,men,winter",
            "unit": "Nos", "business_type": "product"
        },

        # Women's Clothing
        {
            "code": "6204_001", "description": "Women's Kurtis & Ethnic Wear",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Women_Clothing",
            "keywords": "kurti,women kurti,ethnic wear,indian wear,traditional", "tags": "kurti,women,ethnic",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "6204_002", "description": "Women's Formal Shirts & Tops",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Women_Clothing",
            "keywords": "women shirt,formal top,office wear,ladies shirt", "tags": "shirt,women,formal",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "6204_003", "description": "Women's Jeans & Trousers",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Women_Clothing",
            "keywords": "women jeans,ladies jeans,women trouser,denim", "tags": "jeans,women,trouser",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "6204_004", "description": "Women's Dresses",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Women_Clothing",
            "keywords": "dress,women dress,party dress,casual dress,formal dress", "tags": "dress,women,party",
            "unit": "Nos", "business_type": "product"
        },

        # Home Textiles
        {
            "code": "6302_001", "description": "Bed Sheets & Bed Linen",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Home_Textiles",
            "keywords": "bed sheet,bed linen,double bed sheet,single bed sheet,cotton bed sheet", "tags": "bedsheet,home,linen",
            "unit": "Set", "business_type": "product"
        },
        {
            "code": "6302_002", "description": "Pillow Covers & Cushion Covers",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Home_Textiles",
            "keywords": "pillow cover,cushion cover,decorative cover,home decor", "tags": "pillow,cushion,home",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "6302_003", "description": "Curtains & Drapes",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Home_Textiles",
            "keywords": "curtain,drapes,window curtain,door curtain,home decor", "tags": "curtain,window,home",
            "unit": "Pair", "business_type": "product"
        },
        {
            "code": "5208_001", "description": "Cotton Fabric & Cloth",
            "gst_rate": 5.0, "type": "HSN", "category": "Textiles", "subcategory": "Fabrics",
            "keywords": "cotton fabric,cloth,cotton cloth,fabric material,textile", "tags": "fabric,cotton,cloth",
            "unit": "Meters", "business_type": "product"
        },

        # ===== FMCG & DAILY USE ITEMS =====
        
        # Personal Care
        {
            "code": "3401_001", "description": "Bath Soaps & Hand Soaps",
            "gst_rate": 18.0, "type": "HSN", "category": "FMCG", "subcategory": "Personal_Care",
            "keywords": "soap,bath soap,hand soap,antibacterial soap,beauty soap", "tags": "soap,personal,hygiene",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "3305_001", "description": "Shampoos & Hair Care",
            "gst_rate": 18.0, "type": "HSN", "category": "FMCG", "subcategory": "Personal_Care",
            "keywords": "shampoo,hair oil,conditioner,hair care,anti dandruff", "tags": "shampoo,hair,care",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "3401_002", "description": "Detergent Powder & Liquid",
            "gst_rate": 18.0, "type": "HSN", "category": "FMCG", "subcategory": "Cleaning",
            "keywords": "detergent,washing powder,liquid detergent,laundry detergent", "tags": "detergent,cleaning,laundry",
            "unit": "Kg", "business_type": "product"
        },
        {
            "code": "3307_001", "description": "Toothpaste & Oral Care",
            "gst_rate": 18.0, "type": "HSN", "category": "FMCG", "subcategory": "Personal_Care",
            "keywords": "toothpaste,toothbrush,mouthwash,oral care,dental care", "tags": "toothpaste,oral,dental",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "3304_001", "description": "Face Creams & Moisturizers",
            "gst_rate": 18.0, "type": "HSN", "category": "FMCG", "subcategory": "Personal_Care",
            "keywords": "face cream,moisturizer,skin care,beauty cream,lotion", "tags": "cream,skin,beauty",
            "unit": "Nos", "business_type": "product"
        },

        # Food Items
        {
            "code": "2106_001", "description": "Ready to Eat Food & Noodles",
            "gst_rate": 5.0, "type": "HSN", "category": "FMCG", "subcategory": "Food_Items",
            "keywords": "ready to eat,instant noodles,maggi,pasta,instant food", "tags": "food,instant,noodles",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "1701_001", "description": "Sugar & Sweeteners",
            "gst_rate": 0.0, "type": "HSN", "category": "FMCG", "subcategory": "Food_Items",
            "keywords": "sugar,jaggery,sweetener,brown sugar,white sugar", "tags": "sugar,sweet,food",
            "unit": "Kg", "business_type": "product"
        },
        {
            "code": "1006_001", "description": "Rice & Food Grains",
            "gst_rate": 5.0, "type": "HSN", "category": "FMCG", "subcategory": "Food_Items",
            "keywords": "rice,basmati rice,food grain,wheat,dal,pulses", "tags": "rice,grain,food",
            "unit": "Kg", "business_type": "product"
        },
        {
            "code": "1001_001", "description": "Wheat & Flour",
            "gst_rate": 5.0, "type": "HSN", "category": "FMCG", "subcategory": "Food_Items",
            "keywords": "wheat,flour,wheat flour,atta,maida,food grain", "tags": "wheat,flour,grain",
            "unit": "Kg", "business_type": "product"
        },
        {
            "code": "1507_001", "description": "Cooking Oil & Edible Oil",
            "gst_rate": 5.0, "type": "HSN", "category": "FMCG", "subcategory": "Food_Items",
            "keywords": "cooking oil,sunflower oil,mustard oil,coconut oil,edible oil", "tags": "oil,cooking,edible",
            "unit": "Liters", "business_type": "product"
        },

        # ===== PHARMACEUTICALS & MEDICAL =====
        
        # Medicines
        {
            "code": "3004_001", "description": "Pain Relief Medicines",
            "gst_rate": 5.0, "type": "HSN", "category": "Pharmaceuticals", "subcategory": "Medicines",
            "keywords": "paracetamol,aspirin,pain relief,fever medicine,headache medicine", "tags": "medicine,pain,fever",
            "unit": "Strip", "business_type": "product"
        },
        {
            "code": "3004_002", "description": "Cold & Cough Medicines",
            "gst_rate": 12.0, "type": "HSN", "category": "Pharmaceuticals", "subcategory": "Medicines",
            "keywords": "cough syrup,cold medicine,throat medicine,respiratory medicine", "tags": "medicine,cough,cold",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "3004_003", "description": "Ayurvedic Medicines",
            "gst_rate": 12.0, "type": "HSN", "category": "Pharmaceuticals", "subcategory": "Medicines",
            "keywords": "ayurvedic,herbal medicine,natural medicine,traditional medicine", "tags": "medicine,ayurvedic,herbal",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "3005_001", "description": "Bandages & First Aid",
            "gst_rate": 12.0, "type": "HSN", "category": "Pharmaceuticals", "subcategory": "Medical_Supplies",
            "keywords": "bandage,first aid,cotton,gauze,medical supplies", "tags": "bandage,first aid,medical",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "9018_001", "description": "Medical Equipment",
            "gst_rate": 5.0, "type": "HSN", "category": "Pharmaceuticals", "subcategory": "Medical_Equipment",
            "keywords": "thermometer,bp machine,medical equipment,health monitor", "tags": "medical,equipment,health",
            "unit": "Nos", "business_type": "product"
        },

        # ===== STATIONERY & OFFICE SUPPLIES =====
        
        # Paper Products
        {
            "code": "4817_001", "description": "A4 Paper & Office Paper",
            "gst_rate": 18.0, "type": "HSN", "category": "Stationery", "subcategory": "Paper_Products",
            "keywords": "a4 paper,office paper,copier paper,printing paper", "tags": "paper,office,printing",
            "unit": "Ream", "business_type": "product"
        },
        {
            "code": "4817_002", "description": "Notebooks & Diaries",
            "gst_rate": 18.0, "type": "HSN", "category": "Stationery", "subcategory": "Paper_Products",
            "keywords": "notebook,diary,writing pad,exercise book,spiral notebook", "tags": "notebook,diary,writing",
            "unit": "Nos", "business_type": "product"
        },

        # Writing Instruments
        {
            "code": "9608_001", "description": "Ball Pens & Gel Pens",
            "gst_rate": 18.0, "type": "HSN", "category": "Stationery", "subcategory": "Writing_Instruments",
            "keywords": "ball pen,gel pen,blue pen,black pen,writing pen", "tags": "pen,writing,office",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "9608_002", "description": "Pencils & Mechanical Pencils",
            "gst_rate": 18.0, "type": "HSN", "category": "Stationery", "subcategory": "Writing_Instruments",
            "keywords": "pencil,mechanical pencil,hb pencil,drawing pencil", "tags": "pencil,writing,drawing",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "9609_001", "description": "Erasers & Sharpeners",
            "gst_rate": 18.0, "type": "HSN", "category": "Stationery", "subcategory": "Writing_Instruments",
            "keywords": "eraser,rubber,sharpener,pencil sharpener", "tags": "eraser,sharpener,stationery",
            "unit": "Nos", "business_type": "product"
        },

        # Office Supplies
        {
            "code": "3919_001", "description": "Adhesive Tapes & Glue",
            "gst_rate": 18.0, "type": "HSN", "category": "Stationery", "subcategory": "Office_Supplies",
            "keywords": "tape,adhesive tape,cello tape,glue,fevicol", "tags": "tape,adhesive,office",
            "unit": "Nos", "business_type": "product"
        },
        {
            "code": "8443_001", "description": "Office Printers & Photocopiers",
            "gst_rate": 18.0, "type": "HSN", "category": "Stationery", "subcategory": "Office_Equipment",
            "keywords": "office printer,photocopier,xerox machine,office equipment", "tags": "printer,office,equipment",
            "unit": "Nos", "business_type": "product"
        }
    ]

def rebuild_comprehensive_products():
    """Rebuild the product database with comprehensive categories"""
    
    print("🚀 REBUILDING COMPREHENSIVE PRODUCT DATABASE")
    print("=" * 60)
    print("🎯 Strategy: SMART SPECIFICITY")
    print("   ✅ Not too generic (Electronic Equipment)")
    print("   ✅ Not too specific (iPhone 14 Pro Max 256GB)")
    print("   ✅ Just right (Smartphones, Gaming Laptops, LED TVs)")
    print()
    
    db = SessionLocal()
    
    try:
        # First, let's see current state
        current_count = db.query(HSNCode).count()
        print(f"📊 Current products in database: {current_count}")
        
        # Clear existing products (if user wants fresh start)
        print("\n⚠️  Do you want to clear existing products and rebuild? (This is recommended)")
        print("   This will remove all current HSN codes and rebuild with comprehensive categories")
        
        # For now, let's add new products without clearing
        products_data = get_comprehensive_products_data()
        
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        print(f"\n🔄 Processing {len(products_data)} comprehensive product categories...")
        
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
                db.commit()
                updated_count += 1
                print(f"✏️  Updated: {product_data['description']}")
            else:
                # Check if code already exists
                code_exists = db.query(HSNCode).filter(HSNCode.code == product_data["code"]).first()
                
                if code_exists:
                    skipped_count += 1
                    print(f"⚠️  Skipped: {product_data['description']} (Code {product_data['code']} exists)")
                    continue
                
                try:
                    # Create new product
                    product = HSNCode(**product_data)
                    db.add(product)
                    db.commit()
                    added_count += 1
                    print(f"✅ Added: {product_data['description']}")
                except Exception as e:
                    db.rollback()
                    skipped_count += 1
                    print(f"⚠️  Skipped: {product_data['description']} - {str(e)[:100]}")
                    continue
        
        final_count = db.query(HSNCode).count()
        
        print(f"\n🎉 COMPREHENSIVE PRODUCT DATABASE REBUILD COMPLETE!")
        print(f"📈 Added: {added_count} new product categories")
        print(f"🔄 Updated: {updated_count} existing products")
        print(f"⚠️  Skipped: {skipped_count} products")
        print(f"📊 Total products now: {final_count}")
        
        # Show comprehensive coverage by category
        print(f"\n💡 COMPREHENSIVE PRODUCT COVERAGE:")
        
        categories = ["Electronics", "Automotive", "Textiles", "FMCG", "Pharmaceuticals", "Stationery"]
        for category in categories:
            category_products = db.query(HSNCode).filter(
                HSNCode.category == category,
                HSNCode.type == "HSN"
            ).count()
            
            sample_products = db.query(HSNCode).filter(
                HSNCode.category == category,
                HSNCode.type == "HSN"
            ).limit(4).all()
            
            print(f"\n📱 {category.upper()} ({category_products} product types):")
            for product in sample_products:
                print(f"   • {product.description}")
            if category_products > 4:
                print(f"   ... and {category_products - 4} more")
        
    except Exception as e:
        print(f"❌ Error rebuilding products: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    rebuild_comprehensive_products()
