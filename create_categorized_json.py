#!/usr/bin/env python3
"""
Script to create categorized JSON from master services data
"""

import json
from collections import defaultdict

def create_categorized_json():
    """Create categorized JSON format with counts"""
    
    # Read the original JSON file
    with open('master_services_export_20250906_121840.json', 'r', encoding='utf-8') as f:
        services = json.load(f)
    
    # Organize by category
    categories = defaultdict(list)
    
    for service in services:
        category = service['category']
        service_data = {
            "name": service['name'],
            "description": service['description'],
            "sac_code": service['sac_code'],
            "subcategory": service['subcategory'],
            "keywords": service['keywords'],
            "gst_rate": service['gst_rate'],
            "unit": service['unit'],
            "usage_count": service['usage_count']
        }
        categories[category].append(service_data)
    
    # Create the categorized structure
    categorized_data = {
        "categories": {},
        "summary": {
            "total_services": len(services),
            "total_categories": len(categories)
        }
    }
    
    # Sort categories alphabetically and add count
    for category in sorted(categories.keys()):
        services_list = categories[category]
        categorized_data["categories"][category] = {
            "count": len(services_list),
            "services": services_list
        }
    
    # Create output filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"master_services_categorized_{timestamp}.json"
    
    # Write to JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(categorized_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully created categorized JSON: {filename}")
    print(f"📊 Total services: {categorized_data['summary']['total_services']}")
    print(f"📊 Total categories: {categorized_data['summary']['total_categories']}")
    
    # Show category counts
    print("\n📋 Category breakdown:")
    for category, data in categorized_data["categories"].items():
        print(f"  • {category}: {data['count']} services")
    
    return filename

if __name__ == "__main__":
    print("🚀 Creating categorized JSON from master services...")
    filename = create_categorized_json()
    print(f"🎉 Done! File saved as: {filename}")
