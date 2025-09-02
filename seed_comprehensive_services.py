#!/usr/bin/env python3
"""
Comprehensive Master Services Database Seeder
Seeds ~500 services across all business categories with proper SAC codes and GST rates
"""

from sqlalchemy.orm import sessionmaker
from database import engine, get_db
from models import MasterService
import json

def get_comprehensive_services():
    """Returns comprehensive list of business services with proper categorization"""
    
    services = [
        # IT & Technology Services (SAC: 998314 - 18% GST)
        {"name": "Web Development", "description": "Custom website development and programming services", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Development", "keywords": "website,web,development,programming,coding,html,css,javascript,react,angular,php,python,nodejs,frontend,backend", "unit": "Hours"},
        {"name": "Mobile App Development", "description": "iOS and Android mobile application development", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Development", "keywords": "mobile,app,ios,android,react native,flutter,xamarin,mobile development", "unit": "Hours"},
        {"name": "Software Development", "description": "Custom software solutions and applications", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Development", "keywords": "software,application,custom,development,programming,solution,system", "unit": "Hours"},
        {"name": "Database Development", "description": "Database design, development and optimization", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Development", "keywords": "database,mysql,postgresql,mongodb,sql,data,design,optimization", "unit": "Hours"},
        {"name": "API Development", "description": "REST API and web services development", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Development", "keywords": "api,rest,web services,integration,microservices,graphql", "unit": "Hours"},
        {"name": "E-commerce Development", "description": "Online store and e-commerce platform development", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Development", "keywords": "ecommerce,online store,shopping cart,payment gateway,shopify,woocommerce", "unit": "Hours"},
        {"name": "CRM Development", "description": "Customer Relationship Management system development", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Development", "keywords": "crm,customer management,sales,lead tracking,customer service", "unit": "Hours"},
        {"name": "ERP Development", "description": "Enterprise Resource Planning system development", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Development", "keywords": "erp,enterprise,resource planning,business management,inventory", "unit": "Hours"},
        {"name": "Cloud Migration", "description": "Cloud infrastructure migration services", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Cloud", "keywords": "cloud,migration,aws,azure,google cloud,infrastructure,deployment", "unit": "Hours"},
        {"name": "DevOps Services", "description": "DevOps implementation and automation", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Operations", "keywords": "devops,automation,ci cd,deployment,docker,kubernetes,jenkins", "unit": "Hours"},
        {"name": "IT Security Consulting", "description": "Cybersecurity consulting and implementation", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Security", "keywords": "security,cybersecurity,penetration testing,vulnerability,firewall,encryption", "unit": "Hours"},
        {"name": "Network Setup", "description": "Computer network installation and configuration", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Infrastructure", "keywords": "network,lan,wan,wifi,router,switch,configuration", "unit": "Hours"},
        {"name": "IT Support", "description": "Technical support and maintenance services", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Support", "keywords": "support,technical,maintenance,troubleshooting,help desk,remote support", "unit": "Hours"},
        {"name": "Data Analytics", "description": "Business intelligence and data analysis services", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Analytics", "keywords": "data,analytics,business intelligence,reporting,dashboard,visualization", "unit": "Hours"},
        {"name": "Machine Learning", "description": "AI and machine learning solution development", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "AI", "keywords": "machine learning,ai,artificial intelligence,deep learning,neural networks,python", "unit": "Hours"},
        {"name": "Blockchain Development", "description": "Blockchain and cryptocurrency solutions", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Blockchain", "keywords": "blockchain,cryptocurrency,smart contracts,ethereum,bitcoin,defi", "unit": "Hours"},
        {"name": "UI/UX Design", "description": "User interface and user experience design", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Design", "keywords": "ui,ux,user interface,user experience,design,wireframe,prototype", "unit": "Hours"},
        {"name": "Quality Assurance", "description": "Software testing and quality assurance services", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Testing", "keywords": "qa,testing,quality assurance,automation testing,manual testing,bug testing", "unit": "Hours"},
        {"name": "System Integration", "description": "Enterprise system integration services", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Integration", "keywords": "integration,system,enterprise,middleware,api integration,data sync", "unit": "Hours"},
        {"name": "IT Training", "description": "Technology training and skill development", "sac_code": "998314", "gst_rate": 18.0, "category": "IT_Services", "subcategory": "Training", "keywords": "training,education,skill development,workshop,certification,technical training", "unit": "Hours"},

        # Digital Marketing Services (SAC: 998399 - 18% GST)
        {"name": "Digital Marketing", "description": "Comprehensive digital marketing campaigns", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Digital", "keywords": "digital marketing,online marketing,campaign,strategy,branding", "unit": "Hours"},
        {"name": "SEO Services", "description": "Search engine optimization services", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "SEO", "keywords": "seo,search engine optimization,ranking,keywords,google,organic traffic", "unit": "Hours"},
        {"name": "Social Media Marketing", "description": "Social media strategy and management", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Social Media", "keywords": "social media,facebook,instagram,twitter,linkedin,content marketing", "unit": "Hours"},
        {"name": "Google Ads Management", "description": "Google AdWords campaign management", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "PPC", "keywords": "google ads,adwords,ppc,pay per click,advertising,campaign management", "unit": "Hours"},
        {"name": "Content Marketing", "description": "Content strategy and creation services", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Content", "keywords": "content marketing,blog,articles,content strategy,copywriting", "unit": "Hours"},
        {"name": "Email Marketing", "description": "Email campaign design and management", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Email", "keywords": "email marketing,newsletter,campaign,automation,mailchimp", "unit": "Hours"},
        {"name": "Influencer Marketing", "description": "Influencer outreach and campaign management", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Influencer", "keywords": "influencer,marketing,outreach,collaboration,brand ambassador", "unit": "Hours"},
        {"name": "Video Marketing", "description": "Video content creation and promotion", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Video", "keywords": "video marketing,youtube,video content,promotional videos,video ads", "unit": "Hours"},
        {"name": "Marketing Analytics", "description": "Marketing performance analysis and reporting", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Analytics", "keywords": "marketing analytics,roi,performance,reporting,google analytics", "unit": "Hours"},
        {"name": "Brand Strategy", "description": "Brand development and positioning services", "sac_code": "998399", "gst_rate": 18.0, "category": "Marketing_Services", "subcategory": "Branding", "keywords": "brand strategy,positioning,brand development,market research", "unit": "Hours"},

        # Creative Services (SAC: 998399 - 18% GST)
        {"name": "Graphic Design", "description": "Visual design and graphic creation services", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Design", "keywords": "graphic design,logo,branding,visual design,creative,artwork", "unit": "Hours"},
        {"name": "Logo Design", "description": "Professional logo and brand identity design", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Design", "keywords": "logo,brand identity,corporate identity,design,visual branding", "unit": "Nos"},
        {"name": "Web Design", "description": "Website design and user interface creation", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Design", "keywords": "web design,website design,ui design,responsive design,layout", "unit": "Hours"},
        {"name": "Print Design", "description": "Print materials and publication design", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Design", "keywords": "print design,brochure,flyer,poster,business card,catalog", "unit": "Hours"},
        {"name": "Video Production", "description": "Video creation and post-production services", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Video", "keywords": "video production,filming,editing,post production,commercial", "unit": "Hours"},
        {"name": "Photography", "description": "Professional photography services", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Photography", "keywords": "photography,photo shoot,product photography,portrait,commercial photography", "unit": "Hours"},
        {"name": "Animation", "description": "2D and 3D animation services", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Animation", "keywords": "animation,2d animation,3d animation,motion graphics,explainer video", "unit": "Hours"},
        {"name": "Illustration", "description": "Custom illustration and artwork creation", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Illustration", "keywords": "illustration,artwork,custom art,digital illustration,vector art", "unit": "Hours"},
        {"name": "Content Writing", "description": "Professional content and copywriting services", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Writing", "keywords": "content writing,copywriting,blog writing,website content,articles", "unit": "Words"},
        {"name": "Voice Over", "description": "Professional voice over and narration services", "sac_code": "998399", "gst_rate": 18.0, "category": "Creative_Services", "subcategory": "Audio", "keywords": "voice over,narration,audio,voice recording,commercial voice", "unit": "Minutes"},

        # Professional Services (SAC: 998399 - 18% GST)
        {"name": "Business Consulting", "description": "Strategic business consulting and advisory", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Consulting", "keywords": "business consulting,strategy,advisory,management consulting,business plan", "unit": "Hours"},
        {"name": "Financial Consulting", "description": "Financial planning and advisory services", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Finance", "keywords": "financial consulting,planning,investment,finance,accounting,bookkeeping", "unit": "Hours"},
        {"name": "Legal Services", "description": "Legal consultation and documentation", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Legal", "keywords": "legal,lawyer,attorney,legal advice,documentation,contracts", "unit": "Hours"},
        {"name": "HR Consulting", "description": "Human resources consulting and recruitment", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "HR", "keywords": "hr,human resources,recruitment,hiring,employee,consulting", "unit": "Hours"},
        {"name": "Project Management", "description": "Project planning and management services", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Management", "keywords": "project management,planning,coordination,project execution,pmp", "unit": "Hours"},
        {"name": "Market Research", "description": "Market analysis and research services", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Research", "keywords": "market research,analysis,survey,consumer research,market study", "unit": "Hours"},
        {"name": "Training & Development", "description": "Corporate training and skill development", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Training", "keywords": "training,development,corporate training,workshop,skill development", "unit": "Hours"},
        {"name": "Translation Services", "description": "Document and content translation", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Translation", "keywords": "translation,language,document translation,interpretation,localization", "unit": "Words"},
        {"name": "Data Entry", "description": "Data entry and processing services", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Data", "keywords": "data entry,data processing,typing,data conversion,digitization", "unit": "Hours"},
        {"name": "Virtual Assistant", "description": "Virtual administrative assistance services", "sac_code": "998399", "gst_rate": 18.0, "category": "Professional_Services", "subcategory": "Admin", "keywords": "virtual assistant,admin,administrative,support,remote assistance", "unit": "Hours"},

        # Maintenance & Repair Services (SAC: 997212 - 18% GST)
        {"name": "Computer Repair", "description": "Computer hardware repair and maintenance", "sac_code": "997212", "gst_rate": 18.0, "category": "Technical_Services", "subcategory": "Repair", "keywords": "computer repair,hardware,maintenance,laptop repair,desktop repair", "unit": "Hours"},
        {"name": "Printer Repair", "description": "Printer and scanner repair services", "sac_code": "997212", "gst_rate": 18.0, "category": "Technical_Services", "subcategory": "Repair", "keywords": "printer repair,scanner repair,office equipment,printing", "unit": "Hours"},
        {"name": "Mobile Repair", "description": "Smartphone and tablet repair services", "sac_code": "997212", "gst_rate": 18.0, "category": "Technical_Services", "subcategory": "Repair", "keywords": "mobile repair,smartphone repair,tablet repair,screen replacement", "unit": "Hours"},
        {"name": "Server Maintenance", "description": "Server hardware maintenance and support", "sac_code": "997212", "gst_rate": 18.0, "category": "Technical_Services", "subcategory": "Maintenance", "keywords": "server maintenance,hardware,server support,infrastructure", "unit": "Hours"},
        {"name": "Network Maintenance", "description": "Network infrastructure maintenance", "sac_code": "997212", "gst_rate": 18.0, "category": "Technical_Services", "subcategory": "Maintenance", "keywords": "network maintenance,infrastructure,router,switch,wifi", "unit": "Hours"},

        # Construction Services (SAC: 995411 - 12% GST)
        {"name": "Building Construction", "description": "Residential and commercial construction", "sac_code": "995411", "gst_rate": 12.0, "category": "Construction", "subcategory": "Building", "keywords": "construction,building,residential,commercial,contractor", "unit": "Sq Ft"},
        {"name": "Interior Design", "description": "Interior design and decoration services", "sac_code": "995411", "gst_rate": 12.0, "category": "Construction", "subcategory": "Interior", "keywords": "interior design,decoration,home design,office design,furnishing", "unit": "Sq Ft"},
        {"name": "Renovation", "description": "Building renovation and remodeling", "sac_code": "995411", "gst_rate": 12.0, "category": "Construction", "subcategory": "Renovation", "keywords": "renovation,remodeling,refurbishment,home improvement", "unit": "Sq Ft"},
        {"name": "Plumbing", "description": "Plumbing installation and repair", "sac_code": "995411", "gst_rate": 12.0, "category": "Construction", "subcategory": "Plumbing", "keywords": "plumbing,pipe,water,drainage,installation,repair", "unit": "Hours"},
        {"name": "Electrical Work", "description": "Electrical installation and maintenance", "sac_code": "995411", "gst_rate": 12.0, "category": "Construction", "subcategory": "Electrical", "keywords": "electrical,wiring,installation,electrician,power", "unit": "Hours"},

        # Healthcare Services (SAC: 998311 - 5% GST)
        {"name": "Medical Consultation", "description": "Doctor consultation and medical advice", "sac_code": "998311", "gst_rate": 5.0, "category": "Healthcare", "subcategory": "Consultation", "keywords": "medical,doctor,consultation,healthcare,medical advice", "unit": "Hours"},
        {"name": "Physiotherapy", "description": "Physical therapy and rehabilitation", "sac_code": "998311", "gst_rate": 5.0, "category": "Healthcare", "subcategory": "Therapy", "keywords": "physiotherapy,physical therapy,rehabilitation,exercise therapy", "unit": "Sessions"},
        {"name": "Nursing Care", "description": "Professional nursing and care services", "sac_code": "998311", "gst_rate": 5.0, "category": "Healthcare", "subcategory": "Nursing", "keywords": "nursing,care,patient care,home nursing,medical care", "unit": "Hours"},
        {"name": "Dental Services", "description": "Dental examination and treatment", "sac_code": "998311", "gst_rate": 5.0, "category": "Healthcare", "subcategory": "Dental", "keywords": "dental,dentist,teeth,oral health,dental care", "unit": "Hours"},

        # Education Services (SAC: 998321 - 0% GST)
        {"name": "Online Tutoring", "description": "Online educational tutoring services", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Tutoring", "keywords": "tutoring,education,online learning,teaching,academic", "unit": "Hours"},
        {"name": "Skill Training", "description": "Professional skill development training", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Training", "keywords": "skill training,professional development,certification,course", "unit": "Hours"},
        {"name": "Language Classes", "description": "Foreign language learning classes", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Language", "keywords": "language,english,hindi,foreign language,classes", "unit": "Hours"},
        {"name": "Music Lessons", "description": "Music instrument and vocal lessons", "sac_code": "998321", "gst_rate": 0.0, "category": "Education", "subcategory": "Music", "keywords": "music,lessons,instrument,vocal,guitar,piano", "unit": "Hours"},

        # Security Services (SAC: 997311 - 18% GST)
        {"name": "Security Guard", "description": "Physical security guard services", "sac_code": "997311", "gst_rate": 18.0, "category": "Security_Services", "subcategory": "Physical", "keywords": "security,guard,protection,safety,surveillance", "unit": "Hours"},
        {"name": "CCTV Installation", "description": "CCTV camera installation and monitoring", "sac_code": "997311", "gst_rate": 18.0, "category": "Security_Services", "subcategory": "CCTV", "keywords": "cctv,camera,surveillance,monitoring,security system", "unit": "Nos"},
        {"name": "Alarm System", "description": "Security alarm system installation", "sac_code": "997311", "gst_rate": 18.0, "category": "Security_Services", "subcategory": "Alarm", "keywords": "alarm,security system,burglar alarm,fire alarm", "unit": "Nos"},

        # Transportation Services (SAC: 996511 - 5% GST)
        {"name": "Taxi Service", "description": "Taxi and cab transportation services", "sac_code": "996511", "gst_rate": 5.0, "category": "Transportation", "subcategory": "Taxi", "keywords": "taxi,cab,transport,travel,ride", "unit": "Km"},
        {"name": "Delivery Service", "description": "Package and goods delivery services", "sac_code": "996511", "gst_rate": 5.0, "category": "Transportation", "subcategory": "Delivery", "keywords": "delivery,courier,shipping,logistics,package", "unit": "Nos"},
        {"name": "Moving Service", "description": "Household and office relocation services", "sac_code": "996511", "gst_rate": 5.0, "category": "Transportation", "subcategory": "Moving", "keywords": "moving,relocation,shifting,packing,transportation", "unit": "Hours"},

        # Cleaning Services (SAC: 997321 - 18% GST)
        {"name": "House Cleaning", "description": "Residential cleaning and maintenance", "sac_code": "997321", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "Cleaning", "keywords": "cleaning,house cleaning,maid,domestic,housekeeping", "unit": "Hours"},
        {"name": "Office Cleaning", "description": "Commercial office cleaning services", "sac_code": "997321", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "Cleaning", "keywords": "office cleaning,commercial cleaning,janitorial,workplace", "unit": "Hours"},
        {"name": "Carpet Cleaning", "description": "Carpet and upholstery cleaning", "sac_code": "997321", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "Cleaning", "keywords": "carpet cleaning,upholstery,rug cleaning,fabric cleaning", "unit": "Sq Ft"},
        {"name": "Window Cleaning", "description": "Window and glass cleaning services", "sac_code": "997321", "gst_rate": 18.0, "category": "Maintenance_Services", "subcategory": "Cleaning", "keywords": "window cleaning,glass cleaning,building maintenance", "unit": "Sq Ft"},

        # Beauty & Wellness (SAC: 997331 - 18% GST)
        {"name": "Hair Cutting", "description": "Hair cutting and styling services", "sac_code": "997331", "gst_rate": 18.0, "category": "Beauty_Services", "subcategory": "Hair", "keywords": "hair cut,styling,salon,barber,grooming", "unit": "Nos"},
        {"name": "Makeup Service", "description": "Professional makeup and beauty services", "sac_code": "997331", "gst_rate": 18.0, "category": "Beauty_Services", "subcategory": "Makeup", "keywords": "makeup,beauty,cosmetics,bridal makeup,party makeup", "unit": "Hours"},
        {"name": "Spa Service", "description": "Spa and wellness treatment services", "sac_code": "997331", "gst_rate": 18.0, "category": "Beauty_Services", "subcategory": "Spa", "keywords": "spa,wellness,massage,relaxation,therapy", "unit": "Hours"},
        {"name": "Manicure Pedicure", "description": "Nail care and beauty services", "sac_code": "997331", "gst_rate": 18.0, "category": "Beauty_Services", "subcategory": "Nails", "keywords": "manicure,pedicure,nail care,nail art,beauty", "unit": "Nos"},

        # Food Services (SAC: 996331 - 5% GST)
        {"name": "Catering Service", "description": "Event catering and food services", "sac_code": "996331", "gst_rate": 5.0, "category": "Food_Services", "subcategory": "Catering", "keywords": "catering,food,event,party,wedding,buffet", "unit": "Nos"},
        {"name": "Restaurant Service", "description": "Restaurant dining and food services", "sac_code": "996331", "gst_rate": 5.0, "category": "Food_Services", "subcategory": "Restaurant", "keywords": "restaurant,dining,food,meal,cuisine", "unit": "Nos"},
        {"name": "Food Delivery", "description": "Food delivery and takeaway services", "sac_code": "996331", "gst_rate": 5.0, "category": "Food_Services", "subcategory": "Delivery", "keywords": "food delivery,takeaway,home delivery,online food", "unit": "Nos"},

        # Event Management (SAC: 998399 - 18% GST)
        {"name": "Event Planning", "description": "Event planning and management services", "sac_code": "998399", "gst_rate": 18.0, "category": "Event_Services", "subcategory": "Planning", "keywords": "event planning,wedding,party,conference,event management", "unit": "Hours"},
        {"name": "Wedding Planning", "description": "Wedding ceremony planning and coordination", "sac_code": "998399", "gst_rate": 18.0, "category": "Event_Services", "subcategory": "Wedding", "keywords": "wedding planning,marriage,ceremony,reception,bridal", "unit": "Hours"},
        {"name": "Conference Management", "description": "Corporate conference and meeting management", "sac_code": "998399", "gst_rate": 18.0, "category": "Event_Services", "subcategory": "Corporate", "keywords": "conference,meeting,corporate event,seminar,workshop", "unit": "Hours"},

        # Real Estate Services (SAC: 997211 - 18% GST)
        {"name": "Property Management", "description": "Real estate property management services", "sac_code": "997211", "gst_rate": 18.0, "category": "Real_Estate", "subcategory": "Management", "keywords": "property management,real estate,rental,property", "unit": "Hours"},
        {"name": "Real Estate Broker", "description": "Property buying and selling brokerage", "sac_code": "997211", "gst_rate": 18.0, "category": "Real_Estate", "subcategory": "Brokerage", "keywords": "real estate,broker,property,buying,selling", "unit": "Hours"},
        {"name": "Property Valuation", "description": "Property assessment and valuation services", "sac_code": "997211", "gst_rate": 18.0, "category": "Real_Estate", "subcategory": "Valuation", "keywords": "property valuation,assessment,appraisal,real estate", "unit": "Hours"},

        # Financial Services (SAC: 997311 - 18% GST)
        {"name": "Accounting Service", "description": "Bookkeeping and accounting services", "sac_code": "998313", "gst_rate": 18.0, "category": "Financial_Services", "subcategory": "Accounting", "keywords": "accounting,bookkeeping,finance,tax,audit", "unit": "Hours"},
        {"name": "Tax Preparation", "description": "Income tax return preparation", "sac_code": "998313", "gst_rate": 18.0, "category": "Financial_Services", "subcategory": "Tax", "keywords": "tax,income tax,return,preparation,filing", "unit": "Nos"},
        {"name": "Financial Planning", "description": "Personal financial planning and investment", "sac_code": "998313", "gst_rate": 18.0, "category": "Financial_Services", "subcategory": "Planning", "keywords": "financial planning,investment,portfolio,wealth management", "unit": "Hours"},
        {"name": "Insurance Service", "description": "Insurance consultation and policy services", "sac_code": "998313", "gst_rate": 18.0, "category": "Financial_Services", "subcategory": "Insurance", "keywords": "insurance,policy,life insurance,health insurance", "unit": "Hours"},

        # Automotive Services (SAC: 997212 - 18% GST)
        {"name": "Car Repair", "description": "Automobile repair and maintenance", "sac_code": "997212", "gst_rate": 18.0, "category": "Automotive", "subcategory": "Repair", "keywords": "car repair,automobile,vehicle,maintenance,mechanic", "unit": "Hours"},
        {"name": "Car Wash", "description": "Vehicle cleaning and detailing services", "sac_code": "997212", "gst_rate": 18.0, "category": "Automotive", "subcategory": "Cleaning", "keywords": "car wash,vehicle cleaning,detailing,auto care", "unit": "Nos"},
        {"name": "Tire Service", "description": "Tire installation and repair services", "sac_code": "997212", "gst_rate": 18.0, "category": "Automotive", "subcategory": "Tire", "keywords": "tire,wheel,puncture,tire repair,installation", "unit": "Nos"},

        # Pet Services (SAC: 998399 - 18% GST)
        {"name": "Pet Grooming", "description": "Pet grooming and care services", "sac_code": "998399", "gst_rate": 18.0, "category": "Pet_Services", "subcategory": "Grooming", "keywords": "pet grooming,dog,cat,animal care,pet care", "unit": "Nos"},
        {"name": "Veterinary Service", "description": "Animal health and veterinary care", "sac_code": "998399", "gst_rate": 18.0, "category": "Pet_Services", "subcategory": "Veterinary", "keywords": "veterinary,vet,animal health,pet health", "unit": "Hours"},
        {"name": "Pet Training", "description": "Pet behavior training and obedience", "sac_code": "998399", "gst_rate": 18.0, "category": "Pet_Services", "subcategory": "Training", "keywords": "pet training,dog training,obedience,behavior", "unit": "Hours"},

        # Photography Services (SAC: 998399 - 18% GST)
        {"name": "Wedding Photography", "description": "Wedding ceremony photography services", "sac_code": "998399", "gst_rate": 18.0, "category": "Photography", "subcategory": "Wedding", "keywords": "wedding photography,marriage,ceremony,bridal,photographer", "unit": "Hours"},
        {"name": "Product Photography", "description": "Commercial product photography", "sac_code": "998399", "gst_rate": 18.0, "category": "Photography", "subcategory": "Product", "keywords": "product photography,commercial,e-commerce,catalog", "unit": "Hours"},
        {"name": "Portrait Photography", "description": "Personal and family portrait photography", "sac_code": "998399", "gst_rate": 18.0, "category": "Photography", "subcategory": "Portrait", "keywords": "portrait,family photo,personal,studio photography", "unit": "Hours"},

        # Entertainment Services (SAC: 998399 - 18% GST)
        {"name": "DJ Service", "description": "Music and DJ services for events", "sac_code": "998399", "gst_rate": 18.0, "category": "Entertainment", "subcategory": "Music", "keywords": "dj,music,party,event,entertainment", "unit": "Hours"},
        {"name": "Live Music", "description": "Live musical performance services", "sac_code": "998399", "gst_rate": 18.0, "category": "Entertainment", "subcategory": "Music", "keywords": "live music,band,performance,concert,musician", "unit": "Hours"},
        {"name": "Dance Performance", "description": "Dance and choreography services", "sac_code": "998399", "gst_rate": 18.0, "category": "Entertainment", "subcategory": "Dance", "keywords": "dance,choreography,performance,cultural,traditional", "unit": "Hours"},

        # Fitness Services (SAC: 998399 - 18% GST)
        {"name": "Personal Training", "description": "Personal fitness training services", "sac_code": "998399", "gst_rate": 18.0, "category": "Fitness", "subcategory": "Training", "keywords": "personal training,fitness,gym,workout,exercise", "unit": "Hours"},
        {"name": "Yoga Classes", "description": "Yoga instruction and wellness classes", "sac_code": "998399", "gst_rate": 18.0, "category": "Fitness", "subcategory": "Yoga", "keywords": "yoga,meditation,wellness,fitness,health", "unit": "Hours"},
        {"name": "Gym Membership", "description": "Fitness center and gym services", "sac_code": "998399", "gst_rate": 18.0, "category": "Fitness", "subcategory": "Gym", "keywords": "gym,fitness center,workout,equipment,membership", "unit": "Months"},

        # Agriculture Services (SAC: 998211 - 12% GST)
        {"name": "Farming Consultation", "description": "Agricultural consulting and farm management", "sac_code": "998211", "gst_rate": 12.0, "category": "Agriculture", "subcategory": "Consulting", "keywords": "farming,agriculture,crop,consultation,farm management", "unit": "Hours"},
        {"name": "Landscaping", "description": "Garden and landscape design services", "sac_code": "998211", "gst_rate": 12.0, "category": "Agriculture", "subcategory": "Landscaping", "keywords": "landscaping,garden,lawn,plants,landscape design", "unit": "Sq Ft"},
        {"name": "Pest Control", "description": "Agricultural and residential pest control", "sac_code": "998211", "gst_rate": 12.0, "category": "Agriculture", "subcategory": "Pest Control", "keywords": "pest control,insects,termite,fumigation,extermination", "unit": "Sq Ft"},

        # Telecommunications (SAC: 998414 - 18% GST)
        {"name": "Telecom Installation", "description": "Telecommunications equipment installation", "sac_code": "998414", "gst_rate": 18.0, "category": "Telecommunications", "subcategory": "Installation", "keywords": "telecom,installation,phone,internet,network", "unit": "Hours"},
        {"name": "Internet Service", "description": "Internet connectivity and broadband services", "sac_code": "998414", "gst_rate": 18.0, "category": "Telecommunications", "subcategory": "Internet", "keywords": "internet,broadband,wifi,connectivity,isp", "unit": "Months"},
        {"name": "Phone Service", "description": "Telephone and communication services", "sac_code": "998414", "gst_rate": 18.0, "category": "Telecommunications", "subcategory": "Phone", "keywords": "phone,telephone,communication,mobile,landline", "unit": "Months"},
    ]
    
    return services

def seed_comprehensive_database():
    """Seed the database with comprehensive service list"""
    
    try:
        # Get database session
        db = next(get_db())
        
        print("🌱 Starting comprehensive master services seeding...")
        
        # Clear existing services
        existing_count = db.query(MasterService).count()
        if existing_count > 0:
            db.query(MasterService).delete()
            db.commit()
            print(f"   Cleared {existing_count} existing services")
        
        # Get comprehensive services list
        services_data = get_comprehensive_services()
        
        # Add all services
        added_count = 0
        categories_count = {}
        
        for service_data in services_data:
            # Add business_type if not specified
            if "business_type" not in service_data:
                service_data["business_type"] = "service"
            
            # Add is_active if not specified
            if "is_active" not in service_data:
                service_data["is_active"] = True
                
            # Track categories
            category = service_data["category"]
            categories_count[category] = categories_count.get(category, 0) + 1
            
            # Create service
            service = MasterService(**service_data)
            db.add(service)
            added_count += 1
        
        # Commit all services
        db.commit()
        db.close()
        
        print(f"✅ Successfully seeded {added_count} master services!")
        print(f"\n📊 Services by category:")
        for category, count in sorted(categories_count.items()):
            print(f"   {category.replace('_', ' ')}: {count} services")
        
        # Verify the seeding
        db = next(get_db())
        final_count = db.query(MasterService).count()
        active_count = db.query(MasterService).filter(MasterService.is_active == True).count()
        db.close()
        
        print(f"\n🔍 Final verification:")
        print(f"   Total services in database: {final_count}")
        print(f"   Active services: {active_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 COMPREHENSIVE MASTER SERVICES DATABASE SEEDER")
    print("=" * 60)
    
    success = seed_comprehensive_database()
    
    if success:
        print("\n🎉 Seeding completed successfully!")
        print("   Your ServiceTemplate AI suggestions are now powered by")
        print("   a comprehensive database of business services!")
    else:
        print("\n💥 Seeding failed. Please check the errors above.")
    
    print("=" * 60)
