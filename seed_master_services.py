#!/usr/bin/env python3
"""
Seed script to populate the master_services table with comprehensive service data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import engine
from models import MasterService

def get_master_services_data():
    """Return comprehensive list of Indian business services with SAC codes and GST rates"""
    
    return [
        # IT & Digital Services
        {
            "name": "Web Development",
            "description": "Custom website development and programming services",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Web_Development",
            "business_type": "service",
            "keywords": "website,web,development,programming,coding,html,css,javascript,react,angular,php,python",
            "tags": "technology,digital,programming",
            "unit": "Nos"
        },
        {
            "name": "Mobile App Development",
            "description": "iOS and Android mobile application development",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Mobile_Development",
            "business_type": "service",
            "keywords": "mobile,app,application,ios,android,flutter,react native,development",
            "tags": "technology,mobile,app",
            "unit": "Nos"
        },
        {
            "name": "Software Development",
            "description": "Custom software and application development services",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Software_Development",
            "business_type": "service",
            "keywords": "software,development,programming,application,system,desktop,enterprise",
            "tags": "technology,software,programming",
            "unit": "Nos"
        },
        {
            "name": "Digital Marketing",
            "description": "Online marketing and digital advertising services",
            "sac_code": "998399",
            "gst_rate": 18.0,
            "category": "Marketing_Services",
            "subcategory": "Digital_Marketing",
            "business_type": "service",
            "keywords": "digital marketing,online marketing,seo,sem,social media,advertising,google ads,facebook ads",
            "tags": "marketing,digital,advertising",
            "unit": "Nos"
        },
        {
            "name": "SEO Services",
            "description": "Search Engine Optimization and website ranking services",
            "sac_code": "998399",
            "gst_rate": 18.0,
            "category": "Marketing_Services",
            "subcategory": "SEO",
            "business_type": "service",
            "keywords": "seo,search engine optimization,google ranking,website optimization,keyword research",
            "tags": "marketing,seo,optimization",
            "unit": "Nos"
        },
        {
            "name": "Graphic Design",
            "description": "Logo design, branding, and visual design services",
            "sac_code": "998399",
            "gst_rate": 18.0,
            "category": "Creative_Services",
            "subcategory": "Design",
            "business_type": "service",
            "keywords": "graphic design,logo,branding,visual design,creative,artwork,illustration",
            "tags": "creative,design,visual",
            "unit": "Nos"
        },
        {
            "name": "Content Writing",
            "description": "Website content, blog posts, and copywriting services",
            "sac_code": "998399",
            "gst_rate": 18.0,
            "category": "Creative_Services",
            "subcategory": "Writing",
            "business_type": "service",
            "keywords": "content writing,copywriting,blog,articles,website content,creative writing",
            "tags": "creative,writing,content",
            "unit": "Nos"
        },
        
        # Professional Services
        {
            "name": "Accounting Services",
            "description": "Bookkeeping, financial statements, and accounting services",
            "sac_code": "998212",
            "gst_rate": 18.0,
            "category": "Professional_Services",
            "subcategory": "Accounting",
            "business_type": "service",
            "keywords": "accounting,bookkeeping,financial statements,audit,taxation,ca services",
            "tags": "finance,accounting,professional",
            "unit": "Nos"
        },
        {
            "name": "Tax Consultation",
            "description": "Income tax, GST, and tax planning consultation services",
            "sac_code": "998212",
            "gst_rate": 18.0,
            "category": "Professional_Services",
            "subcategory": "Tax",
            "business_type": "service",
            "keywords": "tax,taxation,income tax,gst,tax planning,tax consultation,ca,chartered accountant",
            "tags": "finance,tax,consultation",
            "unit": "Nos"
        },
        {
            "name": "Legal Advisory",
            "description": "Legal consultation and advisory services",
            "sac_code": "998211",
            "gst_rate": 18.0,
            "category": "Professional_Services",
            "subcategory": "Legal",
            "business_type": "service",
            "keywords": "legal,lawyer,advocate,legal advice,consultation,contract,agreement",
            "tags": "legal,professional,consultation",
            "unit": "Nos"
        },
        {
            "name": "Business Consulting",
            "description": "Management and business strategy consulting services",
            "sac_code": "998213",
            "gst_rate": 18.0,
            "category": "Professional_Services",
            "subcategory": "Consulting",
            "business_type": "service",
            "keywords": "business consulting,management consulting,strategy,business advice,consulting",
            "tags": "consulting,business,professional",
            "unit": "Nos"
        },
        
        # Technical Services
        {
            "name": "Electrical Services",
            "description": "Electrical installation, repair, and maintenance services",
            "sac_code": "995411",
            "gst_rate": 18.0,
            "category": "Technical_Services",
            "subcategory": "Electrical",
            "business_type": "service",
            "keywords": "electrical,electrician,wiring,installation,repair,maintenance,electrical work",
            "tags": "technical,electrical,maintenance",
            "unit": "Nos"
        },
        {
            "name": "Plumbing Services",
            "description": "Plumbing installation, repair, and maintenance services",
            "sac_code": "995412",
            "gst_rate": 18.0,
            "category": "Technical_Services",
            "subcategory": "Plumbing",
            "business_type": "service",
            "keywords": "plumbing,plumber,pipes,water,drainage,installation,repair,maintenance",
            "tags": "technical,plumbing,maintenance",
            "unit": "Nos"
        },
        {
            "name": "HVAC Services",
            "description": "Air conditioning and heating system services",
            "sac_code": "995413",
            "gst_rate": 18.0,
            "category": "Technical_Services",
            "subcategory": "HVAC",
            "business_type": "service",
            "keywords": "hvac,air conditioning,ac,heating,ventilation,installation,repair,maintenance",
            "tags": "technical,hvac,maintenance",
            "unit": "Nos"
        },
        {
            "name": "Construction Services",
            "description": "Building construction and civil engineering services",
            "sac_code": "995131",
            "gst_rate": 18.0,
            "category": "Construction",
            "subcategory": "Building",
            "business_type": "service",
            "keywords": "construction,building,civil,engineering,contractor,renovation,repair",
            "tags": "construction,building,engineering",
            "unit": "Nos"
        },
        
        # Healthcare Services
        {
            "name": "Medical Consultation",
            "description": "Doctor consultation and medical examination services",
            "sac_code": "999211",
            "gst_rate": 0.0,  # Healthcare services are often exempt
            "category": "Healthcare",
            "subcategory": "Medical",
            "business_type": "service",
            "keywords": "medical,doctor,consultation,examination,healthcare,clinic,treatment",
            "tags": "healthcare,medical,consultation",
            "unit": "Nos"
        },
        {
            "name": "Dental Services",
            "description": "Dental examination, treatment, and oral healthcare services",
            "sac_code": "999212",
            "gst_rate": 0.0,
            "category": "Healthcare",
            "subcategory": "Dental",
            "business_type": "service",
            "keywords": "dental,dentist,teeth,oral health,dental treatment,examination",
            "tags": "healthcare,dental,medical",
            "unit": "Nos"
        },
        
        # Education Services
        {
            "name": "Training Services",
            "description": "Professional training and skill development services",
            "sac_code": "999220",
            "gst_rate": 18.0,
            "category": "Education",
            "subcategory": "Training",
            "business_type": "service",
            "keywords": "training,education,skill development,workshop,course,learning",
            "tags": "education,training,development",
            "unit": "Nos"
        },
        {
            "name": "Online Courses",
            "description": "E-learning and online education services",
            "sac_code": "999220",
            "gst_rate": 18.0,
            "category": "Education",
            "subcategory": "Online_Learning",
            "business_type": "service",
            "keywords": "online courses,e-learning,education,digital learning,training,course",
            "tags": "education,online,learning",
            "unit": "Nos"
        },
        
        # Additional Popular Services
        {
            "name": "Photography Services",
            "description": "Event photography and photo editing services",
            "sac_code": "998399",
            "gst_rate": 18.0,
            "category": "Creative_Services",
            "subcategory": "Photography",
            "business_type": "service",
            "keywords": "photography,photographer,photo,pictures,event,wedding,portfolio,editing",
            "tags": "creative,photography,visual",
            "unit": "Nos"
        },
        {
            "name": "Video Production",
            "description": "Video creation, editing, and production services",
            "sac_code": "998399",
            "gst_rate": 18.0,
            "category": "Creative_Services",
            "subcategory": "Video",
            "business_type": "service",
            "keywords": "video,production,editing,filming,videography,video editing,content creation",
            "tags": "creative,video,production",
            "unit": "Nos"
        },
        {
            "name": "Data Entry Services",
            "description": "Data processing and entry services",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Data_Processing",
            "business_type": "service",
            "keywords": "data entry,data processing,typing,data conversion,excel,database",
            "tags": "data,processing,administrative",
            "unit": "Nos"
        },
        {
            "name": "Translation Services",
            "description": "Language translation and localization services",
            "sac_code": "998399",
            "gst_rate": 18.0,
            "category": "Professional_Services",
            "subcategory": "Translation",
            "business_type": "service",
            "keywords": "translation,language,localization,translator,interpretation,multilingual",
            "tags": "language,translation,communication",
            "unit": "Nos"
        },
        {
            "name": "Cleaning Services",
            "description": "Commercial and residential cleaning services",
            "sac_code": "998819",
            "gst_rate": 18.0,
            "category": "Maintenance_Services",
            "subcategory": "Cleaning",
            "business_type": "service",
            "keywords": "cleaning,housekeeping,janitorial,commercial cleaning,residential cleaning",
            "tags": "cleaning,maintenance,services",
            "unit": "Nos"
        },
        {
            "name": "Security Services",
            "description": "Security guard and surveillance services",
            "sac_code": "998611",
            "gst_rate": 18.0,
            "category": "Security_Services",
            "subcategory": "Guard_Services",
            "business_type": "service",
            "keywords": "security,guard,surveillance,protection,safety,security services",
            "tags": "security,protection,services",
            "unit": "Nos"
        }
    ]

def seed_master_services():
    """Populate the master_services table with initial data"""
    
    # First, create all tables
    from database import Base
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Create database session
    db = Session(engine)
    
    try:
        # Check if data already exists
        existing_count = db.query(MasterService).count()
        if existing_count > 0:
            print(f"Master services table already has {existing_count} records. Skipping seed.")
            return
        
        # Get services data
        services_data = get_master_services_data()
        
        # Create MasterService objects
        services = []
        for service_data in services_data:
            service = MasterService(**service_data)
            services.append(service)
        
        # Bulk insert
        db.bulk_save_objects(services)
        db.commit()
        
        print(f"Successfully seeded {len(services)} master services!")
        
        # Print summary by category
        categories = {}
        for service in services_data:
            category = service['category']
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        print("\nServices by category:")
        for category, count in categories.items():
            print(f"  {category.replace('_', ' ')}: {count} services")
            
    except Exception as e:
        print(f"Error seeding master services: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding master services database...")
    seed_master_services()
    print("Done!")
