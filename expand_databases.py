#!/usr/bin/env python3
"""
Massive Database Expansion
Adds hundreds more products (HSN) and services to make the system comprehensive
"""

from sqlalchemy.orm import sessionmaker
from database import engine, get_db
from models import HSNCode, MasterService
import json

def get_expanded_hsn_data():
    """Get massive expanded HSN product database"""
    
    expanded_hsn = [
        # Additional Electronics & Technology
        {"code": "8542", "description": "Electronic Circuits, Microprocessors & Chips", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Components", "keywords": "microprocessor,circuit,chip,electronic,semiconductor", "unit": "Nos"},
        {"code": "8529", "description": "Antennas, Satellite Dishes & RF Equipment", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Communication", "keywords": "antenna,satellite,dish,rf,communication", "unit": "Nos"},
        {"code": "8521", "description": "Video Recording Equipment, Camcorders", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Video", "keywords": "video,recording,camcorder,camera,filming", "unit": "Nos"},
        {"code": "8519", "description": "CD Players, MP3 Players & Music Systems", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Audio", "keywords": "cd player,mp3,music system,audio player", "unit": "Nos"},
        {"code": "9013", "description": "Laser Equipment, Optical Instruments", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Optical", "keywords": "laser,optical,instrument,measurement", "unit": "Nos"},
        {"code": "8526", "description": "Radar Equipment, Remote Control Devices", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Control", "keywords": "radar,remote control,wireless,automation", "unit": "Nos"},
        
        # Smart Home & IoT
        {"code": "8531", "description": "Smart Home Devices, IoT Sensors & Alarms", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Smart Home", "keywords": "smart home,iot,sensor,alarm,automation,alexa,google home", "unit": "Nos"},
        {"code": "8543", "description": "Electric Motors, Servo Motors & Actuators", "gst_rate": 18.0, "type": "HSN", "category": "Electronics", "subcategory": "Motors", "keywords": "motor,servo,actuator,electric,automation", "unit": "Nos"},
        
        # Extended Home Appliances
        {"code": "8422", "description": "Dishwashers, Bottle Washing Machines", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Kitchen", "keywords": "dishwasher,kitchen,cleaning,washing", "unit": "Nos"},
        {"code": "8451", "description": "Textile Machinery, Sewing Machines", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Textile", "keywords": "sewing machine,textile,tailoring,embroidery", "unit": "Nos"},
        {"code": "8452", "description": "Industrial Sewing Machines, Embroidery", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Industrial", "keywords": "industrial sewing,embroidery,textile machinery", "unit": "Nos"},
        {"code": "8414", "description": "Air Pumps, Vacuum Pumps & Compressors", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Pumps", "keywords": "pump,vacuum,compressor,air pump", "unit": "Nos"},
        {"code": "8413", "description": "Water Pumps, Submersible Pumps", "gst_rate": 18.0, "type": "HSN", "category": "Appliances", "subcategory": "Water", "keywords": "water pump,submersible,pump,irrigation", "unit": "Nos"},
        
        # Sports & Fitness Equipment
        {"code": "9506", "description": "Gym Equipment, Treadmills & Exercise Machines", "gst_rate": 18.0, "type": "HSN", "category": "Sports", "subcategory": "Fitness", "keywords": "gym,treadmill,exercise,fitness,equipment,workout", "unit": "Nos"},
        {"code": "9503", "description": "Bicycles, Cycles & Bike Accessories", "gst_rate": 12.0, "type": "HSN", "category": "Sports", "subcategory": "Cycling", "keywords": "bicycle,cycle,bike,cycling,mountain bike", "unit": "Nos"},
        {"code": "9507", "description": "Fishing Equipment, Rods & Tackle", "gst_rate": 18.0, "type": "HSN", "category": "Sports", "subcategory": "Fishing", "keywords": "fishing,rod,tackle,angling", "unit": "Nos"},
        {"code": "9506", "description": "Cricket Equipment, Bats & Sports Gear", "gst_rate": 18.0, "type": "HSN", "category": "Sports", "subcategory": "Cricket", "keywords": "cricket,bat,sports,gear,helmet,pads", "unit": "Nos"},
        {"code": "9506", "description": "Football, Basketball & Sports Balls", "gst_rate": 18.0, "type": "HSN", "category": "Sports", "subcategory": "Ball Games", "keywords": "football,basketball,sports ball,volleyball", "unit": "Nos"},
        
        # Musical Instruments
        {"code": "9207", "description": "Musical Instruments, Guitars & Keyboards", "gst_rate": 18.0, "type": "HSN", "category": "Music", "subcategory": "Instruments", "keywords": "guitar,keyboard,piano,musical instrument", "unit": "Nos"},
        {"code": "9208", "description": "Music Boxes, Harmonicas & Wind Instruments", "gst_rate": 18.0, "type": "HSN", "category": "Music", "subcategory": "Wind", "keywords": "harmonica,flute,wind instrument,music box", "unit": "Nos"},
        {"code": "9209", "description": "Musical Instrument Parts & Accessories", "gst_rate": 18.0, "type": "HSN", "category": "Music", "subcategory": "Accessories", "keywords": "strings,picks,musical accessories", "unit": "Nos"},
        
        # Extended Clothing & Fashion
        {"code": "4203", "description": "Leather Goods, Bags & Wallets", "gst_rate": 18.0, "type": "HSN", "category": "Fashion", "subcategory": "Leather", "keywords": "leather,bag,wallet,handbag,purse,belt", "unit": "Nos"},
        {"code": "6601", "description": "Umbrellas, Walking Sticks", "gst_rate": 18.0, "type": "HSN", "category": "Fashion", "subcategory": "Accessories", "keywords": "umbrella,walking stick,rain protection", "unit": "Nos"},
        {"code": "7113", "description": "Fashion Jewelry, Artificial Jewelry", "gst_rate": 3.0, "type": "HSN", "category": "Fashion", "subcategory": "Jewelry", "keywords": "jewelry,fashion jewelry,artificial,ornaments", "unit": "Nos"},
        {"code": "9615", "description": "Hair Accessories, Hair Clips & Bands", "gst_rate": 18.0, "type": "HSN", "category": "Fashion", "subcategory": "Hair", "keywords": "hair clip,hair band,hair accessories", "unit": "Nos"},
        {"code": "4202", "description": "Travel Bags, Suitcases & Luggage", "gst_rate": 18.0, "type": "HSN", "category": "Fashion", "subcategory": "Luggage", "keywords": "suitcase,luggage,travel bag,trolley bag", "unit": "Nos"},
        
        # Home Decor & Furniture
        {"code": "9405", "description": "Lamps, LED Lights & Lighting Fixtures", "gst_rate": 18.0, "type": "HSN", "category": "Home", "subcategory": "Lighting", "keywords": "lamp,led,light,lighting,fixture,bulb", "unit": "Nos"},
        {"code": "7009", "description": "Mirrors, Glass Decoratives", "gst_rate": 18.0, "type": "HSN", "category": "Home", "subcategory": "Decor", "keywords": "mirror,glass,decorative,home decor", "unit": "Nos"},
        {"code": "9404", "description": "Mattresses, Cushions & Pillows", "gst_rate": 18.0, "type": "HSN", "category": "Home", "subcategory": "Bedding", "keywords": "mattress,cushion,pillow,bedding,foam", "unit": "Nos"},
        {"code": "5703", "description": "Carpets, Rugs & Floor Coverings", "gst_rate": 18.0, "type": "HSN", "category": "Home", "subcategory": "Flooring", "keywords": "carpet,rug,floor covering,mat", "unit": "Sq Mt"},
        {"code": "6304", "description": "Curtains, Drapes & Window Coverings", "gst_rate": 12.0, "type": "HSN", "category": "Home", "subcategory": "Window", "keywords": "curtain,drape,window covering,blinds", "unit": "Set"},
        
        # Garden & Outdoor
        {"code": "8201", "description": "Garden Tools, Spades & Hand Tools", "gst_rate": 18.0, "type": "HSN", "category": "Garden", "subcategory": "Tools", "keywords": "garden tools,spade,shovel,hand tools", "unit": "Nos"},
        {"code": "8433", "description": "Lawn Mowers, Garden Equipment", "gst_rate": 18.0, "type": "HSN", "category": "Garden", "subcategory": "Equipment", "keywords": "lawn mower,garden equipment,grass cutter", "unit": "Nos"},
        {"code": "0602", "description": "Plants, Saplings & Nursery Items", "gst_rate": 5.0, "type": "HSN", "category": "Garden", "subcategory": "Plants", "keywords": "plants,sapling,nursery,tree,flower", "unit": "Nos"},
        {"code": "3105", "description": "Fertilizers, Plant Food & Garden Chemicals", "gst_rate": 5.0, "type": "HSN", "category": "Garden", "subcategory": "Fertilizer", "keywords": "fertilizer,plant food,garden,chemical", "unit": "Kg"},
        
        # Automotive Extended
        {"code": "4016", "description": "Car Mats, Rubber Accessories", "gst_rate": 18.0, "type": "HSN", "category": "Automotive", "subcategory": "Accessories", "keywords": "car mat,rubber,automotive accessories", "unit": "Set"},
        {"code": "7007", "description": "Car Glass, Windshields & Mirrors", "gst_rate": 18.0, "type": "HSN", "category": "Automotive", "subcategory": "Glass", "keywords": "windshield,car glass,mirror,automotive glass", "unit": "Nos"},
        {"code": "8708", "description": "Car Batteries, Automotive Batteries", "gst_rate": 18.0, "type": "HSN", "category": "Automotive", "subcategory": "Battery", "keywords": "car battery,automotive battery,vehicle battery", "unit": "Nos"},
        {"code": "8511", "description": "Car Lights, Headlights & Indicators", "gst_rate": 18.0, "type": "HSN", "category": "Automotive", "subcategory": "Lights", "keywords": "headlight,car light,indicator,automotive lighting", "unit": "Nos"},
        
        # Health & Wellness
        {"code": "9021", "description": "Wheelchairs, Medical Mobility Aids", "gst_rate": 5.0, "type": "HSN", "category": "Medical", "subcategory": "Mobility", "keywords": "wheelchair,mobility aid,walking aid,medical", "unit": "Nos"},
        {"code": "9019", "description": "Massage Equipment, Physiotherapy Devices", "gst_rate": 12.0, "type": "HSN", "category": "Medical", "subcategory": "Therapy", "keywords": "massage,physiotherapy,therapy,medical device", "unit": "Nos"},
        {"code": "9020", "description": "Breathing Apparatus, Oxygen Equipment", "gst_rate": 12.0, "type": "HSN", "category": "Medical", "subcategory": "Respiratory", "keywords": "oxygen,breathing,respiratory,medical equipment", "unit": "Nos"},
        {"code": "3002", "description": "Vaccines, Medical Preparations", "gst_rate": 5.0, "type": "HSN", "category": "Medical", "subcategory": "Vaccine", "keywords": "vaccine,medical,preparation,immunization", "unit": "Vial"},
        
        # Baby & Kids Products
        {"code": "9503", "description": "Toys, Dolls & Children's Games", "gst_rate": 12.0, "type": "HSN", "category": "Kids", "subcategory": "Toys", "keywords": "toy,doll,children,kids,games,play", "unit": "Nos"},
        {"code": "8715", "description": "Baby Strollers, Prams & Carriers", "gst_rate": 18.0, "type": "HSN", "category": "Kids", "subcategory": "Transport", "keywords": "stroller,pram,baby carrier,children", "unit": "Nos"},
        {"code": "9404", "description": "Baby Mattresses, Cribs & Nursery Furniture", "gst_rate": 12.0, "type": "HSN", "category": "Kids", "subcategory": "Furniture", "keywords": "crib,baby mattress,nursery,children furniture", "unit": "Nos"},
        {"code": "6111", "description": "Baby Clothes, Children's Clothing", "gst_rate": 5.0, "type": "HSN", "category": "Kids", "subcategory": "Clothing", "keywords": "baby clothes,children clothing,kids wear", "unit": "Nos"},
        
        # Extended Food Categories
        {"code": "2008", "description": "Processed Fruits, Jams & Preserves", "gst_rate": 12.0, "type": "HSN", "category": "Food", "subcategory": "Processed", "keywords": "jam,preserve,processed fruit,pickle", "unit": "Kg"},
        {"code": "1704", "description": "Chocolates, Sweets & Confectionery", "gst_rate": 18.0, "type": "HSN", "category": "Food", "subcategory": "Sweets", "keywords": "chocolate,sweet,candy,confectionery", "unit": "Kg"},
        {"code": "2005", "description": "Pickles, Chutneys & Preserved Vegetables", "gst_rate": 12.0, "type": "HSN", "category": "Food", "subcategory": "Preserved", "keywords": "pickle,chutney,preserved,vegetables", "unit": "Kg"},
        {"code": "0709", "description": "Fresh Vegetables, Onions & Potatoes", "gst_rate": 0.0, "type": "HSN", "category": "Food", "subcategory": "Vegetables", "keywords": "vegetables,onion,potato,fresh,produce", "unit": "Kg"},
        {"code": "0803", "description": "Fresh Fruits, Bananas & Apples", "gst_rate": 0.0, "type": "HSN", "category": "Food", "subcategory": "Fruits", "keywords": "fruit,banana,apple,fresh,produce", "unit": "Kg"},
        {"code": "1806", "description": "Ice Cream, Frozen Desserts", "gst_rate": 18.0, "type": "HSN", "category": "Food", "subcategory": "Frozen", "keywords": "ice cream,frozen,dessert,kulfi", "unit": "Ltr"},
        
        # Cosmetics & Beauty Extended
        {"code": "3303", "description": "Perfumed Oils, Aromatherapy Products", "gst_rate": 18.0, "type": "HSN", "category": "Beauty", "subcategory": "Aromatherapy", "keywords": "aromatherapy,essential oil,perfumed oil", "unit": "Ml"},
        {"code": "3306", "description": "Dental Care, Teeth Whitening Products", "gst_rate": 18.0, "type": "HSN", "category": "Beauty", "subcategory": "Dental", "keywords": "dental care,teeth whitening,oral care", "unit": "Nos"},
        {"code": "9616", "description": "Beauty Tools, Makeup Brushes", "gst_rate": 18.0, "type": "HSN", "category": "Beauty", "subcategory": "Tools", "keywords": "makeup brush,beauty tools,cosmetic tools", "unit": "Set"},
        
        # Paper & Packaging
        {"code": "4819", "description": "Packaging Materials, Cartons & Boxes", "gst_rate": 18.0, "type": "HSN", "category": "Packaging", "subcategory": "Boxes", "keywords": "packaging,carton,box,shipping,delivery", "unit": "Nos"},
        {"code": "3923", "description": "Plastic Bags, Containers & Storage", "gst_rate": 18.0, "type": "HSN", "category": "Packaging", "subcategory": "Plastic", "keywords": "plastic bag,container,storage,packaging", "unit": "Nos"},
        {"code": "4823", "description": "Paper Plates, Disposable Tableware", "gst_rate": 18.0, "type": "HSN", "category": "Packaging", "subcategory": "Disposable", "keywords": "paper plate,disposable,tableware,party", "unit": "Pack"},
        
        # Cleaning & Maintenance
        {"code": "3402", "description": "Detergents, Washing Powder & Cleaners", "gst_rate": 18.0, "type": "HSN", "category": "Cleaning", "subcategory": "Detergent", "keywords": "detergent,washing powder,cleaner,laundry", "unit": "Kg"},
        {"code": "3808", "description": "Disinfectants, Sanitizers & Pest Control", "gst_rate": 18.0, "type": "HSN", "category": "Cleaning", "subcategory": "Sanitizer", "keywords": "sanitizer,disinfectant,pest control,cleaning", "unit": "Ltr"},
        {"code": "9603", "description": "Brooms, Brushes & Cleaning Tools", "gst_rate": 18.0, "type": "HSN", "category": "Cleaning", "subcategory": "Tools", "keywords": "broom,brush,cleaning tools,mop", "unit": "Nos"},
        
        # Renewable Energy
        {"code": "8541", "description": "Solar Panels, Photovoltaic Cells", "gst_rate": 5.0, "type": "HSN", "category": "Energy", "subcategory": "Solar", "keywords": "solar panel,photovoltaic,renewable energy,solar", "unit": "Nos"},
        {"code": "8502", "description": "Wind Turbines, Generators", "gst_rate": 18.0, "type": "HSN", "category": "Energy", "subcategory": "Wind", "keywords": "wind turbine,generator,renewable,wind energy", "unit": "Nos"},
        {"code": "8507", "description": "Rechargeable Batteries, Energy Storage", "gst_rate": 18.0, "type": "HSN", "category": "Energy", "subcategory": "Battery", "keywords": "battery,rechargeable,energy storage,lithium", "unit": "Nos"},
    ]
    
    return expanded_hsn

def get_expanded_services_data():
    """Get massive expanded services database"""
    
    expanded_services = [
        # Advanced IT Services
        {"name": "Cloud Computing Services", "description": "Cloud infrastructure setup and management", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Cloud", "keywords": "cloud,aws,azure,google cloud,infrastructure,saas,paas", "unit": "Hours"},
        {"name": "Cybersecurity Services", "description": "Information security and cyber threat protection", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Security", "keywords": "cybersecurity,security,firewall,antivirus,protection,hacking", "unit": "Hours"},
        {"name": "Data Analytics Services", "description": "Big data analysis and business intelligence", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Analytics", "keywords": "data analytics,business intelligence,big data,reporting,dashboard", "unit": "Hours"},
        {"name": "AI/ML Development", "description": "Artificial Intelligence and Machine Learning solutions", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "AI", "keywords": "artificial intelligence,machine learning,ai,ml,deep learning,nlp", "unit": "Hours"},
        {"name": "Blockchain Development", "description": "Blockchain and cryptocurrency application development", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Blockchain", "keywords": "blockchain,cryptocurrency,bitcoin,ethereum,smart contracts,defi", "unit": "Hours"},
        {"name": "IoT Solutions", "description": "Internet of Things device integration and management", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "IoT", "keywords": "iot,internet of things,sensors,automation,smart devices", "unit": "Hours"},
        {"name": "DevOps & Automation", "description": "Development operations and process automation", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "DevOps", "keywords": "devops,automation,ci cd,docker,kubernetes,jenkins", "unit": "Hours"},
        {"name": "Technical Writing", "description": "Documentation and technical content creation", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Documentation", "keywords": "technical writing,documentation,api docs,user manual", "unit": "Hours"},
        {"name": "Software Testing", "description": "Quality assurance and software testing services", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Testing", "keywords": "software testing,qa,quality assurance,automation testing,manual testing", "unit": "Hours"},
        {"name": "IT Consulting", "description": "Technology strategy and IT consulting services", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Consulting", "keywords": "it consulting,technology consulting,strategy,advisory", "unit": "Hours"},
        
        # Digital Marketing Extended
        {"name": "Search Engine Marketing", "description": "SEM, Google Ads and paid search campaigns", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "SEM", "keywords": "sem,google ads,paid search,ppc,adwords,search marketing", "unit": "Hours"},
        {"name": "Social Media Management", "description": "Complete social media account management", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Social Media", "keywords": "social media management,facebook,instagram,twitter,linkedin,content", "unit": "Hours"},
        {"name": "Influencer Marketing", "description": "Influencer outreach and campaign management", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Influencer", "keywords": "influencer marketing,brand ambassador,collaboration,outreach", "unit": "Campaign"},
        {"name": "Content Marketing", "description": "Strategic content creation and distribution", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Content", "keywords": "content marketing,blog,article,content strategy,storytelling", "unit": "Hours"},
        {"name": "Email Marketing", "description": "Email campaign design and automation", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Email", "keywords": "email marketing,newsletter,email automation,mailchimp", "unit": "Campaign"},
        {"name": "Video Marketing", "description": "Video content creation and promotion", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Video", "keywords": "video marketing,youtube marketing,video content,promotional video", "unit": "Hours"},
        {"name": "Affiliate Marketing", "description": "Affiliate program setup and management", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Affiliate", "keywords": "affiliate marketing,referral program,commission,partnership", "unit": "Hours"},
        {"name": "Brand Strategy", "description": "Brand development and positioning services", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Branding", "keywords": "brand strategy,branding,positioning,brand identity,marketing strategy", "unit": "Hours"},
        {"name": "Market Research", "description": "Market analysis and consumer research", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Research", "keywords": "market research,consumer research,survey,analysis,insights", "unit": "Hours"},
        {"name": "Public Relations", "description": "PR services and media relations", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "PR", "keywords": "public relations,pr,media relations,press release,publicity", "unit": "Hours"},
        
        # Creative Services Extended
        {"name": "3D Design & Modeling", "description": "3D graphics, modeling and animation services", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "3D", "keywords": "3d design,3d modeling,animation,3d graphics,rendering", "unit": "Hours"},
        {"name": "Video Production", "description": "Professional video shooting and editing", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Video", "keywords": "video production,filming,video editing,cinematography", "unit": "Hours"},
        {"name": "Photography Services", "description": "Professional photography for events and products", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Photography", "keywords": "photography,photo shoot,event photography,product photography", "unit": "Hours"},
        {"name": "Audio Production", "description": "Music production and audio editing services", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Audio", "keywords": "audio production,music production,sound editing,recording", "unit": "Hours"},
        {"name": "Logo & Branding Design", "description": "Logo design and complete brand identity", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Branding", "keywords": "logo design,brand identity,corporate identity,branding", "unit": "Project"},
        {"name": "Print Design", "description": "Brochures, flyers and print material design", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Print", "keywords": "print design,brochure,flyer,poster,catalog,print media", "unit": "Hours"},
        {"name": "Packaging Design", "description": "Product packaging and label design", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Packaging", "keywords": "packaging design,label design,product packaging", "unit": "Project"},
        {"name": "Interior Design", "description": "Residential and commercial interior design", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Interior", "keywords": "interior design,home design,office design,space planning", "unit": "Sq Ft"},
        {"name": "Fashion Design", "description": "Clothing and accessory design services", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Fashion", "keywords": "fashion design,clothing design,textile design,pattern making", "unit": "Design"},
        {"name": "Illustration Services", "description": "Custom illustrations and artwork creation", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Illustration", "keywords": "illustration,artwork,custom art,digital illustration", "unit": "Hours"},
        
        # Professional Services Extended
        {"name": "Legal Documentation", "description": "Legal document preparation and review", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Legal", "keywords": "legal documentation,contracts,agreements,legal review", "unit": "Document"},
        {"name": "Patent Services", "description": "Patent filing and intellectual property services", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "IP", "keywords": "patent,intellectual property,trademark,copyright,ip", "unit": "Application"},
        {"name": "Tax Consultation", "description": "Tax planning and compliance services", "sac_code": "998313", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Tax", "keywords": "tax consultation,tax planning,tax filing,compliance", "unit": "Hours"},
        {"name": "Business Registration", "description": "Company incorporation and registration services", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Registration", "keywords": "business registration,company incorporation,startup,legal entity", "unit": "Application"},
        {"name": "Investment Advisory", "description": "Financial investment and portfolio advisory", "sac_code": "998313", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Investment", "keywords": "investment advisory,portfolio,financial planning,wealth management", "unit": "Hours"},
        {"name": "Insurance Services", "description": "Insurance consultation and policy services", "sac_code": "998313", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Insurance", "keywords": "insurance,policy,life insurance,health insurance,general insurance", "unit": "Policy"},
        {"name": "Loan Services", "description": "Loan processing and financial assistance", "sac_code": "998313", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Finance", "keywords": "loan,home loan,personal loan,business loan,finance", "unit": "Application"},
        {"name": "Property Valuation", "description": "Real estate valuation and assessment", "sac_code": "997211", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Valuation", "keywords": "property valuation,real estate valuation,assessment,appraisal", "unit": "Property"},
        {"name": "Recruitment Services", "description": "Talent acquisition and placement services", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "HR", "keywords": "recruitment,hiring,talent acquisition,job placement,staffing", "unit": "Position"},
        {"name": "Training & Development", "description": "Corporate training and skill development", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Training", "keywords": "training,corporate training,skill development,workshop,seminar", "unit": "Hours"},
        
        # Health & Wellness Services
        {"name": "Physiotherapy", "description": "Physical therapy and rehabilitation services", "sac_code": "998311", "gst_rate": 5.0, "category": "Healthcare", "subcategory": "Therapy", "keywords": "physiotherapy,physical therapy,rehabilitation,exercise therapy", "unit": "Session"},
        {"name": "Nutrition Counseling", "description": "Diet planning and nutrition consultation", "sac_code": "998311", "gst_rate": 5.0, "category": "Healthcare", "subcategory": "Nutrition", "keywords": "nutrition,diet plan,nutritionist,health consultation", "unit": "Session"},
        {"name": "Mental Health Counseling", "description": "Psychology and mental health services", "sac_code": "998311", "gst_rate": 5.0, "category": "Healthcare", "subcategory": "Mental Health", "keywords": "mental health,psychology,counseling,therapy,psychiatry", "unit": "Session"},
        {"name": "Yoga Instruction", "description": "Yoga classes and wellness instruction", "sac_code": "998399", "gst_rate": 18.0, "category": "Healthcare", "subcategory": "Wellness", "keywords": "yoga,meditation,wellness,fitness,health", "unit": "Class"},
        {"name": "Massage Therapy", "description": "Therapeutic massage and spa services", "sac_code": "997331", "gst_rate": 18.0, "category": "Healthcare", "subcategory": "Therapy", "keywords": "massage,spa,therapy,relaxation,wellness", "unit": "Session"},
        {"name": "Home Healthcare", "description": "Medical care services at home", "sac_code": "998311", "gst_rate": 5.0, "category": "Healthcare", "subcategory": "Home Care", "keywords": "home healthcare,nursing,medical care,elder care", "unit": "Hours"},
        
        # Educational Services
        {"name": "Online Tutoring", "description": "Subject-specific online tutoring", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Tutoring", "keywords": "online tutoring,education,teaching,academic,subject tutoring", "unit": "Hours"},
        {"name": "Skill Development Training", "description": "Professional skill and certification training", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Skills", "keywords": "skill development,certification,professional training,courses", "unit": "Hours"},
        {"name": "Language Classes", "description": "Foreign language learning and instruction", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Language", "keywords": "language classes,english,hindi,foreign language,speaking", "unit": "Hours"},
        {"name": "Music Lessons", "description": "Musical instrument and vocal training", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Music", "keywords": "music lessons,guitar,piano,vocal,instrument", "unit": "Hours"},
        {"name": "Dance Classes", "description": "Dance instruction and choreography", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Dance", "keywords": "dance classes,choreography,classical,modern,dance", "unit": "Hours"},
        {"name": "Art Classes", "description": "Drawing, painting and art instruction", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Art", "keywords": "art classes,painting,drawing,sketching,art", "unit": "Hours"},
        
        # Event & Entertainment Services
        {"name": "Wedding Planning", "description": "Complete wedding ceremony planning", "sac_code": "998399", "gst_rate": 18.0, "category": "Event_Services", "subcategory": "Wedding", "keywords": "wedding planning,marriage,ceremony,bridal,wedding", "unit": "Event"},
        {"name": "Birthday Party Planning", "description": "Birthday and celebration event planning", "sac_code": "998399", "gst_rate": 18.0, "category": "Event_Services", "subcategory": "Birthday", "keywords": "birthday party,celebration,party planning,event", "unit": "Event"},
        {"name": "Corporate Event Management", "description": "Business conferences and corporate events", "sac_code": "998399", "gst_rate": 18.0, "category": "Event_Services", "subcategory": "Corporate", "keywords": "corporate event,conference,seminar,business event", "unit": "Event"},
        {"name": "Live Entertainment", "description": "Live music and entertainment performances", "sac_code": "998399", "gst_rate": 18.0, "category": "Event_Services", "subcategory": "Entertainment", "keywords": "live entertainment,music,performance,band,artist", "unit": "Event"},
        {"name": "DJ Services", "description": "Music and DJ services for events", "sac_code": "998399", "gst_rate": 18.0, "category": "Event_Services", "subcategory": "Music", "keywords": "dj,music,party,event entertainment,sound", "unit": "Event"},
        {"name": "Catering Services", "description": "Food catering for events and parties", "sac_code": "996331", "gst_rate": 5.0, "category": "Event_Services", "subcategory": "Catering", "keywords": "catering,food,event catering,party food,wedding catering", "unit": "Event"},
        
        # Transportation Services
        {"name": "Taxi & Cab Services", "description": "Local transportation and taxi services", "sac_code": "996511", "gst_rate": 5.0, "category": "Transportation", "subcategory": "Taxi", "keywords": "taxi,cab,transport,uber,ola,ride", "unit": "Trip"},
        {"name": "Delivery Services", "description": "Package delivery and courier services", "sac_code": "996511", "gst_rate": 5.0, "category": "Transportation", "subcategory": "Delivery", "keywords": "delivery,courier,package,shipping,logistics", "unit": "Delivery"},
        {"name": "Moving Services", "description": "Household and office relocation", "sac_code": "996511", "gst_rate": 5.0, "category": "Transportation", "subcategory": "Moving", "keywords": "moving,relocation,packers,movers,shifting", "unit": "Move"},
        {"name": "Car Rental", "description": "Vehicle rental and leasing services", "sac_code": "996511", "gst_rate": 5.0, "category": "Transportation", "subcategory": "Rental", "keywords": "car rental,vehicle rental,self drive,lease", "unit": "Day"},
        {"name": "Logistics Services", "description": "Supply chain and logistics management", "sac_code": "996511", "gst_rate": 5.0, "category": "Transportation", "subcategory": "Logistics", "keywords": "logistics,supply chain,warehousing,distribution", "unit": "Shipment"},
        
        # Property & Real Estate Services
        {"name": "Property Management", "description": "Rental property management services", "sac_code": "997211", "gst_rate": 18.0, "category": "Real_Estate", "subcategory": "Management", "keywords": "property management,rental,real estate,property", "unit": "Property"},
        {"name": "Real Estate Brokerage", "description": "Property buying and selling services", "sac_code": "997211", "gst_rate": 5.0, "category": "Real_Estate", "subcategory": "Brokerage", "keywords": "real estate,property broker,buying,selling,agent", "unit": "Transaction"},
        {"name": "Property Rental", "description": "Residential and commercial property rental", "sac_code": "997211", "gst_rate": 0.0, "category": "Real_Estate", "subcategory": "Rental", "keywords": "property rental,house rent,office rent,residential", "unit": "Month"},
        {"name": "Construction Services", "description": "Building construction and contracting", "sac_code": "995411", "gst_rate": 12.0, "category": "Real_Estate", "subcategory": "Construction", "keywords": "construction,building,contractor,civil work", "unit": "Sq Ft"},
        
        # Security & Safety Services
        {"name": "Security Guard Services", "description": "Physical security and guard services", "sac_code": "997311", "gst_rate": 18.0, "category": "Security_Services", "subcategory": "Guard", "keywords": "security guard,protection,safety,surveillance", "unit": "Hours"},
        {"name": "CCTV Installation", "description": "Security camera installation and monitoring", "sac_code": "997311", "gst_rate": 18.0, "category": "Security_Services", "subcategory": "CCTV", "keywords": "cctv,security camera,surveillance,monitoring", "unit": "Installation"},
        {"name": "Home Security Systems", "description": "Residential security system installation", "sac_code": "997311", "gst_rate": 18.0, "category": "Security_Services", "subcategory": "Home", "keywords": "home security,alarm system,residential security", "unit": "Installation"},
        
        # Maintenance & Repair Services
        {"name": "AC Repair & Maintenance", "description": "Air conditioner repair and servicing", "sac_code": "997212", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "AC", "keywords": "ac repair,air conditioner,servicing,maintenance,cooling", "unit": "Service"},
        {"name": "Appliance Repair", "description": "Home appliance repair services", "sac_code": "997212", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "Appliance", "keywords": "appliance repair,washing machine,refrigerator,microwave", "unit": "Service"},
        {"name": "Plumbing Services", "description": "Water pipe repair and plumbing work", "sac_code": "997212", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "Plumbing", "keywords": "plumbing,pipe repair,water,drainage,plumber", "unit": "Service"},
        {"name": "Electrical Services", "description": "Electrical wiring and repair work", "sac_code": "997212", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "Electrical", "keywords": "electrical,wiring,electrician,repair,installation", "unit": "Service"},
        {"name": "Carpentry Services", "description": "Wood work and furniture repair", "sac_code": "997212", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "Carpentry", "keywords": "carpentry,wood work,furniture,carpenter,repair", "unit": "Service"},
        {"name": "Painting Services", "description": "Wall painting and home painting", "sac_code": "997212", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "Painting", "keywords": "painting,wall painting,home painting,painter", "unit": "Sq Ft"},
        
        # Beauty & Personal Care Services
        {"name": "Hair Salon Services", "description": "Hair cutting, styling and treatments", "sac_code": "997331", "gst_rate": 18.0, "category": "Beauty_Services", "subcategory": "Hair", "keywords": "hair salon,hair cut,styling,hair treatment,salon", "unit": "Service"},
        {"name": "Beauty Parlour Services", "description": "Facial, beauty treatments and makeup", "sac_code": "997331", "gst_rate": 18.0, "category": "Beauty_Services", "subcategory": "Beauty", "keywords": "beauty parlour,facial,makeup,beauty treatment", "unit": "Service"},
        {"name": "Spa Services", "description": "Wellness spa and relaxation treatments", "sac_code": "997331", "gst_rate": 18.0, "category": "Beauty_Services", "subcategory": "Spa", "keywords": "spa,wellness,relaxation,body treatment,therapy", "unit": "Service"},
        {"name": "Nail Services", "description": "Manicure, pedicure and nail art", "sac_code": "997331", "gst_rate": 18.0, "category": "Beauty_Services", "subcategory": "Nails", "keywords": "manicure,pedicure,nail art,nail care", "unit": "Service"},
        
        # Pet Services
        {"name": "Pet Grooming", "description": "Pet cleaning and grooming services", "sac_code": "998399", "gst_rate": 18.0, "category": "Pet_Services", "subcategory": "Grooming", "keywords": "pet grooming,dog grooming,pet care,animal care", "unit": "Service"},
        {"name": "Pet Training", "description": "Animal training and behavior modification", "sac_code": "998399", "gst_rate": 18.0, "category": "Pet_Services", "subcategory": "Training", "keywords": "pet training,dog training,animal behavior,obedience", "unit": "Session"},
        {"name": "Veterinary Services", "description": "Animal health and medical care", "sac_code": "998399", "gst_rate": 18.0, "category": "Pet_Services", "subcategory": "Medical", "keywords": "veterinary,vet,animal health,pet health,medical", "unit": "Consultation"},
        {"name": "Pet Boarding", "description": "Pet care and boarding services", "sac_code": "998399", "gst_rate": 18.0, "category": "Pet_Services", "subcategory": "Boarding", "keywords": "pet boarding,pet care,dog boarding,animal care", "unit": "Day"},
    ]
    
    return expanded_services

def expand_databases():
    """Expand both HSN and Services databases massively"""
    
    try:
        # Get database session
        db = next(get_db())
        
        print("🚀 MASSIVE DATABASE EXPANSION")
        print("=" * 50)
        
        # Expand HSN Database
        print("\n📦 EXPANDING HSN PRODUCTS DATABASE...")
        hsn_data = get_expanded_hsn_data()
        
        hsn_added = 0
        hsn_updated = 0
        seen_codes = set()
        
        for hsn_item in hsn_data:
            code = hsn_item["code"]
            
            # Skip duplicates within the dataset itself
            if code in seen_codes:
                continue
            seen_codes.add(code)
            
            # Check if code already exists in database
            existing = db.query(HSNCode).filter(HSNCode.code == code).first()
            if not existing:
                try:
                    hsn_code = HSNCode(**hsn_item, source="expanded_dataset", is_active=True)
                    db.add(hsn_code)
                    db.commit()  # Commit each one individually
                    hsn_added += 1
                except Exception as e:
                    print(f"   Warning: Could not add HSN {code}: {e}")
                    db.rollback()
            else:
                # Update existing with new description if it's more detailed
                if len(hsn_item["description"]) > len(existing.description):
                    existing.description = hsn_item["description"]
                    existing.keywords = hsn_item.get("keywords")
                    existing.category = hsn_item.get("category") 
                    existing.subcategory = hsn_item.get("subcategory")
                    hsn_updated += 1
        
        db.commit()
        print(f"✅ Added {hsn_added} new HSN codes, updated {hsn_updated} existing codes")
        
        # Expand Services Database
        print("\n🛠️ EXPANDING SERVICES DATABASE...")
        services_data = get_expanded_services_data()
        
        services_added = 0
        for service_item in services_data:
            # Check if already exists
            existing = db.query(MasterService).filter(MasterService.name == service_item["name"]).first()
            if not existing:
                try:
                    service_item["business_type"] = "service"
                    master_service = MasterService(**service_item, is_active=True)
                    db.add(master_service)
                    db.commit()  # Commit individually
                    services_added += 1
                except Exception as e:
                    print(f"   Warning: Could not add service {service_item['name']}: {e}")
                    db.rollback()
        
        print(f"✅ Added {services_added} new services")
        
        # Final counts
        total_hsn = db.query(HSNCode).count()
        total_services = db.query(MasterService).count()
        
        print(f"\n🎉 EXPANSION COMPLETE!")
        print(f"   📦 Total HSN/SAC codes: {total_hsn}")
        print(f"   🛠️ Total Services: {total_services}")
        print(f"   🎯 Total business codes: {total_hsn + total_services}")
        
        # Category breakdown
        print(f"\n📊 HSN Categories:")
        hsn_categories = db.execute("SELECT category, COUNT(*) as count FROM hsn_codes WHERE category IS NOT NULL GROUP BY category ORDER BY count DESC").fetchall()
        for cat, count in hsn_categories[:10]:
            print(f"   {cat}: {count} codes")
        
        print(f"\n📊 Service Categories:")
        service_categories = db.execute("SELECT category, COUNT(*) as count FROM master_services GROUP BY category ORDER BY count DESC").fetchall()
        for cat, count in service_categories[:10]:
            print(f"   {cat.replace('_', ' ')}: {count} services")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error expanding databases: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 MASSIVE DATABASE EXPANSION")
    print("   Adding hundreds more products and services")
    print("=" * 70)
    
    success = expand_databases()
    
    if success:
        print("\n🎉 EXPANSION SUCCESSFUL!")
        print("   ✅ Your system now has comprehensive business coverage")
        print("   ✅ Hundreds of products across all categories") 
        print("   ✅ Professional services for every business type")
        print("   ✅ Smart search will find relevant items instantly")
    else:
        print("\n💥 Expansion failed. Please check the errors above.")
    
    print("=" * 70)
