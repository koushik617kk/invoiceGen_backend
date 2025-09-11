#!/usr/bin/env python3
"""
Script to validate and fix SAC codes in existing data
"""

import json
from collections import defaultdict

def validate_and_fix_sac_codes():
    """Validate SAC codes against official list and suggest fixes"""
    
    # Official SAC codes from research
    official_sac_codes = {
        '998311': 'Management consulting and management services',
        '998312': 'Business consulting services, public relations',
        '998313': 'IT consulting and support services',
        '998314': 'IT design and development services',
        '998315': 'Hosting and IT infrastructure services',
        '998316': 'IT infrastructure and network management',
        '998319': 'Other IT services not elsewhere classified',
        '998211': 'Legal services',
        '998212': 'Accounting and bookkeeping services',
        '997212': 'Maintenance and repair services of motor vehicles',
        '997331': 'Beauty and wellness services',
        '996511': 'Transportation services',
        '995411': 'Food and beverage services',
        '997311': 'Cleaning services',
        '997211': 'Repair services',
        '998321': 'Professional services',
        '997321': 'Maintenance services',
        '996331': 'Logistics services',
        '998414': 'Other professional services'
    }
    
    # Read existing data
    with open('master_services_export_20250906_121840.json', 'r', encoding='utf-8') as f:
        services = json.load(f)
    
    print("🔍 VALIDATING SAC CODES")
    print("=" * 60)
    
    # Analyze current SAC codes
    sac_analysis = defaultdict(list)
    for service in services:
        sac_code = service['sac_code']
        sac_analysis[sac_code].append({
            'name': service['name'],
            'category': service['category'],
            'description': service['description']
        })
    
    print("📊 CURRENT SAC CODE USAGE:")
    for sac_code, services_list in sorted(sac_analysis.items()):
        status = "✅ OFFICIAL" if sac_code in official_sac_codes else "❌ UNOFFICIAL"
        print(f"• {sac_code}: {len(services_list)} services - {status}")
        if sac_code in official_sac_codes:
            print(f"  Description: {official_sac_codes[sac_code]}")
    
    print("\n" + "=" * 60)
    print("🔧 SUGGESTED FIXES")
    print("=" * 60)
    
    # Create mapping suggestions
    suggestions = {
        # IT Services
        '998399': '998314',  # Generic IT services -> IT design and development
        '998321': '998311',  # Generic professional -> Management consulting
        
        # Professional Services
        '998414': '998311',  # Other professional -> Management consulting
        
        # Automotive Services
        '997211': '997212',  # Generic repair -> Motor vehicle repair
        
        # Beauty Services
        '997331': '997331',  # Already correct
        
        # Transportation
        '996511': '996511',  # Already correct
        
        # Food Services
        '995411': '995411',  # Already correct
        
        # Cleaning Services
        '997311': '997311',  # Already correct
        
        # Maintenance Services
        '997321': '997212',  # Generic maintenance -> Motor vehicle repair
        
        # Logistics
        '996331': '996511',  # Logistics -> Transportation
    }
    
    print("MAPPING SUGGESTIONS:")
    for old_code, new_code in suggestions.items():
        if old_code in sac_analysis:
            old_desc = official_sac_codes.get(new_code, "Unknown")
            print(f"• {old_code} → {new_code} ({old_desc})")
            print(f"  Affects {len(sac_analysis[old_code])} services")
    
    print("\n" + "=" * 60)
    print("📋 VALIDATION REPORT")
    print("=" * 60)
    
    # Count official vs unofficial
    official_count = sum(len(services_list) for sac_code, services_list in sac_analysis.items() 
                        if sac_code in official_sac_codes)
    unofficial_count = sum(len(services_list) for sac_code, services_list in sac_analysis.items() 
                          if sac_code not in official_sac_codes)
    
    print(f"✅ Official SAC codes: {official_count} services")
    print(f"❌ Unofficial SAC codes: {unofficial_count} services")
    print(f"📊 Total services: {official_count + unofficial_count}")
    
    # Calculate improvement percentage
    improvement = (official_count / (official_count + unofficial_count)) * 100
    print(f"📈 Current accuracy: {improvement:.1f}%")
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDED ACTIONS")
    print("=" * 60)
    
    print("1. ✅ Keep services with official SAC codes as-is")
    print("2. 🔧 Update unofficial SAC codes using mapping suggestions")
    print("3. 📝 Add official descriptions for better clarity")
    print("4. 🧪 Test search functionality after updates")
    print("5. 📊 Monitor user feedback on suggestions")
    
    return {
        'official_count': official_count,
        'unofficial_count': unofficial_count,
        'suggestions': suggestions,
        'sac_analysis': dict(sac_analysis)
    }

if __name__ == "__main__":
    print("🚀 Validating SAC codes in existing data...")
    analysis = validate_and_fix_sac_codes()
    print("\n🎉 Validation complete!")
