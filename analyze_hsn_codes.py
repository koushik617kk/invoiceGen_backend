#!/usr/bin/env python3
"""
Script to analyze existing HSN codes in the database
"""

from database import SessionLocal
from models import HSNCode
from sqlalchemy import func

def analyze_hsn_codes():
    """Analyze existing HSN codes in the database"""
    
    print("🔍 ANALYZING HSN CODES IN DATABASE")
    print("=" * 60)
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Get total count
        total_count = db.query(HSNCode).count()
        print(f"📊 Total HSN codes in database: {total_count}")
        
        if total_count == 0:
            print("❌ No HSN codes found in database!")
            return
        
        # Show type distribution
        print("\n📋 Type distribution:")
        types = db.query(HSNCode.type, func.count(HSNCode.id)).group_by(HSNCode.type).all()
        for type_name, count in types:
            print(f"  • {type_name}: {count} codes")
        
        # Show category breakdown
        print("\n📋 Category breakdown:")
        categories = db.query(HSNCode.category, func.count(HSNCode.id)).group_by(HSNCode.category).all()
        for category, count in categories:
            print(f"  • {category}: {count} codes")
        
        # Show GST rate distribution
        print("\n💰 GST rate distribution:")
        gst_rates = db.query(HSNCode.gst_rate, func.count(HSNCode.id)).group_by(HSNCode.gst_rate).all()
        for gst_rate, count in gst_rates:
            print(f"  • {gst_rate}%: {count} codes")
        
        # Show sample HSN codes
        print("\n📋 Sample HSN codes:")
        sample_codes = db.query(HSNCode).limit(10).all()
        for code in sample_codes:
            print(f"  • {code.code} - {code.description} - {code.gst_rate}% - {code.type}")
        
        # Check for common issues
        print("\n🔍 QUALITY CHECK:")
        
        # Check for missing descriptions
        missing_desc = db.query(HSNCode).filter(HSNCode.description.is_(None) | (HSNCode.description == '')).count()
        if missing_desc > 0:
            print(f"❌ Missing descriptions: {missing_desc} codes")
        else:
            print("✅ All codes have descriptions")
        
        # Check for missing keywords
        missing_keywords = db.query(HSNCode).filter(HSNCode.keywords.is_(None) | (HSNCode.keywords == '')).count()
        if missing_keywords > 0:
            print(f"❌ Missing keywords: {missing_keywords} codes")
        else:
            print("✅ All codes have keywords")
        
        # Check for invalid GST rates
        valid_rates = [0, 5, 12, 18, 28]
        invalid_gst = db.query(HSNCode).filter(~HSNCode.gst_rate.in_(valid_rates)).count()
        if invalid_gst > 0:
            print(f"❌ Invalid GST rates: {invalid_gst} codes")
        else:
            print("✅ All codes have valid GST rates")
        
        # Check for missing categories
        missing_category = db.query(HSNCode).filter(HSNCode.category.is_(None) | (HSNCode.category == '')).count()
        if missing_category > 0:
            print(f"❌ Missing categories: {missing_category} codes")
        else:
            print("✅ All codes have categories")
        
        print("\n🎯 RECOMMENDATIONS:")
        print("1. ✅ Analyze current HSN codes for accuracy")
        print("2. 🔍 Research official HSN codes for your target products")
        print("3. 📝 Add more automotive products (your main focus)")
        print("4. 🧹 Clean up any incomplete or inaccurate data")
        print("5. 🚀 Enhance search functionality for products")
        
        return {
            'total_count': total_count,
            'types': dict(types),
            'categories': dict(categories),
            'gst_rates': dict(gst_rates),
            'issues': {
                'missing_desc': missing_desc,
                'missing_keywords': missing_keywords,
                'invalid_gst': invalid_gst,
                'missing_category': missing_category
            }
        }
        
    except Exception as e:
        print(f"❌ Error analyzing HSN codes: {e}")
        return None
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Analyzing HSN codes in database...")
    analysis = analyze_hsn_codes()
    
    if analysis:
        print("\n🎉 Analysis complete!")
        print(f"📊 Found {analysis['total_count']} HSN codes")
    else:
        print("\n❌ Analysis failed!")
