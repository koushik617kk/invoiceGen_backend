#!/usr/bin/env python3
"""
Script to analyze HSN codes for search gaps and user experience issues
"""

from database import SessionLocal
from models import HSNCode
from sqlalchemy import func

def analyze_hsn_search_gaps():
    """Analyze HSN codes for search gaps and user experience issues"""
    
    print("🔍 ANALYZING HSN CODES FOR SEARCH GAPS")
    print("=" * 60)
    
    # Connect to database
    db = SessionLocal()
    
    try:
        # Get all HSN codes
        all_codes = db.query(HSNCode).all()
        
        print(f"📊 Total HSN codes: {len(all_codes)}")
        
        # Analyze search patterns
        print("\n🔍 SEARCH PATTERN ANALYSIS:")
        
        # Check for common user search terms that might be missing
        common_searches = [
            "car", "vehicle", "auto", "automotive",
            "phone", "mobile", "smartphone",
            "laptop", "computer", "pc",
            "pen", "paper", "notebook",
            "tire", "tyre", "wheel",
            "battery", "oil", "brake",
            "monitor", "screen", "display",
            "speaker", "headphone", "audio"
        ]
        
        print("\n📝 Checking for common search terms:")
        missing_terms = []
        
        for search_term in common_searches:
            found = False
            for code in all_codes:
                if (search_term.lower() in code.keywords.lower() or 
                    search_term.lower() in code.description.lower()):
                    found = True
                    break
            
            if not found:
                missing_terms.append(search_term)
                print(f"  ❌ Missing: '{search_term}'")
            else:
                print(f"  ✅ Found: '{search_term}'")
        
        # Analyze keyword quality
        print("\n🔍 KEYWORD QUALITY ANALYSIS:")
        
        for code in all_codes:
            keywords = code.keywords.lower()
            description = code.description.lower()
            
            # Check for generic keywords
            generic_keywords = ["parts", "accessories", "equipment", "devices"]
            has_generic = any(gen in keywords for gen in generic_keywords)
            
            # Check for specific keywords
            specific_keywords = ["car", "phone", "computer", "pen", "tire", "battery"]
            has_specific = any(spec in keywords for spec in specific_keywords)
            
            if has_generic and not has_specific:
                print(f"  ⚠️  Generic keywords only: {code.code} - {code.description}")
                print(f"      Keywords: {code.keywords}")
        
        # Check for missing product variations
        print("\n🔍 MISSING PRODUCT VARIATIONS:")
        
        # Automotive variations
        auto_codes = [c for c in all_codes if c.category == "Automotive"]
        print(f"\n🚗 Automotive codes ({len(auto_codes)}):")
        for code in auto_codes:
            print(f"  • {code.code} - {code.description}")
            print(f"    Keywords: {code.keywords}")
        
        # Check if we have common automotive products
        auto_products = ["car", "tire", "battery", "oil", "brake", "engine", "transmission", "suspension"]
        missing_auto = []
        for product in auto_products:
            found = any(product in code.keywords.lower() or product in code.description.lower() 
                       for code in auto_codes)
            if not found:
                missing_auto.append(product)
        
        if missing_auto:
            print(f"\n❌ Missing automotive products: {', '.join(missing_auto)}")
        else:
            print("\n✅ All common automotive products covered")
        
        # Electronics variations
        elec_codes = [c for c in all_codes if c.category == "Electronics"]
        print(f"\n💻 Electronics codes ({len(elec_codes)}):")
        for code in elec_codes:
            print(f"  • {code.code} - {code.description}")
            print(f"    Keywords: {code.keywords}")
        
        # Check if we have common electronics products
        elec_products = ["phone", "laptop", "computer", "monitor", "speaker", "headphone", "camera", "tablet"]
        missing_elec = []
        for product in elec_products:
            found = any(product in code.keywords.lower() or product in code.description.lower() 
                       for code in elec_codes)
            if not found:
                missing_elec.append(product)
        
        if missing_elec:
            print(f"\n❌ Missing electronics products: {', '.join(missing_elec)}")
        else:
            print("\n✅ All common electronics products covered")
        
        # Stationery variations
        stat_codes = [c for c in all_codes if c.category == "Stationery"]
        print(f"\n📝 Stationery codes ({len(stat_codes)}):")
        for code in stat_codes:
            print(f"  • {code.code} - {code.description}")
            print(f"    Keywords: {code.keywords}")
        
        # Check if we have common stationery products
        stat_products = ["pen", "paper", "notebook", "pencil", "eraser", "ruler", "calculator", "stapler"]
        missing_stat = []
        for product in stat_products:
            found = any(product in code.keywords.lower() or product in code.description.lower() 
                       for code in stat_codes)
            if not found:
                missing_stat.append(product)
        
        if missing_stat:
            print(f"\n❌ Missing stationery products: {', '.join(missing_stat)}")
        else:
            print("\n✅ All common stationery products covered")
        
        # Analyze business type coverage
        print("\n🔍 BUSINESS TYPE COVERAGE:")
        
        business_types = {
            "IT Services": ["computer", "laptop", "software", "monitor", "keyboard", "mouse"],
            "Digital Marketing": ["computer", "monitor", "camera", "phone", "tablet"],
            "Professional Services": ["pen", "paper", "notebook", "calculator", "printer"],
            "Automotive Services": ["car", "tire", "battery", "oil", "brake", "engine"],
            "Auto Parts Dealers": ["car", "tire", "battery", "oil", "brake", "engine", "transmission"]
        }
        
        for business_type, required_products in business_types.items():
            coverage = 0
            for product in required_products:
                found = any(product in code.keywords.lower() or product in code.description.lower() 
                           for code in all_codes)
                if found:
                    coverage += 1
            
            percentage = (coverage / len(required_products)) * 100
            print(f"  • {business_type}: {coverage}/{len(required_products)} products ({percentage:.1f}%)")
        
        print("\n🎯 RECOMMENDATIONS:")
        print("1. ✅ Add more specific product variations")
        print("2. 🔍 Include common user search terms")
        print("3. 📝 Add product synonyms and alternative names")
        print("4. 🚗 Expand automotive product range")
        print("5. 💻 Add more electronics variations")
        print("6. 📝 Expand stationery product range")
        
        return {
            'total_codes': len(all_codes),
            'missing_terms': missing_terms,
            'missing_auto': missing_auto,
            'missing_elec': missing_elec,
            'missing_stat': missing_stat,
            'business_coverage': business_types
        }
        
    except Exception as e:
        print(f"❌ Error analyzing HSN codes: {e}")
        return None
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Analyzing HSN codes for search gaps...")
    analysis = analyze_hsn_search_gaps()
    
    if analysis:
        print("\n🎉 Analysis complete!")
        print(f"📊 Found {analysis['total_codes']} HSN codes")
        print(f"❌ Missing {len(analysis['missing_terms'])} common search terms")
    else:
        print("\n❌ Analysis failed!")
