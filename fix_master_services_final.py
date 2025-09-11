#!/usr/bin/env python3
"""
Final fix for master_services table - recreate using ORM
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, DATABASE_URL
from models import MasterService

def recreate_master_services():
    """Drop and recreate master_services table using ORM"""
    print("Recreating master_services table using ORM...")
    
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Drop the existing table
    try:
        MasterService.__table__.drop(engine, checkfirst=True)
        print("Dropped existing master_services table")
    except Exception as e:
        print(f"Could not drop table (may not exist): {e}")
    
    # Create the table using ORM
    try:
        Base.metadata.create_all(bind=engine, tables=[MasterService.__table__])
        print("Created master_services table using ORM")
    except Exception as e:
        print(f"Error creating table: {e}")
        return False
    
    # Verify the table was created
    with engine.connect() as conn:
        result = conn.exec_driver_sql("PRAGMA table_info(master_services)")
        columns = result.fetchall()
        print("New table structure:")
        for col in columns:
            print(f"  {col[1]} {col[2]} (NOT NULL: {col[3]})")
    
    return True

def seed_data():
    """Add sample data using ORM"""
    print("Seeding data using ORM...")
    
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        count = db.query(MasterService).count()
        if count > 0:
            print(f"Table already has {count} records. Skipping seed.")
            return True
        
        # Sample services
        services = [
            MasterService(
                name="Web Development",
                description="Custom website development and programming services",
                sac_code="998314",
                gst_rate=18.0,
                hsn_code="998314",
                category="IT_Services",
                subcategory="Development",
                business_type="service",
                keywords="website,web,development,programming,coding,html,css,javascript,react,angular,php,python",
                tags="tech,programming,website",
                unit="Hours",
                is_active=True,
                usage_count=0
            ),
            MasterService(
                name="Mobile App Development",
                description="iOS and Android mobile application development",
                sac_code="998314",
                gst_rate=18.0,
                hsn_code="998314",
                category="IT_Services",
                subcategory="Development",
                business_type="service",
                keywords="mobile,app,application,ios,android,flutter,react native,development",
                tags="tech,mobile,app",
                unit="Hours",
                is_active=True,
                usage_count=0
            ),
            MasterService(
                name="Digital Marketing",
                description="Online marketing and digital advertising services",
                sac_code="998399",
                gst_rate=18.0,
                category="Marketing_Services",
                subcategory="Digital",
                business_type="service",
                keywords="digital marketing,online marketing,seo,sem,social media,advertising,google ads,facebook ads",
                tags="marketing,digital,advertising",
                unit="Campaign",
                is_active=True,
                usage_count=0
            ),
            MasterService(
                name="Graphic Design",
                description="Logo design, branding, and visual design services",
                sac_code="998399",
                gst_rate=18.0,
                category="Creative_Services",
                subcategory="Design",
                business_type="service",
                keywords="graphic design,logo,branding,visual design,illustration,creative",
                tags="design,creative,visual",
                unit="Design",
                is_active=True,
                usage_count=0
            ),
            MasterService(
                name="Content Writing",
                description="Website content, blog posts, and copywriting services",
                sac_code="998399",
                gst_rate=18.0,
                category="Creative_Services",
                subcategory="Writing",
                business_type="service",
                keywords="content writing,copywriting,blog,articles,seo content,website content",
                tags="writing,content,copy",
                unit="Article",
                is_active=True,
                usage_count=0
            )
        ]
        
        for service in services:
            db.add(service)
        
        db.commit()
        print(f"Added {len(services)} services successfully")
        
        # Verify the data
        count = db.query(MasterService).count()
        print(f"Total services in database: {count}")
        
        # Test search
        web_services = db.query(MasterService).filter(
            MasterService.name.like('%Web%')
        ).all()
        print(f"Services matching 'Web': {len(web_services)}")
        
        return True
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Master Services Final Fix ===")
    
    if recreate_master_services():
        if seed_data():
            print("✅ Master services table fixed and seeded successfully!")
        else:
            print("❌ Failed to seed data")
    else:
        print("❌ Failed to recreate table")

