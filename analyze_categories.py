#!/usr/bin/env python3
"""
Script to analyze master services JSON and organize by categories
"""

import json
from collections import defaultdict

def analyze_master_services_by_category():
    """Analyze master services and organize by category"""
    
    # Read the JSON file
    with open('master_services_export_20250906_121840.json', 'r', encoding='utf-8') as f:
        services = json.load(f)
    
    # Organize by category
    categories = defaultdict(list)
    
    for service in services:
        category = service['category']
        categories[category].append({
            'name': service['name'],
            'description': service['description'],
            'sac_code': service['sac_code'],
            'subcategory': service['subcategory'],
            'keywords': service['keywords'],
            'gst_rate': service['gst_rate'],
            'unit': service['unit'],
            'usage_count': service['usage_count']
        })
    
    # Sort categories alphabetically
    sorted_categories = dict(sorted(categories.items()))
    
    # Create analysis report
    report = []
    report.append("=" * 80)
    report.append("MASTER SERVICES - CATEGORY WISE ANALYSIS")
    report.append("=" * 80)
    report.append("")
    
    total_services = len(services)
    report.append(f"📊 TOTAL SERVICES: {total_services}")
    report.append(f"📊 TOTAL CATEGORIES: {len(sorted_categories)}")
    report.append("")
    
    # Analyze each category
    for category, services_list in sorted_categories.items():
        report.append("=" * 60)
        report.append(f"🏷️  CATEGORY: {category.replace('_', ' ').title()}")
        report.append("=" * 60)
        report.append(f"📈 Services in this category: {len(services_list)}")
        
        # Get unique subcategories
        subcategories = list(set([s['subcategory'] for s in services_list if s['subcategory']]))
        if subcategories:
            report.append(f"📂 Subcategories: {', '.join(subcategories)}")
        
        # Get unique SAC codes
        sac_codes = list(set([s['sac_code'] for s in services_list if s['sac_code']]))
        if sac_codes:
            report.append(f"🔢 SAC Codes: {', '.join(sac_codes)}")
        
        # Get unique GST rates
        gst_rates = list(set([s['gst_rate'] for s in services_list]))
        if gst_rates:
            report.append(f"💰 GST Rates: {', '.join([f'{rate}%' for rate in sorted(gst_rates)])}")
        
        report.append("")
        report.append("📋 SERVICES:")
        report.append("-" * 40)
        
        # Sort services by usage count (descending) then by name
        services_list.sort(key=lambda x: (-x['usage_count'], x['name']))
        
        for i, service in enumerate(services_list, 1):
            report.append(f"{i:2d}. {service['name']}")
            report.append(f"    📝 Description: {service['description']}")
            report.append(f"    🔢 SAC Code: {service['sac_code']}")
            report.append(f"    📂 Subcategory: {service['subcategory']}")
            report.append(f"    🏷️  Keywords: {service['keywords']}")
            report.append(f"    💰 GST Rate: {service['gst_rate']}%")
            report.append(f"    📏 Unit: {service['unit']}")
            report.append(f"    📊 Usage Count: {service['usage_count']}")
            report.append("")
        
        report.append("")
    
    # Summary statistics
    report.append("=" * 80)
    report.append("📊 SUMMARY STATISTICS")
    report.append("=" * 80)
    
    # Category sizes
    category_sizes = [(cat, len(services)) for cat, services in sorted_categories.items()]
    category_sizes.sort(key=lambda x: x[1], reverse=True)
    
    report.append("Categories by size (largest first):")
    for cat, size in category_sizes:
        report.append(f"  • {cat.replace('_', ' ').title()}: {size} services")
    
    report.append("")
    
    # Most used services
    all_services = []
    for services_list in categories.values():
        all_services.extend(services_list)
    
    most_used = sorted(all_services, key=lambda x: x['usage_count'], reverse=True)[:10]
    report.append("🔥 TOP 10 MOST USED SERVICES:")
    for i, service in enumerate(most_used, 1):
        report.append(f"  {i:2d}. {service['name']} (used {service['usage_count']} times)")
    
    report.append("")
    
    # SAC code distribution
    sac_code_dist = defaultdict(int)
    for service in all_services:
        sac_code_dist[service['sac_code']] += 1
    
    report.append("🔢 SAC CODE DISTRIBUTION:")
    for sac_code, count in sorted(sac_code_dist.items(), key=lambda x: x[1], reverse=True):
        report.append(f"  • {sac_code}: {count} services")
    
    report.append("")
    
    # GST rate distribution
    gst_rate_dist = defaultdict(int)
    for service in all_services:
        gst_rate_dist[service['gst_rate']] += 1
    
    report.append("💰 GST RATE DISTRIBUTION:")
    for gst_rate, count in sorted(gst_rate_dist.items(), key=lambda x: x[1], reverse=True):
        report.append(f"  • {gst_rate}%: {count} services")
    
    return "\n".join(report)

if __name__ == "__main__":
    print("🚀 Analyzing master services by category...")
    report = analyze_master_services_by_category()
    
    # Save to file
    with open('master_services_category_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Analysis complete! Report saved to: master_services_category_analysis.txt")
    print("\n" + "="*50)
    print("QUICK PREVIEW:")
    print("="*50)
    
    # Show first 50 lines as preview
    lines = report.split('\n')
    for line in lines[:50]:
        print(line)
    
    if len(lines) > 50:
        print(f"\n... and {len(lines) - 50} more lines in the full report")
