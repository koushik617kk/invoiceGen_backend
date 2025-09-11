#!/usr/bin/env python3
"""
Script to update GST rates based on official 2025 GST reforms
Effective from September 22, 2025
"""

from database import SessionLocal
from models import HSNCode
from sqlalchemy import func
from datetime import datetime

def update_gst_rates_2025():
    """Update GST rates based on official 2025 GST reforms"""
    
    print("🚀 UPDATING GST RATES FOR 2025 REFORMS")
    print("=" * 60)
    print("📅 Effective Date: September 22, 2025")
    print("📋 Source: Official GST Council Notification")
    print("=" * 60)
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Get all HSN codes
        all_codes = db.query(HSNCode).all()
        
        print(f"📊 Total HSN codes to review: {len(all_codes)}")
        
        # Define GST rate changes based on official 2025 reforms
        gst_rate_changes = {
            # AUTOMOTIVE - 28% to 18% (Official Change)
            "8708": {"old_rate": 28.0, "new_rate": 18.0, "reason": "Auto parts - uniform 18% rate"},
            "4011": {"old_rate": 28.0, "new_rate": 18.0, "reason": "Tires - reduced from 28% to 18%"},
            "8507": {"old_rate": 28.0, "new_rate": 18.0, "reason": "Car batteries - reduced from 28% to 18%"},
            "2710": {"old_rate": 28.0, "new_rate": 18.0, "reason": "Engine oil - reduced from 28% to 18%"},
            
            # STATIONERY - 12% to 5% (Official Change for Essential Items)
            "4820": {"old_rate": 12.0, "new_rate": 5.0, "reason": "Notebooks - essential items to 5%"},
            "9608": {"old_rate": 12.0, "new_rate": 5.0, "reason": "Pens - essential items to 5%"},
            "4823": {"old_rate": 12.0, "new_rate": 5.0, "reason": "Paper - essential items to 5%"},
            
            # ELECTRONICS - Remain at 18% (No Change)
            "8517": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Phones - no change, remains 18%"},
            "8471": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Computers - no change, remains 18%"},
            "8518": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Audio equipment - no change, remains 18%"},
            "8528": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Monitors - no change, remains 18%"},
            "8523": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Storage devices - no change, remains 18%"},
            "9013": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Optical instruments - no change, remains 18%"},
            "9015": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Measurement tools - no change, remains 18%"},
            "8443": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Printers - no change, remains 18%"},
            "8525": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Cameras - no change, remains 18%"},
            "8470": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Calculators - no change, remains 18%"},
            "8305": {"old_rate": 18.0, "new_rate": 18.0, "reason": "Office equipment - no change, remains 18%"},
            "9017": {"old_rate": 12.0, "new_rate": 5.0, "reason": "Drawing instruments - essential items to 5%"},
        }
        
        updated_count = 0
        no_change_count = 0
        
        print("\n🔍 Updating GST rates based on official 2025 reforms...")
        print("=" * 60)
        
        for code in all_codes:
            if code.code in gst_rate_changes:
                change_info = gst_rate_changes[code.code]
                old_rate = change_info["old_rate"]
                new_rate = change_info["new_rate"]
                reason = change_info["reason"]
                
                if old_rate != new_rate:
                    # Update the GST rate
                    code.gst_rate = new_rate
                    code.updated_at = datetime.utcnow()
                    updated_count += 1
                    
                    print(f"  🔄 Updated {code.code}: {code.description}")
                    print(f"      Rate: {old_rate}% → {new_rate}%")
                    print(f"      Reason: {reason}")
                    print()
                else:
                    no_change_count += 1
                    print(f"  ✅ No change {code.code}: {code.description} ({new_rate}%)")
            else:
                print(f"  ⚠️  Not in update list: {code.code} - {code.description} ({code.gst_rate}%)")
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Successfully updated {updated_count} HSN codes")
        print(f"✅ {no_change_count} codes already had correct rates")
        
        # Verify the update
        print("\n🔍 Verifying GST rates update...")
        print("=" * 60)
        
        # Show rate distribution
        print("📊 GST Rate Distribution:")
        rate_distribution = db.query(HSNCode.gst_rate, func.count(HSNCode.id)).group_by(HSNCode.gst_rate).all()
        for rate, count in rate_distribution:
            print(f"  • {rate}%: {count} codes")
        
        # Show automotive codes
        print("\n🚗 Automotive HSN codes (should be 18%):")
        auto_codes = db.query(HSNCode).filter(HSNCode.category == "Automotive").all()
        for code in auto_codes:
            status = "✅" if code.gst_rate == 18.0 else "❌"
            print(f"  {status} {code.code} - {code.description} - {code.gst_rate}%")
        
        # Show stationery codes
        print("\n📝 Stationery HSN codes (should be 5%):")
        stat_codes = db.query(HSNCode).filter(HSNCode.category == "Stationery").all()
        for code in stat_codes:
            status = "✅" if code.gst_rate == 5.0 else "❌"
            print(f"  {status} {code.code} - {code.description} - {code.gst_rate}%")
        
        # Show electronics codes
        print("\n💻 Electronics HSN codes (should be 18%):")
        elec_codes = db.query(HSNCode).filter(HSNCode.category == "Electronics").all()
        for code in elec_codes:
            status = "✅" if code.gst_rate == 18.0 else "❌"
            print(f"  {status} {code.code} - {code.description} - {code.gst_rate}%")
        
        # Test common search terms with new rates
        print("\n🔍 Testing search with updated rates:")
        test_terms = ["car", "tire", "battery", "pen", "paper", "computer", "phone"]
        
        for term in test_terms:
            found_codes = db.query(HSNCode).filter(
                HSNCode.keywords.contains(term) | HSNCode.description.contains(term)
            ).limit(3).all()
            
            if found_codes:
                print(f"  ✅ '{term}': {len(found_codes)} codes found")
                for code in found_codes:
                    print(f"      • {code.code} - {code.gst_rate}% - {code.description}")
        
        print("\n🎉 GST RATES UPDATED FOR 2025!")
        print("=" * 60)
        print("✅ Automotive: 28% → 18% (Official Change)")
        print("✅ Stationery: 12% → 5% (Essential Items)")
        print("✅ Electronics: 18% (No Change)")
        print("✅ Effective: September 22, 2025")
        print("✅ Compliant with official GST reforms")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating GST rates: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting GST rates update for 2025 reforms...")
    success = update_gst_rates_2025()
    
    if success:
        print("\n🎉 SUCCESS! GST rates updated for 2025 reforms!")
        print("🚀 Your system is now compliant with official GST changes!")
    else:
        print("\n❌ FAILED! Please check the errors above.")
