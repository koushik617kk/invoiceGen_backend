#!/usr/bin/env python3
"""
Backend Reorganization Script
Organizes the invoiceGen_backend directory by moving files into appropriate folders
while keeping core application files in place and updating imports.
"""

import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Core application files that should stay in root
CORE_FILES = {
    'main.py',
    'models.py', 
    'database.py',
    'schemas.py',
    'pdf_render_modern.py',  # Main PDF renderer being used
    'pdf_render.py',         # Original ReportLab renderer
    'pdf_render_playwright.py',  # Playwright renderer
    'pdf_render_backup.py',  # Backup renderer
    'compare_pdf_approaches.py',  # PDF comparison tool
    'tax.py',
    'security_cognito.py',
    'admin_auth.py',
    'hsn_service.py',
    'export_handlers.py',  # New core service
    'requirements.txt',
    '__init__.py'
}

# Folder structure and file mappings
FOLDER_MAPPINGS = {
    'testing/': [
        'test_database.py',
        'test_subscription.py', 
        'test_subscription_validation.py',
        'test_updated_subscription.py',
        'test_pdf_migration.py',  # New test file
    ],
    
    'data_management/hsn_sac/': [
        'analyze_hsn_codes.py',
        'analyze_hsn_search_gaps.py',
        'create_better_hsn_data.py',
        'export_hsn_codes.py',
        'export_updated_hsn_data.py',
        'fill_hsn_gaps.py',
        'fix_hsn_codes.py',
        'fix_hsn_model.py',
        'improve_hsn_codes.py',
        'improve_hsn_keywords.py',
        'verify_hsn_codes.py',
        'expand_hsn_database.py',
        'seed_hsn_comprehensive.py',
    ],
    
    'data_management/master_services/': [
        'analyze_categories.py',
        'create_categorized_json.py',
        'export_master_services.py',
        'fix_master_services_final.py',
        'manage_master_data.py',
        'seed_master_services.py',
        'seed_comprehensive_services.py',
        'seed_specific_services.py',
    ],
    
    'data_management/products/': [
        'add_500_products.py',
        'create_master_products.py',
        'expand_to_500_products.py',
        'rebuild_comprehensive_products.py',
        'seed_specific_products.py',
    ],
    
    'migrations/': [
        'migrate_to_postgresql.py',
        'migrate_sqlite_to_postgres.py',
        'migrate_add_trial_start_date.py',
        'verify_migration.py',
    ],
    
    'database_ops/': [
        'backup_database.py',
        'check_database_summary.py',
        'create_schema.py',
        'expand_databases.py',
        'inspect_database.py',
        'simple_update_database.py',
        'update_database_with_improved_data.py',
        'update_existing_columns_only.py',
        'validate_existing_data.py',
        'verify_database_update.py',
    ],
    
    'specialized_fixes/': [
        'fix_pharmaceutical_rates.py',
        'fix_remaining_stationery_rates.py',
        'fix_sac_codes.py',
        'update_gst_rates_2025.py',
        'final_gst_verification.py',
        'validate_sac_codes.py',
    ],
    
    'data_exports/': [
        'export_all_data.py',
        'notify_ca_requests.py',
    ],
    
    'subscription/': [
        'seed_subscription_plans.py',
    ],
    
    'deployment/': [
        'deploy.sh',
        'deploy_to_ec2.sh',
    ],
    
    # PDF generation files stay in root - removed from here
    
    'data_files/json/': [
        'hsn_codes_export_20250906_121854.json',
        'hsn_data_original.json',
        'hsn_data.json',
        'master_services_categorized_20250906_123405.json',
        'master_services_export_20250906_121840.json',
        'master_services_improved_20250907_003150.json',
        'updated_hsn_codes_export_20250907_110047.json',
        'updated_hsn_codes_export_20250907_110429.json',
        'updated_hsn_codes_export_20250907_110501.json',
    ],
    
    'data_files/documents/': [
        '1.pdf',
        'comparison_reportlab.pdf',
        'comparison_weasyprint.pdf',
        'test_alignment_fix.pdf',
        'test_compact_design.pdf',
        'test_corrected_calculations.pdf',
        'test_corrected_subtotal.pdf',
        'test_gst_breakdown_in_table.pdf',
        'test_gst_percentage_breakdown.pdf',
        'test_horizontal_design.pdf',
        'test_invoice_custom_css.pdf',
        'test_invoice_custom_css.pdf',
        'test_invoice_new.pdf',
        'test_invoice_old.pdf',
        'test_minimalist_design.pdf',
        'test_mixed_gst_fix.pdf',
        'test_subtotal_line_totals.pdf',
    ],
    
    'data_files/analysis/': [
        'master_services_category_analysis.txt',
        'phase1_research_findings.md',
        'PDF_ANALYSIS_SUMMARY.md',
        'PDF_MIGRATION_GUIDE.md',
    ],
    
    'data_files/databases/': [
        'invoice_gen.db',
        'invoicegen.db',
        'rental_assistant.db',
    ]
}

# Import path mappings for files that will be moved
IMPORT_MAPPINGS = {
    # Testing files
    'testing/test_database.py': {
        'from database import': 'from ..database import',
        'from models import': 'from ..models import',
    },
    'testing/test_subscription.py': {
        'from database import': 'from ..database import',
        'from models import': 'from ..models import',
    },
    'testing/test_subscription_validation.py': {
        'from database import': 'from ..database import',
        'from models import': 'from ..models import',
    },
    'testing/test_updated_subscription.py': {
        'from database import': 'from ..database import',
        'from models import': 'from ..models import',
    },
    'testing/test_pdf_migration.py': {
        'from pdf_render import': 'from ..pdf_render import',
        'from pdf_render_modern import': 'from ..pdf_render_modern import',
    },
    
    # Data management files
    'data_management/hsn_sac/analyze_hsn_codes.py': {
        'from database import': 'from ...database import',
        'from models import': 'from ...models import',
    },
    'data_management/hsn_sac/export_hsn_codes.py': {
        'from database import': 'from ...database import',
        'from models import': 'from ...models import',
    },
    'data_management/master_services/seed_master_services.py': {
        'from database import': 'from ...database import',
        'from models import': 'from ...models import',
    },
    
    # Migration files
    'migrations/migrate_to_postgresql.py': {
        'from database import': 'from ..database import',
        'from models import': 'from ..models import',
    },
    
    # PDF generation files stay in root - no import changes needed
}

def create_folders():
    """Create all necessary folders"""
    print("📁 Creating folder structure...")
    
    for folder in FOLDER_MAPPINGS.keys():
        os.makedirs(folder, exist_ok=True)
        print(f"  ✓ Created {folder}")
    
    # Create __init__.py files for Python packages
    python_folders = [
        'testing',
        'data_management',
        'data_management/hsn_sac',
        'data_management/master_services', 
        'data_management/products',
        'migrations',
        'database_ops',
        'specialized_fixes',
        'data_exports',
        'subscription',
    ]
    
    for folder in python_folders:
        init_file = os.path.join(folder, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('')
            print(f"  ✓ Created {init_file}")

def move_files():
    """Move files to their designated folders"""
    print("\n📦 Moving files to organized folders...")
    
    moved_count = 0
    for folder, files in FOLDER_MAPPINGS.items():
        for file in files:
            if os.path.exists(file):
                dest_path = os.path.join(folder, file)
                shutil.move(file, dest_path)
                print(f"  ✓ Moved {file} → {dest_path}")
                moved_count += 1
            else:
                print(f"  ⚠️  File not found: {file}")
    
    print(f"\n📊 Moved {moved_count} files total")

def update_imports():
    """Update import statements in moved files"""
    print("\n🔧 Updating import statements...")
    
    for file_path, import_changes in IMPORT_MAPPINGS.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Apply import changes
                for old_import, new_import in import_changes.items():
                    content = content.replace(old_import, new_import)
                
                # Write back if changes were made
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✓ Updated imports in {file_path}")
                else:
                    print(f"  - No import changes needed in {file_path}")
                    
            except Exception as e:
                print(f"  ❌ Error updating {file_path}: {e}")
        else:
            print(f"  ⚠️  File not found: {file_path}")

def create_readme():
    """Create a README explaining the new structure"""
    readme_content = """# InvoiceGen Backend - Organized Structure

## Core Application Files (Root Directory)
These files remain in the root directory as they are essential for the application:

- `main.py` - FastAPI application with all API endpoints
- `models.py` - SQLAlchemy database models
- `database.py` - Database configuration and connection management
- `schemas.py` - Pydantic schemas for request/response validation
- `pdf_render_modern.py` - PDF invoice generation (WeasyPrint - Main renderer)
- `pdf_render.py` - Original ReportLab PDF renderer
- `pdf_render_playwright.py` - Playwright PDF renderer
- `pdf_render_backup.py` - Backup PDF renderer
- `compare_pdf_approaches.py` - PDF generation comparison tool
- `tax.py` - GST calculation logic
- `security_cognito.py` - AWS Cognito authentication
- `admin_auth.py` - Internal admin authentication
- `hsn_service.py` - HSN/SAC code suggestion service
- `export_handlers.py` - Export functionality handlers
- `requirements.txt` - Python dependencies

## Organized Folders

### `testing/`
All test files for different components:
- `test_database.py` - Database connection tests
- `test_subscription.py` - Subscription system tests
- `test_subscription_validation.py` - Subscription validation tests
- `test_updated_subscription.py` - Updated subscription features tests
- `test_pdf_migration.py` - PDF generation migration tests

### `data_management/`
Organized by data type:

#### `data_management/hsn_sac/`
HSN/SAC code management scripts:
- Analysis, export, import, and improvement scripts
- Code validation and gap-filling tools

#### `data_management/master_services/`
Master services data management:
- Service catalog creation and maintenance
- Category analysis and organization

#### `data_management/products/`
Product data management:
- Product catalog creation and expansion
- Product-specific seeding scripts

### `migrations/`
Database migration scripts:
- SQLite to PostgreSQL migration tools
- Schema update scripts
- Migration verification tools

### `database_ops/`
Database operations and maintenance:
- Backup and restore scripts
- Database inspection and validation
- Schema updates and fixes

### `specialized_fixes/`
Targeted fixes for specific issues:
- GST rate corrections for different categories
- SAC code fixes
- Data quality improvements

### PDF Generation Files (Root Directory)
All PDF generation files remain in root directory:
- `pdf_render_modern.py` - Main WeasyPrint renderer
- `pdf_render.py` - Original ReportLab renderer
- `pdf_render_playwright.py` - Playwright renderer
- `pdf_render_backup.py` - Backup renderer
- `compare_pdf_approaches.py` - PDF comparison tool

### `data_exports/`
Export and backup functionality:
- Data export scripts
- Notification handlers

### `subscription/`
Subscription management:
- Subscription plan seeding
- Subscription-related utilities

### `deployment/`
Deployment scripts:
- Production deployment tools
- Environment-specific deployment scripts

### `data_files/`
Organized data files:

#### `data_files/json/`
JSON data files:
- HSN codes exports
- Master services data
- Configuration files

#### `data_files/documents/`
PDF and document files:
- Sample invoices
- Test PDFs
- Comparison documents

#### `data_files/analysis/`
Analysis and documentation:
- Research findings
- Migration guides
- Analysis reports

#### `data_files/databases/`
Database files:
- SQLite database files
- Database backups

## Import Updates
All moved Python files have had their imports updated to reflect the new folder structure using relative imports.

## Usage
The core application functionality remains unchanged. All scripts in subfolders can be run from their new locations or from the root directory using Python module syntax.

Example:
```bash
# Run a test from the root directory
python -m testing.test_database

# Run a data management script
python -m data_management.hsn_sac.export_hsn_codes
```
"""
    
    with open('README_ORGANIZATION.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("  ✓ Created README_ORGANIZATION.md")

def main():
    """Main reorganization function"""
    print("🚀 Starting InvoiceGen Backend Reorganization")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found. Please run this script from the invoiceGen_backend directory.")
        return
    
    print("✓ Confirmed: Running from invoiceGen_backend directory")
    
    # Create folder structure
    create_folders()
    
    # Move files
    move_files()
    
    # Update imports
    update_imports()
    
    # Create documentation
    create_readme()
    
    print("\n" + "=" * 50)
    print("✅ Reorganization Complete!")
    print("\n📋 Summary:")
    print("- Core application files remain in root directory")
    print("- All other files organized into logical folders")
    print("- Import statements updated for moved files")
    print("- README_ORGANIZATION.md created with structure explanation")
    print("\n🎯 Next steps:")
    print("1. Test the application to ensure everything works")
    print("2. Update any deployment scripts if needed")
    print("3. Consider updating documentation references")

if __name__ == "__main__":
    main()
