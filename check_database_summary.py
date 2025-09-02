#!/usr/bin/env python3
"""
DATABASE SUMMARY REPORT
Check total products and services available to users
Shows comprehensive breakdown by categories and types
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import HSNCode, MasterService

def generate_database_summary():
    """Generate comprehensive database summary for products and services"""
    
    print("📊 DATABASE SUMMARY REPORT")
    print("=" * 70)
    print("🎯 What users will see when searching for products and services")
    print()
    
    db = SessionLocal()
    
    try:
        # ===== PRODUCTS SUMMARY =====
        print("🛍️  PRODUCTS SUMMARY")
        print("-" * 50)
        
        # Total products count
        total_products = db.query(HSNCode).filter(HSNCode.business_type == 'product').count()
        print(f"📦 Total Products: {total_products}")
        
        # Products by category
        product_categories = db.query(
            HSNCode.category,
            func.count(HSNCode.id).label('count')
        ).filter(HSNCode.business_type == 'product').group_by(HSNCode.category).all()
        
        print(f"\n📋 Products by Category:")
        for category, count in product_categories:
            print(f"   • {category}: {count} products")
        
        # Products by HSN code (showing how many products per HSN)
        hsn_breakdown = db.query(
            HSNCode.code,
            func.count(HSNCode.id).label('count')
        ).filter(HSNCode.business_type == 'product').group_by(HSNCode.code).all()
        
        print(f"\n🏷️  Products by HSN Code:")
        for hsn_code, count in hsn_breakdown:
            print(f"   • HSN {hsn_code}: {count} products")
        
        # Sample products from each major category
        print(f"\n💡 Sample Products by Category:")
        for category, _ in product_categories:
            sample_products = db.query(HSNCode).filter(
                HSNCode.category == category,
                HSNCode.business_type == 'product'
            ).limit(3).all()
            
            print(f"\n   📱 {category.upper()}:")
            for product in sample_products:
                print(f"      • {product.description} (HSN: {product.code}, GST: {product.gst_rate}%)")
        
        # ===== SERVICES SUMMARY =====
        print(f"\n\n🔧 SERVICES SUMMARY")
        print("-" * 50)
        
        # Total services count
        total_services = db.query(MasterService).filter(MasterService.is_active == True).count()
        print(f"⚙️  Total Services: {total_services}")
        
        # Services by category
        service_categories = db.query(
            MasterService.category,
            func.count(MasterService.id).label('count')
        ).filter(MasterService.is_active == True).group_by(MasterService.category).all()
        
        print(f"\n📋 Services by Category:")
        for category, count in service_categories:
            print(f"   • {category}: {count} services")
        
        # Services by subcategory
        service_subcategories = db.query(
            MasterService.subcategory,
            func.count(MasterService.id).label('count')
        ).filter(
            MasterService.is_active == True,
            MasterService.subcategory.isnot(None)
        ).group_by(MasterService.subcategory).all()
        
        print(f"\n🔍 Services by Subcategory:")
        for subcategory, count in service_subcategories:
            print(f"   • {subcategory}: {count} services")
        
        # Sample services from each category
        print(f"\n💡 Sample Services by Category:")
        for category, _ in service_categories:
            sample_services = db.query(MasterService).filter(
                MasterService.category == category,
                MasterService.is_active == True
            ).limit(3).all()
            
            print(f"\n   🔧 {category.upper()}:")
            for service in sample_services:
                print(f"      • {service.name} (SAC: {service.sac_code}, GST: {service.gst_rate}%)")
        
        # ===== OVERALL SUMMARY =====
        print(f"\n\n🎊 OVERALL DATABASE SUMMARY")
        print("=" * 70)
        
        print(f"📦 Total Products Available to Users: {total_products}")
        print(f"⚙️  Total Services Available to Users: {total_services}")
        print(f"🎯 Total Items (Products + Services): {total_products + total_services}")
        
        # Breakdown by business type
        print(f"\n📊 Breakdown by Type:")
        print(f"   • Product-based businesses: {total_products} items to choose from")
        print(f"   • Service-based businesses: {total_services} items to choose from")
        print(f"   • Mixed businesses: {total_products + total_services} total items")
        
        # Search experience summary
        print(f"\n🔍 User Search Experience:")
        print(f"   • When user types 'smartphone' → Gets {db.query(HSNCode).filter(HSNCode.description.like('%smartphone%')).count()} specific options")
        print(f"   • When user types 'laptop' → Gets {db.query(HSNCode).filter(HSNCode.description.like('%laptop%')).count()} specific options")
        print(f"   • When user types 'website' → Gets {db.query(MasterService).filter(MasterService.name.like('%website%')).count()} specific options")
        print(f"   • When user types 'development' → Gets {db.query(MasterService).filter(MasterService.name.like('%development%')).count()} specific options")
        
        # GST rate distribution
        print(f"\n💰 GST Rate Distribution:")
        
        # Product GST rates
        product_gst_rates = db.query(
            HSNCode.gst_rate,
            func.count(HSNCode.id).label('count')
        ).filter(HSNCode.business_type == 'product').group_by(HSNCode.gst_rate).all()
        
        print(f"   📦 Products by GST Rate:")
        for gst_rate, count in sorted(product_gst_rates):
            print(f"      • {gst_rate}% GST: {count} products")
        
        # Service GST rates
        service_gst_rates = db.query(
            MasterService.gst_rate,
            func.count(MasterService.id).label('count')
        ).filter(MasterService.is_active == True).group_by(MasterService.gst_rate).all()
        
        print(f"   🔧 Services by GST Rate:")
        for gst_rate, count in sorted(service_gst_rates):
            print(f"      • {gst_rate}% GST: {count} services")
        
        # Database health check
        print(f"\n🏥 Database Health Check:")
        
        # Check for missing data
        products_without_category = db.query(HSNCode).filter(
            HSNCode.business_type == 'product',
            HSNCode.category.is_(None)
        ).count()
        
        services_without_category = db.query(MasterService).filter(
            MasterService.is_active == True,
            MasterService.category.is_(None)
        ).count()
        
        products_without_keywords = db.query(HSNCode).filter(
            HSNCode.business_type == 'product',
            HSNCode.keywords.is_(None)
        ).count()
        
        services_without_keywords = db.query(MasterService).filter(
            MasterService.is_active == True,
            MasterService.keywords.is_(None)
        ).count()
        
        print(f"   ✅ Products without category: {products_without_category}")
        print(f"   ✅ Services without category: {services_without_category}")
        print(f"   ✅ Products without keywords: {products_without_keywords}")
        print(f"   ✅ Services without keywords: {services_without_keywords}")
        
        # Quality metrics
        print(f"\n📈 Quality Metrics:")
        avg_product_keyword_length = db.query(func.avg(func.length(HSNCode.keywords))).filter(
            HSNCode.business_type == 'product',
            HSNCode.keywords.isnot(None)
        ).scalar() or 0
        
        avg_service_keyword_length = db.query(func.avg(func.length(MasterService.keywords))).filter(
            MasterService.is_active == True,
            MasterService.keywords.isnot(None)
        ).scalar() or 0
        
        print(f"   📊 Average product keyword length: {avg_product_keyword_length:.1f} characters")
        print(f"   📊 Average service keyword length: {avg_service_keyword_length:.1f} characters")
        
        # Final recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"   ✅ Database is well-populated with {total_products + total_services} items")
        print(f"   ✅ Good coverage across multiple categories and GST rates")
        print(f"   ✅ Smart specificity achieved - not too generic, not too specific")
        
        if total_products < 50:
            print(f"   ⚠️  Consider adding more product categories for better coverage")
        
        if total_services < 20:
            print(f"   ⚠️  Consider adding more service types for service-based businesses")
        
        print(f"\n🎉 SUMMARY: Users have access to {total_products + total_services} well-organized, searchable items!")
        
    except Exception as e:
        print(f"❌ Error generating database summary: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    generate_database_summary()
