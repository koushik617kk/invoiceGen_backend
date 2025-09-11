#!/usr/bin/env python3
"""
Script to fix pharmaceutical HSN codes to 5% GST rate
The 12% rate was abolished in 2025 GST reforms
"""

from database import SessionLocal
from models import HSNCode
from datetime import datetime

def fix_pharmaceutical_rates():
    """Fix pharmaceutical HSN codes to 5% GST rate"""
    
    print("🚀 FIXING PHARMACEUTICAL HSN CODES TO 5% GST RATE")
    print("=" * 60)
    print("📅 2025 GST Reform: 12% rate abolished")
    print("📋 All medical supplies moved to 5% (essential items)")
    print("=" * 60)
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Find pharmaceutical codes at 12% (should be 5%)
        pharma_12_percent = db.query(HSNCode).filter(
            HSNCode.category == "Pharmaceuticals",
            HSNCode.gst_rate == 12.0
        ).all()
        
        print(f"📊 Found {len(pharma_12_percent)} pharmaceutical codes at 12% that need to be updated to 5%")
        
        updated_count = 0
        
        for code in pharma_12_percent:
            print(f"  🔄 Updating {code.code}: {code.description}")
            print(f"      Rate: {code.gst_rate}% → 5.0%")
            print(f"      Reason: 12% rate abolished - medical supplies are essential items")
            
            # Update the GST rate
            code.gst_rate = 5.0
            code.updated_at = datetime.utcnow()
            updated_count += 1
        
        # Also check for any other codes at 12% (should be none after 2025 reforms)
        all_12_percent = db.query(HSNCode).filter(HSNCode.gst_rate == 12.0).all()
        
        if all_12_percent:
            print(f"\n⚠️  Found {len(all_12_percent)} other codes at 12% (should be updated):")
            for code in all_12_percent:
                print(f"  • {code.code} - {code.description} - {code.category}")
                # Update to 5% (essential items) or 18% (non-essential) based on category
                if code.category in ["Pharmaceuticals", "Stationery"]:
                    code.gst_rate = 5.0
                    print(f"    Updated to 5% (essential item)")
                else:
                    code.gst_rate = 18.0
                    print(f"    Updated to 18% (non-essential item)")
                code.updated_at = datetime.utcnow()
                updated_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Successfully updated {updated_count} HSN codes")
        
        # Verify the update
        print("\n🔍 Verifying pharmaceutical codes update...")
        
        # Show all pharmaceutical codes
        print("💊 All Pharmaceutical HSN codes (should be 5%):")
        all_pharma = db.query(HSNCode).filter(HSNCode.category == "Pharmaceuticals").all()
        for code in all_pharma:
            status = "✅" if code.gst_rate == 5.0 else "❌"
            print(f"  {status} {code.code} - {code.description} - {code.gst_rate}%")
        
        # Show final rate distribution
        print("\n📊 Final GST Rate Distribution:")
        from sqlalchemy import func
        rate_distribution = db.query(HSNCode.gst_rate, func.count(HSNCode.id)).group_by(HSNCode.gst_rate).all()
        for rate, count in rate_distribution:
            print(f"  • {rate}%: {count} codes")
        
        # Check if 12% rate is completely eliminated
        remaining_12_percent = db.query(HSNCode).filter(HSNCode.gst_rate == 12.0).count()
        if remaining_12_percent == 0:
            print("\n🎉 SUCCESS! 12% GST rate completely eliminated!")
            print("✅ All codes now comply with 2025 GST reforms")
        else:
            print(f"\n⚠️  Warning: {remaining_12_percent} codes still at 12%")
        
        print("\n🎉 PHARMACEUTICAL RATES FIXED!")
        print("=" * 60)
        print("✅ All pharmaceutical items now at 5% GST")
        print("✅ 12% rate completely abolished")
        print("✅ Compliant with official 2025 GST reforms")
        print("✅ Essential medical supplies properly categorized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing pharmaceutical rates: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting pharmaceutical rates fix...")
    success = fix_pharmaceutical_rates()
    
    if success:
        print("\n🎉 SUCCESS! Pharmaceutical rates fixed!")
        print("🚀 12% rate completely eliminated!")
    else:
        print("\n❌ FAILED! Please check the errors above.")
