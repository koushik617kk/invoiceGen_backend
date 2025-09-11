"""
Modern PDF generation using WeasyPrint and Jinja2 templates.
This approach is much cleaner, more maintainable, and leverages web technologies.
"""

import os
from io import BytesIO
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


class ModernPDFRenderer:
    """
    Modern PDF renderer using WeasyPrint and Jinja2 templates.
    Provides clean separation of concerns and easier maintenance.
    """
    
    def __init__(self, template_dir: str = "templates"):
        """
        Initialize the PDF renderer with template directory.
        
        Args:
            template_dir: Directory containing HTML templates
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Font configuration for better text rendering
        self.font_config = FontConfiguration()
    
    def render_invoice_pdf(self, invoice, business_profile=None, template_name: str = "invoice_template.html") -> bytes:
        """
        Generate PDF invoice using modern HTML/CSS approach.
        
        Args:
            invoice: Invoice object with all invoice data
            business_profile: Business profile object with company details
            template_name: Name of the HTML template to use
            
        Returns:
            bytes: PDF content as bytes
        """
        try:
            # Load and render template
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(
                invoice=invoice,
                business_profile=business_profile
            )
            
            # Generate PDF using WeasyPrint
            html_doc = HTML(string=html_content)
            
            # Create PDF with optimized settings
            pdf_bytes = html_doc.write_pdf(
                font_config=self.font_config,
                optimize_images=True,
                jpeg_quality=95
            )
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            # Fallback to simple error PDF
            return self._generate_error_pdf(str(e))
    
    def _generate_error_pdf(self, error_message: str) -> bytes:
        """
        Generate a simple error PDF when template rendering fails.
        
        Args:
            error_message: Error message to display
            
        Returns:
            bytes: Error PDF content
        """
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>PDF Generation Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; }}
                .error {{ color: #dc2626; font-size: 18px; }}
            </style>
        </head>
        <body>
            <h1 class="error">PDF Generation Error</h1>
            <p>An error occurred while generating the PDF:</p>
            <p><code>{error_message}</code></p>
            <p>Please contact support if this issue persists.</p>
        </body>
        </html>
        """
        
        html_doc = HTML(string=error_html)
        return html_doc.write_pdf(font_config=self.font_config)
    
    def render_invoice_with_custom_css(self, invoice, business_profile=None, 
                                     template_name: str = "invoice_template.html",
                                     custom_css: Optional[str] = None) -> bytes:
        """
        Generate PDF with custom CSS styling.
        
        Args:
            invoice: Invoice object with all invoice data
            business_profile: Business profile object with company details
            template_name: Name of the HTML template to use
            custom_css: Custom CSS string to apply
            
        Returns:
            bytes: PDF content as bytes
        """
        try:
            # Load and render template
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(
                invoice=invoice,
                business_profile=business_profile
            )
            
            # Generate PDF with custom CSS
            html_doc = HTML(string=html_content)
            
            if custom_css:
                css_doc = CSS(string=custom_css)
                pdf_bytes = html_doc.write_pdf(
                    stylesheets=[css_doc],
                    font_config=self.font_config,
                    optimize_images=True,
                    jpeg_quality=95
                )
            else:
                pdf_bytes = html_doc.write_pdf(
                    font_config=self.font_config,
                    optimize_images=True,
                    jpeg_quality=95
                )
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Error generating PDF with custom CSS: {e}")
            return self._generate_error_pdf(str(e))
    
    def get_available_templates(self) -> list:
        """
        Get list of available HTML templates.
        
        Returns:
            list: List of template filenames
        """
        if not self.template_dir.exists():
            return []
        
        return [f.name for f in self.template_dir.glob("*.html")]
    
    def validate_template(self, template_name: str) -> bool:
        """
        Validate that a template exists and is valid.
        
        Args:
            template_name: Name of template to validate
            
        Returns:
            bool: True if template is valid, False otherwise
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return True
        except Exception:
            return False


# Backward compatibility functions
def render_invoice_pdf(invoice, business_profile=None, template=None) -> bytes:
    """
    Backward compatible function that uses the modern renderer.
    This maintains the same interface as the original function.
    """
    renderer = ModernPDFRenderer()
    return renderer.render_invoice_pdf(invoice, business_profile)


def render_default_pdf(invoice, business_profile=None) -> bytes:
    """
    Backward compatible function for default PDF generation.
    This maintains the same interface as the original function.
    """
    renderer = ModernPDFRenderer()
    return renderer.render_invoice_pdf(invoice, business_profile)


# Example usage and testing functions
def test_pdf_generation():
    """
    Test function to verify PDF generation works correctly.
    """
    # This would be used for testing with sample data
    pass


if __name__ == "__main__":
    # Example usage
    renderer = ModernPDFRenderer()
    print("Available templates:", renderer.get_available_templates())
    print("Template validation:", renderer.validate_template("invoice_template.html"))
