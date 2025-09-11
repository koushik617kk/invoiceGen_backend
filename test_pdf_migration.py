"""
Migration script to test the new WeasyPrint-based PDF generation
and compare it with the existing ReportLab approach.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime, date
from io import BytesIO

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import both old and new PDF renderers
try:
    from pdf_render import render_invoice_pdf as old_render_invoice_pdf
    from pdf_render_modern import render_invoice_pdf as new_render_invoice_pdf, ModernPDFRenderer
    print("✓ Successfully imported both PDF renderers")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


class MockInvoice:
    """Mock invoice class for testing"""
    def __init__(self):
        self.invoice_number = "INV-2024-001"
        self.date = date(2024, 1, 15)
        self.due_date = date(2024, 2, 15)
        self.financial_year = "2024-25"
        self.place_of_supply = "Delhi"
        self.seller_state_code = "07"  # Haryana
        self.terms_and_conditions = "Payment due within 30 days of invoice date."
        
        # Mock buyer
        self.buyer = MockBuyer()
        
        # Mock items
        self.items = [
            MockInvoiceItem("Web Development Services", "998314", "Nos", 1, 1000.00, 5, 50.00, 950.00, 18, 1121.00),
            MockInvoiceItem("Domain Registration", "998314", "Nos", 1, 100.00, 0, 0.00, 100.00, 5, 105.00)
        ]
        
        # Calculate totals using the actual compute_totals function
        from tax import compute_totals
        self.subtotal, self.taxable_value, self.cgst, self.sgst, self.igst, self.total = compute_totals(
            self.items, self.seller_state_code, self.buyer.state_code
        )
        
        # Calculate discount (sum of all item discounts)
        self.discount = sum(
            (item.quantity * item.rate * item.discount_percent / 100) if item.discount_percent 
            else item.discount_amount if item.discount_amount 
            else 0 
            for item in self.items
        )
        
        self.round_off = 0.00
        self.total_in_words = "One Thousand Two Hundred Twenty Six Rupees Only"  # Will be updated based on actual total


class MockBuyer:
    """Mock buyer class for testing"""
    def __init__(self):
        self.name = "ABC Company Pvt Ltd"
        self.gstin = "07AABCU9603R1ZX"
        self.state_code = "07"  # Haryana (same as seller for intrastate)
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
        self.logo_path = None  # No logo for testing
        self.signature_path = None  # No signature for testing
        self.bank_account_name = "Tech Solutions Pvt Ltd"
        self.bank_name = "HDFC Bank"
        self.bank_branch = "Gurgaon Branch"
        self.bank_account_number = "1234567890123456"
        self.bank_ifsc = "HDFC0001234"
        self.upi_id = "techsolutions@hdfc"
        self.accepts_cash = "YES"
        self.cash_note = "Cash payments accepted at our office"
        self.default_terms = "Payment due within 30 days. Late payments subject to 2% monthly interest."


def test_old_pdf_generation():
    """Test the old ReportLab-based PDF generation"""
    print("\n" + "="*50)
    print("Testing OLD ReportLab PDF Generation")
    print("="*50)
    
    try:
        start_time = time.time()
        
        # Create mock data
        invoice = MockInvoice()
        business_profile = MockBusinessProfile()
        
        # Generate PDF using old method
        pdf_bytes = old_render_invoice_pdf(invoice, business_profile)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Save PDF for comparison
        output_path = "test_invoice_old.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✓ Old PDF generated successfully")
        print(f"  - File size: {len(pdf_bytes):,} bytes")
        print(f"  - Generation time: {generation_time:.3f} seconds")
        print(f"  - Output file: {output_path}")
        
        return pdf_bytes, generation_time
        
    except Exception as e:
        print(f"✗ Error generating old PDF: {e}")
        return None, 0


def test_new_pdf_generation():
    """Test the new WeasyPrint-based PDF generation"""
    print("\n" + "="*50)
    print("Testing NEW WeasyPrint PDF Generation")
    print("="*50)
    
    try:
        start_time = time.time()
        
        # Create mock data
        invoice = MockInvoice()
        business_profile = MockBusinessProfile()
        
        # Generate PDF using new method
        pdf_bytes = new_render_invoice_pdf(invoice, business_profile)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Save PDF for comparison
        output_path = "test_invoice_new.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✓ New PDF generated successfully")
        print(f"  - File size: {len(pdf_bytes):,} bytes")
        print(f"  - Generation time: {generation_time:.3f} seconds")
        print(f"  - Output file: {output_path}")
        
        return pdf_bytes, generation_time
        
    except Exception as e:
        print(f"✗ Error generating new PDF: {e}")
        return None, 0


def test_modern_renderer_features():
    """Test additional features of the modern renderer"""
    print("\n" + "="*50)
    print("Testing Modern Renderer Features")
    print("="*50)
    
    try:
        renderer = ModernPDFRenderer()
        
        # Test template validation
        print("✓ Testing template validation...")
        is_valid = renderer.validate_template("invoice_template.html")
        print(f"  - Template valid: {is_valid}")
        
        # Test available templates
        print("✓ Testing template discovery...")
        templates = renderer.get_available_templates()
        print(f"  - Available templates: {templates}")
        
        # Test custom CSS rendering
        print("✓ Testing custom CSS rendering...")
        invoice = MockInvoice()
        business_profile = MockBusinessProfile()
        
        custom_css = """
        body { background-color: #f0f0f0; }
        .company-name { color: #ff0000 !important; }
        """
        
        pdf_bytes = renderer.render_invoice_with_custom_css(
            invoice, business_profile, custom_css=custom_css
        )
        
        output_path = "test_invoice_custom_css.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"  - Custom CSS PDF generated: {output_path}")
        print(f"  - File size: {len(pdf_bytes):,} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing modern features: {e}")
        return False


def compare_performance(old_time, new_time):
    """Compare performance between old and new approaches"""
    print("\n" + "="*50)
    print("Performance Comparison")
    print("="*50)
    
    if old_time > 0 and new_time > 0:
        speedup = old_time / new_time
        print(f"Old method time: {old_time:.3f} seconds")
        print(f"New method time: {new_time:.3f} seconds")
        print(f"Speedup: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    else:
        print("Cannot compare performance due to errors")


def main():
    """Main test function"""
    print("PDF Generation Migration Test")
    print("="*50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test old PDF generation
    old_pdf, old_time = test_old_pdf_generation()
    
    # Test new PDF generation
    new_pdf, new_time = test_new_pdf_generation()
    
    # Test modern renderer features
    modern_features_ok = test_modern_renderer_features()
    
    # Compare performance
    compare_performance(old_time, new_time)
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    print(f"Old PDF generation: {'✓ PASS' if old_pdf else '✗ FAIL'}")
    print(f"New PDF generation: {'✓ PASS' if new_pdf else '✗ FAIL'}")
    print(f"Modern features: {'✓ PASS' if modern_features_ok else '✗ FAIL'}")
    
    if old_pdf and new_pdf:
        print("\n🎉 Both PDF generation methods are working!")
        print("You can now compare the generated PDFs:")
        print("  - test_invoice_old.pdf (ReportLab)")
        print("  - test_invoice_new.pdf (WeasyPrint)")
        print("  - test_invoice_custom_css.pdf (WeasyPrint with custom CSS)")
        print("\nRecommendation: Migrate to the new WeasyPrint approach for better maintainability!")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
