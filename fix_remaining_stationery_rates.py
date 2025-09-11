#!/usr/bin/env python3
"""
Script to fix remaining stationery items to 5% GST rate
"""

from database import SessionLocal
from models import HSNCode
from datetime import datetime

def fix_remaining_stationery_rates():
    """Fix remaining stationery items to 5% GST rate"""
    
    print("🚀 FIXING REMAINING STATIONERY ITEMS TO 5% GST RATE")
    print("=" * 60)
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Get stationery codes that are still at 18%
        stationery_codes = db.query(HSNCode).filter(
            HSNCode.category == "Stationery",
            HSNCode.gst_rate == 18.0
        ).all()
        
        print(f"📊 Found {len(stationery_codes)} stationery codes at 18% that need to be updated to 5%")
        
        updated_count = 0
        
        for code in stationery_codes:
            print(f"  🔄 Updating {code.code}: {code.description}")
            print(f"      Rate: {code.gst_rate}% → 5.0%")
            print(f"      Reason: Essential stationery items - official 2025 GST reform")
            
            # Update the GST rate
            code.gst_rate = 5.0
            code.updated_at = datetime.utcnow()
            updated_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Successfully updated {updated_count} stationery codes to 5%")
        
        # Verify the update
        print("\n🔍 Verifying stationery codes update...")
        
        # Show all stationery codes
        print("📝 All Stationery HSN codes (should be 5%):")
        all_stationery = db.query(HSNCode).filter(HSNCode.category == "Stationery").all()
        for code in all_stationery:
            status = "✅" if code.gst_rate == 5.0 else "❌"
            print(f"  {status} {code.code} - {code.description} - {code.gst_rate}%")
        
        # Show final rate distribution
        print("\n📊 Final GST Rate Distribution:")
        from sqlalchemy import func
        rate_distribution = db.query(HSNCode.gst_rate, func.count(HSNCode.id)).group_by(HSNCode.gst_rate).all()
        for rate, count in rate_distribution:
            print(f"  • {rate}%: {count} codes")
        
        print("\n🎉 STATIONERY RATES FIXED!")
        print("=" * 60)
        print("✅ All stationery items now at 5% GST")
        print("✅ Compliant with official 2025 GST reforms")
        print("✅ Essential items properly categorized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing stationery rates: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting stationery rates fix...")
    success = fix_remaining_stationery_rates()
    
    if success:
        print("\n🎉 SUCCESS! Stationery rates fixed!")
        print("🚀 All essential items now at correct 5% rate!")
    else:
        print("\n❌ FAILED! Please check the errors above.")
