#!/usr/bin/env python3
"""
Enhanced service seeding script - Creates SPECIFIC services instead of categories
This addresses the user's concern about getting generic categories instead of specific services
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import MasterService

def get_specific_services_data():
    """
    Return comprehensive list of SPECIFIC services (not categories)
    Each service is actionable and can be directly used in invoices
    """
    
    return [
        # ===== WEB DEVELOPMENT - SPECIFIC SERVICES =====
        {
            "name": "WordPress Website Development",
            "description": "Custom WordPress website with theme customization and plugins",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Web_Development", 
            "business_type": "service",
            "keywords": "wordpress,website,cms,blog,custom theme,plugins,wp",
            "tags": "website,wordpress,cms",
            "unit": "Nos"
        },
        {
            "name": "E-commerce Website Development",
            "description": "Complete online store with payment gateway and inventory management",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Web_Development",
            "business_type": "service", 
            "keywords": "ecommerce,online store,shopping cart,payment gateway,woocommerce,shopify",
            "tags": "ecommerce,store,shopping",
            "unit": "Nos"
        },
        {
            "name": "Corporate Website Development",
            "description": "Professional corporate website with company profile and services",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Web_Development",
            "business_type": "service",
            "keywords": "corporate,company,business website,professional,portfolio",
            "tags": "corporate,business,professional",
            "unit": "Nos"
        },
        {
            "name": "Custom Web Application Development",
            "description": "Bespoke web application with custom functionality and database",
            "sac_code": "998314", 
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Web_Development",
            "business_type": "service",
            "keywords": "web app,custom application,saas,dashboard,portal",
            "tags": "webapp,custom,application",
            "unit": "Nos"
        },
        {
            "name": "Landing Page Development",
            "description": "High-converting single page website for marketing campaigns",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services", 
            "subcategory": "Web_Development",
            "business_type": "service",
            "keywords": "landing page,single page,marketing,conversion,campaign",
            "tags": "landing,marketing,page",
            "unit": "Nos"
        },
        {
            "name": "Website Maintenance & Updates",
            "description": "Ongoing website maintenance, updates, and technical support",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Web_Development",
            "business_type": "service",
            "keywords": "maintenance,updates,support,bug fixes,website care",
            "tags": "maintenance,support,updates",
            "unit": "Hours"
        },

        # ===== MOBILE APP DEVELOPMENT - SPECIFIC SERVICES =====
        {
            "name": "Android App Development",
            "description": "Native Android application development with Google Play Store deployment",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Mobile_Development",
            "business_type": "service",
            "keywords": "android,mobile app,kotlin,java,play store,native app",
            "tags": "android,mobile,app",
            "unit": "Nos"
        },
        {
            "name": "iOS App Development", 
            "description": "Native iOS application development with App Store deployment",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Mobile_Development",
            "business_type": "service",
            "keywords": "ios,iphone,ipad,swift,app store,native app",
            "tags": "ios,mobile,app",
            "unit": "Nos"
        },
        {
            "name": "Cross-Platform App Development",
            "description": "React Native or Flutter app for both Android and iOS platforms",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Mobile_Development", 
            "business_type": "service",
            "keywords": "cross platform,react native,flutter,hybrid app,multi platform",
            "tags": "crossplatform,hybrid,app",
            "unit": "Nos"
        },

        # ===== DIGITAL MARKETING - SPECIFIC SERVICES =====
        {
            "name": "Search Engine Optimization (SEO)",
            "description": "Complete SEO audit, keyword research, and organic ranking improvement",
            "sac_code": "998315",
            "gst_rate": 18.0,
            "category": "Digital_Marketing",
            "subcategory": "SEO_Services",
            "business_type": "service",
            "keywords": "seo,search engine optimization,google ranking,keywords,organic traffic",
            "tags": "seo,marketing,organic",
            "unit": "Months"
        },
        {
            "name": "Google Ads Campaign Management",
            "description": "Complete Google Ads setup, optimization, and performance management",
            "sac_code": "998315", 
            "gst_rate": 18.0,
            "category": "Digital_Marketing",
            "subcategory": "PPC_Services",
            "business_type": "service",
            "keywords": "google ads,ppc,paid advertising,adwords,campaign management",
            "tags": "googleads,ppc,advertising",
            "unit": "Months"
        },
        {
            "name": "Social Media Marketing",
            "description": "Complete social media strategy, content creation, and community management",
            "sac_code": "998315",
            "gst_rate": 18.0,
            "category": "Digital_Marketing",
            "subcategory": "Social_Media",
            "business_type": "service",
            "keywords": "social media,facebook,instagram,linkedin,content marketing,smm",
            "tags": "social,marketing,content",
            "unit": "Months"
        },
        {
            "name": "Content Writing Services",
            "description": "Professional blog posts, website content, and marketing copy writing",
            "sac_code": "998315",
            "gst_rate": 18.0,
            "category": "Digital_Marketing",
            "subcategory": "Content_Services",
            "business_type": "service",
            "keywords": "content writing,blog posts,copywriting,articles,web content",
            "tags": "content,writing,copy",
            "unit": "Articles"
        },

        # ===== DESIGN SERVICES - SPECIFIC SERVICES =====
        {
            "name": "Logo Design & Branding",
            "description": "Custom logo design with complete brand identity package",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "Design_Services",
            "subcategory": "Graphic_Design",
            "business_type": "service",
            "keywords": "logo design,branding,brand identity,graphic design,visual identity",
            "tags": "logo,branding,design",
            "unit": "Nos"
        },
        {
            "name": "UI/UX Design for Web Applications",
            "description": "User interface and experience design for web platforms",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "Design_Services",
            "subcategory": "UI_UX_Design",
            "business_type": "service",
            "keywords": "ui design,ux design,user interface,user experience,web design",
            "tags": "ui,ux,design",
            "unit": "Screens"
        },
        {
            "name": "Mobile App UI/UX Design",
            "description": "User interface and experience design for mobile applications",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "Design_Services",
            "subcategory": "UI_UX_Design", 
            "business_type": "service",
            "keywords": "mobile ui,mobile ux,app design,mobile interface,app experience",
            "tags": "mobile,ui,ux",
            "unit": "Screens"
        },

        # ===== CONSULTING SERVICES - SPECIFIC SERVICES =====
        {
            "name": "Business Strategy Consulting",
            "description": "Strategic business planning, market analysis, and growth strategies",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "Consulting_Services",
            "subcategory": "Business_Consulting",
            "business_type": "service",
            "keywords": "business strategy,consulting,planning,market analysis,growth strategy",
            "tags": "strategy,consulting,business",
            "unit": "Hours"
        },
        {
            "name": "Digital Transformation Consulting",
            "description": "Technology adoption strategy and digital process improvement",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "Consulting_Services", 
            "subcategory": "Technology_Consulting",
            "business_type": "service",
            "keywords": "digital transformation,technology consulting,process improvement,automation",
            "tags": "digital,transformation,consulting",
            "unit": "Hours"
        },

        # ===== TECHNICAL SERVICES - SPECIFIC SERVICES =====
        {
            "name": "Website Performance Optimization",
            "description": "Speed optimization, Core Web Vitals improvement, and performance monitoring",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Technical_Services",
            "business_type": "service",
            "keywords": "performance optimization,speed optimization,core web vitals,website speed",
            "tags": "performance,speed,optimization",
            "unit": "Nos"
        },
        {
            "name": "Database Design & Development",
            "description": "Custom database architecture, design, and implementation",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Database_Services",
            "business_type": "service",
            "keywords": "database design,database development,sql,mysql,postgresql,mongodb",
            "tags": "database,sql,development",
            "unit": "Nos"
        },
        {
            "name": "API Development & Integration",
            "description": "RESTful API development and third-party service integrations",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "API_Services",
            "business_type": "service",
            "keywords": "api development,rest api,api integration,web services,microservices",
            "tags": "api,integration,development",
            "unit": "APIs"
        },

        # ===== MAINTENANCE & SUPPORT - SPECIFIC SERVICES =====
        {
            "name": "Technical Support & Troubleshooting",
            "description": "Ongoing technical support, bug fixes, and system troubleshooting",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Support_Services",
            "business_type": "service",
            "keywords": "technical support,troubleshooting,bug fixes,system support,help desk",
            "tags": "support,troubleshooting,maintenance",
            "unit": "Hours"
        },
        {
            "name": "Server Setup & Configuration",
            "description": "Web server setup, configuration, and deployment services",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "category": "IT_Services",
            "subcategory": "Infrastructure_Services",
            "business_type": "service",
            "keywords": "server setup,server configuration,deployment,hosting,devops",
            "tags": "server,deployment,hosting",
            "unit": "Nos"
        }
    ]

def seed_specific_services():
    """Seed the database with specific, actionable services"""
    
    print("🚀 SEEDING SPECIFIC SERVICES (Not Categories!)")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # First, let's see what we currently have
        existing_services = db.query(MasterService).count()
        print(f"📊 Current services in database: {existing_services}")
        
        services_data = get_specific_services_data()
        
        added_count = 0
        updated_count = 0
        
        for service_data in services_data:
            # Check if service already exists by name
            existing = db.query(MasterService).filter(
                MasterService.name == service_data["name"]
            ).first()
            
            if existing:
                # Update existing service
                for key, value in service_data.items():
                    setattr(existing, key, value)
                updated_count += 1
                print(f"✏️  Updated: {service_data['name']}")
            else:
                # Create new service
                service = MasterService(**service_data)
                db.add(service)
                added_count += 1
                print(f"✅ Added: {service_data['name']}")
        
        db.commit()
        
        print(f"\n🎉 SEEDING COMPLETE!")
        print(f"📈 Added: {added_count} new services")
        print(f"🔄 Updated: {updated_count} existing services")
        print(f"📊 Total services now: {db.query(MasterService).count()}")
        
        # Show some examples of what we now have
        print(f"\n💡 EXAMPLE SPECIFIC SERVICES:")
        sample_services = db.query(MasterService).filter(
            MasterService.category == "IT_Services"
        ).limit(5).all()
        
        for service in sample_services:
            print(f"   • {service.name}")
            print(f"     Description: {service.description}")
            print(f"     Category: {service.category} > {service.subcategory}")
            print()
        
    except Exception as e:
        print(f"❌ Error seeding services: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_specific_services()
