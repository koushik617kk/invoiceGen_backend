"""
Comprehensive comparison of all PDF generation approaches:
1. Original ReportLab approach
2. WeasyPrint + Jinja2 approach  
3. Playwright + Jinja2 approach
"""

import os
import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime, date

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all PDF renderers
try:
    from pdf_render import render_invoice_pdf as reportlab_render
    from pdf_render_modern import render_invoice_pdf as weasyprint_render
    from pdf_render_playwright import render_invoice_pdf as playwright_render
    print("✓ Successfully imported all PDF renderers")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    print("playwright install")
    sys.exit(1)


class MockInvoice:
    """Mock invoice class for testing"""
    def __init__(self):
        self.invoice_number = "INV-2024-001"
        self.date = date(2024, 1, 15)
        self.due_date = date(2024, 2, 15)
        self.financial_year = "2024-25"
        self.place_of_supply = "Delhi"
        self.subtotal = 1000.00
        self.discount = 50.00
        self.taxable_value = 950.00
        self.cgst = 85.50
        self.sgst = 85.50
        self.igst = 0.00
        self.round_off = 0.00
        self.total = 1121.00
        self.total_in_words = "One Thousand One Hundred Twenty One Rupees Only"
        self.terms_and_conditions = "Payment due within 30 days of invoice date."
        
        # Mock buyer
        self.buyer = MockBuyer()
        
        # Mock items
        self.items = [
            MockInvoiceItem("Web Development Services", "998314", "Nos", 1, 1000.00, 5, 50.00, 950.00, 18, 1121.00),
            MockInvoiceItem("Domain Registration", "998314", "Nos", 1, 100.00, 0, 0.00, 100.00, 18, 118.00)
        ]


class MockBuyer:
    """Mock buyer class for testing"""
    def __init__(self):
        self.name = "ABC Company Pvt Ltd"
        self.gstin = "07AABCU9603R1ZX"
        self.address = "123 Business Street, New Delhi, 110001"
        self.phone = "+91-9876543210"
        self.email = "accounts@abccompany.com"


class MockInvoiceItem:
    """Mock invoice item class for testing"""
    def __init__(self, description, hsn_code, unit, quantity, rate, discount_percent, discount_amount, taxable_value, gst_rate, line_total):
        self.description = description
        self.hsn_code = hsn_code
        self.sac_code = None
        self.unit = unit
        self.quantity = quantity
        self.rate = rate
        self.discount_percent = discount_percent
        self.discount_amount = discount_amount
        self.taxable_value = taxable_value
        self.gst_rate = gst_rate
        self.line_total = line_total


class MockBusinessProfile:
    """Mock business profile class for testing"""
    def __init__(self):
        self.business_name = "Tech Solutions Pvt Ltd"
        self.gstin = "07TECHS1234R1ZX"
        self.pan = "TECHS1234R"
        self.address = "456 Tech Park, Sector 5, Gurgaon, Haryana 122001"
        self.phone = "+91-9876543210"
        self.email = "info@techsolutions.com"
        self.primary_color = "#1e40af"
        self.logo_path = None
        self.signature_path = None
        self.bank_account_name = "Tech Solutions Pvt Ltd"
        self.bank_name = "HDFC Bank"
        self.bank_branch = "Gurgaon Branch"
        self.bank_account_number = "1234567890123456"
        self.bank_ifsc = "HDFC0001234"
        self.upi_id = "techsolutions@hdfc"
        self.accepts_cash = "YES"
        self.cash_note = "Cash payments accepted at our office"
        self.default_terms = "Payment due within 30 days. Late payments subject to 2% monthly interest."


def test_reportlab_approach():
    """Test the original ReportLab approach"""
    print("\n" + "="*60)
    print("Testing REPORTLAB Approach (Original)")
    print("="*60)
    
    try:
        start_time = time.time()
        
        # Create mock data
        invoice = MockInvoice()
        business_profile = MockBusinessProfile()
        
        # Generate PDF using ReportLab
        pdf_bytes = reportlab_render(invoice, business_profile)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Save PDF for comparison
        output_path = "comparison_reportlab.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✓ ReportLab PDF generated successfully")
        print(f"  - File size: {len(pdf_bytes):,} bytes")
        print(f"  - Generation time: {generation_time:.3f} seconds")
        print(f"  - Output file: {output_path}")
        
        return pdf_bytes, generation_time
        
    except Exception as e:
        print(f"✗ Error generating ReportLab PDF: {e}")
        return None, 0


def test_weasyprint_approach():
    """Test the WeasyPrint approach"""
    print("\n" + "="*60)
    print("Testing WEASYPRINT Approach (Modern)")
    print("="*60)
    
    try:
        start_time = time.time()
        
        # Create mock data
        invoice = MockInvoice()
        business_profile = MockBusinessProfile()
        
        # Generate PDF using WeasyPrint
        pdf_bytes = weasyprint_render(invoice, business_profile)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Save PDF for comparison
        output_path = "comparison_weasyprint.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✓ WeasyPrint PDF generated successfully")
        print(f"  - File size: {len(pdf_bytes):,} bytes")
        print(f"  - Generation time: {generation_time:.3f} seconds")
        print(f"  - Output file: {output_path}")
        
        return pdf_bytes, generation_time
        
    except Exception as e:
        print(f"✗ Error generating WeasyPrint PDF: {e}")
        return None, 0


def test_playwright_approach():
    """Test the Playwright approach"""
    print("\n" + "="*60)
    print("Testing PLAYWRIGHT Approach (Browser-based)")
    print("="*60)
    
    try:
        start_time = time.time()
        
        # Create mock data
        invoice = MockInvoice()
        business_profile = MockBusinessProfile()
        
        # Generate PDF using Playwright
        pdf_bytes = playwright_render(invoice, business_profile)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Save PDF for comparison
        output_path = "comparison_playwright.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✓ Playwright PDF generated successfully")
        print(f"  - File size: {len(pdf_bytes):,} bytes")
        print(f"  - Generation time: {generation_time:.3f} seconds")
        print(f"  - Output file: {output_path}")
        
        return pdf_bytes, generation_time
        
    except Exception as e:
        print(f"✗ Error generating Playwright PDF: {e}")
        return None, 0


def compare_approaches(reportlab_time, weasyprint_time, playwright_time):
    """Compare all three approaches"""
    print("\n" + "="*60)
    print("COMPREHENSIVE COMPARISON")
    print("="*60)
    
    approaches = [
        ("ReportLab", reportlab_time),
        ("WeasyPrint", weasyprint_time),
        ("Playwright", playwright_time)
    ]
    
    # Sort by speed (fastest first)
    approaches.sort(key=lambda x: x[1] if x[1] > 0 else float('inf'))
    
    print("Performance Ranking (fastest to slowest):")
    for i, (name, time_taken) in enumerate(approaches, 1):
        if time_taken > 0:
            print(f"  {i}. {name}: {time_taken:.3f} seconds")
        else:
            print(f"  {i}. {name}: FAILED")
    
    # Calculate relative performance
    if reportlab_time > 0 and weasyprint_time > 0:
        weasyprint_speedup = reportlab_time / weasyprint_time
        print(f"\nWeasyPrint vs ReportLab: {weasyprint_speedup:.2f}x {'faster' if weasyprint_speedup > 1 else 'slower'}")
    
    if reportlab_time > 0 and playwright_time > 0:
        playwright_speedup = reportlab_time / playwright_time
        print(f"Playwright vs ReportLab: {playwright_speedup:.2f}x {'faster' if playwright_speedup > 1 else 'slower'}")
    
    if weasyprint_time > 0 and playwright_time > 0:
        playwright_vs_weasyprint = weasyprint_time / playwright_time
        print(f"Playwright vs WeasyPrint: {playwright_vs_weasyprint:.2f}x {'faster' if playwright_vs_weasyprint > 1 else 'slower'}")


def analyze_code_complexity():
    """Analyze code complexity of each approach"""
    print("\n" + "="*60)
    print("CODE COMPLEXITY ANALYSIS")
    print("="*60)
    
    # Count lines in each file
    files_to_analyze = [
        ("pdf_render.py", "ReportLab (Original)"),
        ("pdf_render_modern.py", "WeasyPrint (Modern)"),
        ("pdf_render_playwright.py", "Playwright (Browser)")
    ]
    
    for filename, name in files_to_analyze:
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                total_lines = len(lines)
                code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
                comment_lines = len([line for line in lines if line.strip().startswith('#')])
                
                print(f"\n{name}:")
                print(f"  - Total lines: {total_lines}")
                print(f"  - Code lines: {code_lines}")
                print(f"  - Comment lines: {comment_lines}")
                print(f"  - File size: {os.path.getsize(filename):,} bytes")
        except FileNotFoundError:
            print(f"\n{name}: File not found")


def main():
    """Main comparison function"""
    print("PDF Generation Approaches Comparison")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test all approaches
    reportlab_pdf, reportlab_time = test_reportlab_approach()
    weasyprint_pdf, weasyprint_time = test_weasyprint_approach()
    playwright_pdf, playwright_time = test_playwright_approach()
    
    # Compare approaches
    compare_approaches(reportlab_time, weasyprint_time, playwright_time)
    
    # Analyze code complexity
    analyze_code_complexity()
    
    # Summary and recommendations
    print("\n" + "="*60)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*60)
    
    working_approaches = []
    if reportlab_pdf:
        working_approaches.append(("ReportLab", reportlab_time, "Stable, fast, but complex code"))
    if weasyprint_pdf:
        working_approaches.append(("WeasyPrint", weasyprint_time, "Modern, maintainable, good CSS support"))
    if playwright_pdf:
        working_approaches.append(("Playwright", playwright_time, "Excellent CSS support, browser-based"))
    
    print(f"Working approaches: {len(working_approaches)}/3")
    
    if working_approaches:
        print("\nRecommendations:")
        print("1. For PRODUCTION: Use ReportLab if you need maximum speed and stability")
        print("2. For DEVELOPMENT: Use WeasyPrint for better maintainability and modern CSS")
        print("3. For COMPLEX LAYOUTS: Use Playwright for advanced CSS features")
        print("\nGenerated PDFs for comparison:")
        print("  - comparison_reportlab.pdf")
        print("  - comparison_weasyprint.pdf") 
        print("  - comparison_playwright.pdf")
    else:
        print("❌ No working approaches found. Please check dependencies.")


if __name__ == "__main__":
    main()
