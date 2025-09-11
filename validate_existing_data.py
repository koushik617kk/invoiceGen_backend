#!/usr/bin/env python3
"""
Script to validate and analyze existing master services data
"""

import json
from collections import defaultdict, Counter

def analyze_existing_data():
    """Analyze the existing master services data for validation"""
    
    # Read the existing JSON file
    with open('master_services_export_20250906_121840.json', 'r', encoding='utf-8') as f:
        services = json.load(f)
    
    print("🔍 ANALYZING EXISTING MASTER SERVICES DATA")
    print("=" * 60)
    
    # Basic statistics
    total_services = len(services)
    print(f"📊 Total Services: {total_services}")
    
    # Category analysis
    categories = Counter([s['category'] for s in services])
    print(f"📊 Total Categories: {len(categories)}")
    
    # SAC code analysis
    sac_codes = Counter([s['sac_code'] for s in services])
    print(f"📊 Unique SAC Codes: {len(sac_codes)}")
    
    # GST rate analysis
    gst_rates = Counter([s['gst_rate'] for s in services])
    print(f"📊 GST Rates Used: {dict(gst_rates)}")
    
    print("\n" + "=" * 60)
    print("📋 CATEGORY BREAKDOWN")
    print("=" * 60)
    
    for category, count in categories.most_common():
        print(f"• {category}: {count} services")
    
    print("\n" + "=" * 60)
    print("🔢 SAC CODE ANALYSIS")
    print("=" * 60)
    
    for sac_code, count in sac_codes.most_common():
        print(f"• {sac_code}: {count} services")
    
    print("\n" + "=" * 60)
    print("💰 GST RATE ANALYSIS")
    print("=" * 60)
    
    for rate, count in gst_rates.most_common():
        print(f"• {rate}%: {count} services")
    
    print("\n" + "=" * 60)
    print("🔍 VALIDATION CHECKLIST")
    print("=" * 60)
    
    # Check for common issues
    issues = []
    
    # 1. Check for missing or invalid SAC codes
    invalid_sac = [s for s in services if not s['sac_code'] or len(s['sac_code']) != 6]
    if invalid_sac:
        issues.append(f"❌ Invalid SAC codes: {len(invalid_sac)} services")
    
    # 2. Check for invalid GST rates
    valid_rates = [0, 5, 12, 18, 28]
    invalid_gst = [s for s in services if s['gst_rate'] not in valid_rates]
    if invalid_gst:
        issues.append(f"❌ Invalid GST rates: {len(invalid_gst)} services")
    
    # 3. Check for missing keywords
    missing_keywords = [s for s in services if not s['keywords'] or s['keywords'].strip() == '']
    if missing_keywords:
        issues.append(f"❌ Missing keywords: {len(missing_keywords)} services")
    
    # 4. Check for missing descriptions
    missing_desc = [s for s in services if not s['description'] or s['description'].strip() == '']
    if missing_desc:
        issues.append(f"❌ Missing descriptions: {len(missing_desc)} services")
    
    # 5. Check for duplicate names
    names = [s['name'] for s in services]
    duplicates = [name for name, count in Counter(names).items() if count > 1]
    if duplicates:
        issues.append(f"❌ Duplicate names: {len(duplicates)} duplicates found")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No major issues found!")
    
    print("\n" + "=" * 60)
    print("📈 RECOMMENDATIONS")
    print("=" * 60)
    
    # Recommendations based on analysis
    recommendations = []
    
    # Check if SAC codes match official ones
    official_sac_codes = ['998311', '998312', '998313', '998314', '998315', '998316', '998319']
    unofficial_sac = [s for s in services if s['sac_code'] not in official_sac_codes]
    if unofficial_sac:
        recommendations.append(f"⚠️  {len(unofficial_sac)} services use unofficial SAC codes")
    
    # Check for consistent GST rates
    if len(gst_rates) > 3:
        recommendations.append("⚠️  Consider standardizing GST rates (too many variations)")
    
    # Check for keyword quality
    short_keywords = [s for s in services if s['keywords'] and len(s['keywords'].split(',')) < 3]
    if short_keywords:
        recommendations.append(f"⚠️  {len(short_keywords)} services have limited keywords")
    
    if recommendations:
        for rec in recommendations:
            print(f"  {rec}")
    else:
        print("✅ Data quality looks good!")
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("=" * 60)
    
    print("1. ✅ Your data structure is good!")
    print("2. 🔍 Focus on validating SAC codes against official list")
    print("3. 📝 Improve keywords for better search")
    print("4. 🧹 Clean up any duplicate or incomplete entries")
    print("5. 🚀 Ready to enhance search functionality")
    
    return {
        'total_services': total_services,
        'categories': dict(categories),
        'sac_codes': dict(sac_codes),
        'gst_rates': dict(gst_rates),
        'issues': issues,
        'recommendations': recommendations
    }

if __name__ == "__main__":
    print("🚀 Analyzing existing master services data...")
    analysis = analyze_existing_data()
    print("\n🎉 Analysis complete!")
