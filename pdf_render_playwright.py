"""
Modern PDF generation using Playwright (headless browser).
This approach is often faster than WeasyPrint and handles complex CSS better.
"""

import os
import asyncio
from io import BytesIO
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.async_api import async_playwright


class PlaywrightPDFRenderer:
    """
    PDF renderer using Playwright (headless browser).
    Provides excellent CSS support and fast rendering.
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
    
    async def render_invoice_pdf_async(self, invoice, business_profile=None, 
                                     template_name: str = "invoice_template.html") -> bytes:
        """
        Generate PDF invoice using Playwright (async version).
        
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
            
            # Generate PDF using Playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Set content and wait for it to load
                await page.set_content(html_content)
                await page.wait_for_load_state('networkidle')
                
                # Generate PDF with optimized settings
                pdf_bytes = await page.pdf(
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '16mm',
                        'right': '16mm',
                        'bottom': '16mm',
                        'left': '16mm'
                    }
                )
                
                await browser.close()
                return pdf_bytes
                
        except Exception as e:
            print(f"Error generating PDF with Playwright: {e}")
            # Fallback to simple error PDF
            return await self._generate_error_pdf_async(str(e))
    
    def render_invoice_pdf(self, invoice, business_profile=None, 
                          template_name: str = "invoice_template.html") -> bytes:
        """
        Synchronous wrapper for the async PDF generation.
        
        Args:
            invoice: Invoice object with all invoice data
            business_profile: Business profile object with company details
            template_name: Name of the HTML template to use
            
        Returns:
            bytes: PDF content as bytes
        """
        return asyncio.run(self.render_invoice_pdf_async(invoice, business_profile, template_name))
    
    async def _generate_error_pdf_async(self, error_message: str) -> bytes:
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
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(error_html)
            pdf_bytes = await page.pdf(format='A4')
            await browser.close()
            return pdf_bytes
    
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
    Backward compatible function that uses the Playwright renderer.
    This maintains the same interface as the original function.
    """
    renderer = PlaywrightPDFRenderer()
    return renderer.render_invoice_pdf(invoice, business_profile)


def render_default_pdf(invoice, business_profile=None) -> bytes:
    """
    Backward compatible function for default PDF generation.
    This maintains the same interface as the original function.
    """
    renderer = PlaywrightPDFRenderer()
    return renderer.render_invoice_pdf(invoice, business_profile)


if __name__ == "__main__":
    # Example usage
    renderer = PlaywrightPDFRenderer()
    print("Available templates:", renderer.get_available_templates())
    print("Template validation:", renderer.validate_template("invoice_template.html"))
