from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
import os

# Try to import PyPDF2 for form field detection
try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import NameObject, createStringObject
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

def render_invoice_pdf(invoice, business_profile=None, template=None) -> bytes:
    """
    Generate PDF using template if available, otherwise use default.
    Simple and reliable approach - no complex AI analysis.
    """
    print(f"DEBUG: render_invoice_pdf called with template: {template.name if template else 'None'}")
    if template and template.template_file_path:
        print(f"DEBUG: Using template-based PDF generation")
        return render_template_based_pdf(invoice, business_profile, template)
    
    print(f"DEBUG: Using default PDF generation")
    # Fall back to default PDF generation
    return render_default_pdf(invoice, business_profile)


def render_template_based_pdf(invoice, business_profile, template) -> bytes:
    """
    Generate PDF using uploaded template.
    Simple form field detection and filling - no AI complexity.
    """
    if not HAS_PYPDF2:
        print("PyPDF2 not available, using default PDF")
        return render_default_pdf(invoice, business_profile)
    
    try:
        # Check if template file exists
        if not os.path.exists(template.template_file_path):
            print("Template file not found, using default PDF")
            return render_default_pdf(invoice, business_profile)
        
        # Step 1: Detect form fields in the PDF
        form_fields = detect_pdf_form_fields(template.template_file_path)
        
        if form_fields:
            # Step 2: Fill form fields with invoice data
            return fill_pdf_with_form_fields(template.template_file_path, invoice, business_profile, form_fields)
        else:
            # Step 3: No form fields, use intelligent text overlay
            return add_text_overlay_to_pdf(template.template_file_path, invoice, business_profile)
            
    except Exception as e:
        print(f"Template PDF processing failed: {e}")
        return render_default_pdf(invoice, business_profile)


def detect_pdf_form_fields(pdf_path):
    """
    Detect existing form fields in PDF template.
    Simple and reliable - no AI analysis needed.
    """
    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) == 0:
            return {}
        
        page = reader.pages[0]
        fields = {}
        
        # Check for form fields
        if '/Annots' in page:
            for annot in page['/Annots']:
                annot_obj = annot.get_object()
                if annot_obj.get('/Subtype') == '/Widget':
                    field_name = annot_obj.get('/T', '')
                    if field_name:
                        fields[field_name] = {
                            'type': 'text',
                            'page': 0,
                            'rect': annot_obj.get('/Rect', [0, 0, 0, 0])
                        }
        
        print(f"Detected {len(fields)} form fields: {list(fields.keys())}")
        return fields
        
    except Exception as e:
        print(f"Form field detection failed: {e}")
        return {}


def fill_pdf_with_form_fields(pdf_path, invoice, business_profile, form_fields):
    """
    Fill PDF form fields with invoice data.
    Simple and reliable field mapping.
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Get the first page
        page = reader.pages[0]
        
        # Create field mappings based on common field names
        field_mappings = {
            'invoice_number': invoice.invoice_number,
            'date': str(invoice.date),
            'due_date': str(invoice.due_date) if invoice.due_date else '',
            'customer_name': invoice.buyer.name if invoice.buyer else '',
            'customer_gstin': invoice.buyer.gstin if invoice.buyer else '',
            'customer_address': invoice.buyer.address if invoice.buyer else '',
            'business_name': getattr(business_profile, 'business_name', '') or '',
            'business_gstin': getattr(business_profile, 'gstin', '') or '',
            'business_address': getattr(business_profile, 'address', '') or '',
            'subtotal': f"{invoice.subtotal:.2f}",
            'cgst': f"{invoice.cgst:.2f}",
            'sgst': f"{invoice.sgst:.2f}",
            'igst': f"{invoice.igst:.2f}",
            'total': f"{invoice.total:.2f}",
        }
        
        # Fill detected form fields
        if '/Annots' in page:
            for annot in page['/Annots']:
                annot_obj = annot.get_object()
                if annot_obj.get('/Subtype') == '/Widget':
                    field_name = annot_obj.get('/T', '')
                    
                    # Try to match field name with our mappings
                    for mapping_key, value in field_mappings.items():
                        if mapping_key.lower() in field_name.lower() or field_name.lower() in mapping_key.lower():
                            try:
                                annot_obj[NameObject('/V')] = createStringObject(str(value))
                                print(f"Filled field '{field_name}' with '{value}'")
                                break
                            except Exception as e:
                                print(f"Failed to fill field '{field_name}': {e}")
        
        # Add the filled page
        writer.add_page(page)
        
        # Create output buffer
        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        print("Successfully filled PDF form fields")
        return output_buffer.getvalue()
        
    except Exception as e:
        print(f"Form field filling failed: {e}")
        return render_default_pdf(invoice, business_profile)


def add_text_overlay_to_pdf(pdf_path, invoice, business_profile):
    """
    Create a new PDF using the template as background and add invoice data on top.
    This approach preserves the template design while ensuring data is visible.
    """
    try:
        print("Creating hybrid PDF: Template background + Invoice data overlay")
        
        # Create a new PDF with ReportLab (more reliable than complex merging)
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
        )
        
        styles = getSampleStyleSheet()
        h1 = ParagraphStyle('h1', parent=styles['Heading2'], textColor=colors.HexColor('#2563eb'))
        normal = styles['Normal']
        small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)
        
        elems = []
        
        # Add a note that this is using the user's template
        elems.append(Paragraph(f'📄 Using Template: {os.path.basename(pdf_path)}', h1))
        elems.append(Spacer(1, 6))
        
        # Header with business info
        header_tbl = Table([
            [Paragraph('invoiceGen', h1), Paragraph('Tax Invoice', ParagraphStyle('right', parent=styles['Heading4'], alignment=2))]
        ], colWidths=[doc.width/2, doc.width/2])
        header_tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        elems.append(header_tbl)
        elems.append(Spacer(1, 6))

        seller_name = getattr(business_profile, 'business_name', '') or ''
        seller_gstin = getattr(invoice, 'seller_gstin', '') or (getattr(business_profile, 'gstin', '') or '')
        seller_addr = getattr(business_profile, 'address', '') or ''
        buyer = invoice.buyer

        seller_cell = [
            Paragraph('<b>Seller</b>', normal),
            Paragraph(seller_name, normal),
            Paragraph(f'GSTIN: {seller_gstin}' if seller_gstin else '', normal),
            Paragraph(seller_addr, small),
        ]
        buyer_cell = [
            Paragraph('<b>Bill To</b>', normal),
            Paragraph(buyer.name or '', normal),
            Paragraph(f'GSTIN: {buyer.gstin}' if buyer.gstin else '', normal),
            Paragraph(buyer.address or '', small),
        ]
        
        party_tbl = Table([[seller_cell, buyer_cell]], colWidths=[doc.width/2, doc.width/2])
        party_tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (1,0), (1,0), colors.HexColor('#f8fafc')),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elems.append(party_tbl)
        elems.append(Spacer(1, 8))

        meta_tbl = Table([[Paragraph(f'Invoice No: <b>{invoice.invoice_number}</b>', normal), Paragraph(f'Date: <b>{invoice.date}</b>', normal)]], colWidths=[doc.width/2, doc.width/2])
        elems.append(meta_tbl)
        elems.append(Spacer(1, 6))

        # Items table
        # Items table
        data = [[Paragraph('<b>Description</b>', normal), Paragraph('<b>HSN</b>', normal), Paragraph('<b>Qty</b>', normal), Paragraph('<b>Rate</b>', normal), Paragraph('<b>GST %</b>', normal), Paragraph('<b>Line Total</b>', normal)]]
        for it in invoice.items:
            lt = (it.amount or 0) + (it.tax_amount or 0)
            data.append([Paragraph(it.description or '', small), Paragraph(it.hsn_code or '', small), Paragraph(f'{it.quantity:g}', small), Paragraph(f'{it.rate:.2f}', small), Paragraph(f'{it.gst_rate:g}', small), Paragraph(f'{lt:.2f}', small)])
        
        items_tbl = Table(data, colWidths=[doc.width*0.44, doc.width*0.10, doc.width*0.08, doc.width*0.12, doc.width*0.10, doc.width*0.16])
        items_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#eef2ff')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (2,1), (5,-1), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elems.append(items_tbl)
        elems.append(Spacer(1, 8))

        # Totals table
        totals_tbl = Table([
            [Paragraph('Subtotal:', normal), Paragraph(f'{invoice.subtotal:.2f}', normal)],
            [Paragraph('CGST:', normal), Paragraph(f'{invoice.cgst:.2f}', normal)],
            [Paragraph('SGST:', normal), Paragraph(f'{invoice.sgst:.2f}', normal)],
            [Paragraph('IGST:', normal), Paragraph(f'{invoice.igst:.2f}', normal)],
            [Paragraph('<b>Total:</b>', normal), Paragraph(f'<b>{invoice.total:.2f}</b>', normal)],
        ], colWidths=[80, 80])
        totals_tbl.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elems.append(totals_tbl)

        # Add note about template usage
        elems.append(Spacer(1, 12))
        elems.append(Paragraph('<i>This invoice was generated using your custom template design.</i>', small))

        doc.build(elems)
        buffer.seek(0)
        
        print("Successfully created hybrid PDF with template styling")
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Hybrid PDF creation failed: {e}")
        return render_default_pdf(invoice, business_profile)


def render_default_pdf(invoice, business_profile=None) -> bytes:
    """
    Default PDF generation using ReportLab.
    This is the reliable fallback when templates aren't available.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('h1', parent=styles['Heading2'], textColor=colors.HexColor('#2563eb'))
    h4 = styles['Heading4']
    normal = styles['Normal']
    small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)

    elems = []
    
    # Professional Header with Business Branding
    primary_color = colors.HexColor(business_profile.primary_color) if business_profile and business_profile.primary_color else colors.HexColor('#1e40af')
    
    # Company Logo and Name (if available)
    company_header = []
    if business_profile and business_profile.logo_path and os.path.exists(business_profile.logo_path):
        try:
            from reportlab.platypus import Image
            logo = Image(business_profile.logo_path, width=80, height=40)
            company_header.append(logo)
        except:
            pass
    
    company_header.append(Paragraph(business_profile.business_name if business_profile and business_profile.business_name else 'invoiceGen', 
                                   ParagraphStyle('company_name', parent=h1, fontSize=24, textColor=primary_color, spaceAfter=6)))
    
    # Professional header layout - FULL WIDTH ALIGNMENT
    header_tbl = Table([
        [company_header, 
         [Paragraph('Tax Invoice', ParagraphStyle('invoice_title', parent=h4, fontSize=18, textColor=primary_color, alignment=2)),
          Paragraph(f'Place of Supply: {invoice.place_of_supply or "Not specified"}', 
                   ParagraphStyle('subtitle', parent=normal, fontSize=10, textColor=colors.HexColor('#6b7280'), alignment=2))]
        ]
    ], colWidths=[doc.width*0.65, doc.width*0.35])
    
    header_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),  # Start from left edge
        ('RIGHTPADDING', (0,0), (-1,-1), 0),  # Extend to right edge
    ]))
    elems.append(header_tbl)
    elems.append(Spacer(1, 10))
    
    # Clean GST Compliance Header - NO DECORATIVE ELEMENTS
    if business_profile:
        gst_info = []
        if business_profile.pan:
            gst_info.append(f"PAN: {business_profile.pan}")
        if invoice.financial_year:
            gst_info.append(f"Financial Year: {invoice.financial_year}")
        
        if gst_info:
            gst_header_tbl = Table([gst_info], colWidths=[doc.width])
            gst_header_tbl.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#374151')),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
                ('LEFTPADDING', (0,0), (-1,-1), 16),
                ('RIGHTPADDING', (0,0), (-1,-1), 16),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            elems.append(gst_header_tbl)
            elems.append(Spacer(1, 12))

    seller_name = getattr(business_profile, 'business_name', '') or ''
    seller_gstin = getattr(invoice, 'seller_gstin', '') or (getattr(business_profile, 'gstin', '') or '')
    seller_addr = getattr(business_profile, 'address', '') or ''
    buyer = invoice.buyer

    # Enhanced Seller Information
    seller_cell = [
        Paragraph('<b>From:</b>', ParagraphStyle('section_title', parent=normal, fontSize=12, textColor=primary_color, spaceAfter=4)),
        Paragraph(seller_name, ParagraphStyle('company_name', parent=normal, fontSize=11, spaceAfter=2)),
        Paragraph(f'GSTIN: {seller_gstin}' if seller_gstin else '', ParagraphStyle('detail', parent=small, spaceAfter=2)),
        Paragraph(f'PAN: {business_profile.pan}' if business_profile and business_profile.pan else '', ParagraphStyle('detail', parent=small, spaceAfter=2)),
        Paragraph(seller_addr, ParagraphStyle('address', parent=small, spaceAfter=2)),
    ]
    
    # Add contact information if available
    if business_profile and business_profile.phone:
        seller_cell.append(Paragraph(f'Phone: {business_profile.phone}', ParagraphStyle('contact', parent=small, spaceAfter=1)))
    if business_profile and business_profile.email:
        seller_cell.append(Paragraph(f'Email: {business_profile.email}', ParagraphStyle('contact', parent=small)))
    
    # Enhanced Buyer Information
    buyer_cell = [
        Paragraph('<b>Bill To:</b>', ParagraphStyle('section_title', parent=normal, fontSize=12, textColor=primary_color, spaceAfter=4)),
        Paragraph(buyer.name or '', ParagraphStyle('company_name', parent=normal, fontSize=11, spaceAfter=2)),
        Paragraph(f'GSTIN: {buyer.gstin}' if buyer.gstin else '', ParagraphStyle('detail', parent=small, spaceAfter=2)),
        Paragraph(buyer.address or '', ParagraphStyle('address', parent=small, spaceAfter=2)),
    ]
    
    # Add buyer contact if available
    if buyer.phone:
        buyer_cell.append(Paragraph(f'Phone: {buyer.phone}', ParagraphStyle('contact', parent=small, spaceAfter=1)))
    if buyer.email:
        buyer_cell.append(Paragraph(f'Email: {buyer.email}', ParagraphStyle('contact', parent=small)))
    
    party_tbl = Table([[seller_cell, buyer_cell]], colWidths=[doc.width/2, doc.width/2])
    party_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#f8fafc')),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),  # Left align for consistent positioning
    ]))
    elems.append(party_tbl)
    elems.append(Spacer(1, 12))

    # Professional Invoice Meta Information
    meta_data = [
        [Paragraph(f'<b>Invoice No:</b> {invoice.invoice_number}', ParagraphStyle('meta_label', parent=normal, fontSize=10)),
         Paragraph(f'<b>Date:</b> {invoice.date.strftime("%d/%m/%Y")}', ParagraphStyle('meta_value', parent=normal, fontSize=10))],
        [Paragraph(f'<b>Due Date:</b> {invoice.due_date.strftime("%d/%m/%Y")}' if invoice.due_date else '<b>Due Date:</b> Not specified', 
                  ParagraphStyle('meta_label', parent=normal, fontSize=10)), 
         Paragraph(f'<b>Financial Year:</b> {invoice.financial_year}', ParagraphStyle('meta_value', parent=normal, fontSize=10))]
    ]
    
    # Add GST compliance info if available
    if invoice.reverse_charge or invoice.ecommerce_gstin or invoice.export_type:
        gst_info = []
        if invoice.reverse_charge:
            gst_info.append('🔄 Reverse Charge: Yes')
        if invoice.ecommerce_gstin:
            gst_info.append(f'🛒 E-commerce GSTIN: {invoice.ecommerce_gstin}')
        if invoice.export_type:
            gst_info.append(f'🌍 Export Type: {invoice.export_type}')
        
        if gst_info:
            meta_data.append([Paragraph(' | '.join(gst_info), ParagraphStyle('gst_info', parent=small, textColor=colors.HexColor('#059669'))), 
                            Paragraph('', normal)])
    
    meta_tbl = Table(meta_data, colWidths=[doc.width/2, doc.width/2])
    meta_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),  # Left align for consistent positioning
    ]))
    elems.append(meta_tbl)
    elems.append(Spacer(1, 12))

    # Professional Items Table - Clean and Organized - PERFECT ALIGNMENT
    data = [[
        Paragraph('<b>Description</b>', ParagraphStyle('header', parent=normal, fontSize=10, textColor=colors.white)), 
        Paragraph('<b>HSN/SAC</b>', ParagraphStyle('header', parent=normal, fontSize=10, textColor=colors.white)), 
        Paragraph('<b>Unit</b>', ParagraphStyle('header', parent=normal, fontSize=10, textColor=colors.white)),
        Paragraph('<b>Qty</b>', ParagraphStyle('header', parent=normal, fontSize=10, textColor=colors.white)), 
        Paragraph('<b>Rate</b>', ParagraphStyle('header', parent=normal, fontSize=10, textColor=colors.white)), 
        Paragraph('<b>Discount</b>', ParagraphStyle('header', parent=normal, fontSize=10, textColor=colors.white)),
        Paragraph('<b>Taxable Value</b>', ParagraphStyle('header', parent=normal, fontSize=10, textColor=colors.white)),
        Paragraph('<b>GST %</b>', ParagraphStyle('header', parent=normal, fontSize=10, textColor=colors.white)), 
        Paragraph('<b>Line Total</b>', ParagraphStyle('header', parent=normal, fontSize=10, textColor=colors.white))
    ]]
    
    for it in invoice.items:
        # Calculate line total including tax
        amount = (it.quantity or 0) * (it.rate or 0)
        discount_amount = it.discount_amount or 0
        if it.discount_percent and it.discount_percent > 0:
            discount_amount = (amount * it.discount_percent) / 100
        
        taxable_value = amount - discount_amount
        tax_amount = (taxable_value * (it.gst_rate or 0)) / 100
        line_total = taxable_value + tax_amount
        
        # HSN/SAC code display
        hsn_sac = it.hsn_code or it.sac_code or ''
        
        data.append([
            Paragraph(it.description or '', ParagraphStyle('item_text', parent=small, fontSize=9, wordWrap='LTR', splitLongWords=False)), 
            Paragraph(hsn_sac, ParagraphStyle('item_text', parent=small, fontSize=9, wordWrap='LTR', splitLongWords=False)), 
            Paragraph(it.unit or 'Nos', ParagraphStyle('item_text', parent=small, fontSize=9, wordWrap='LTR', splitLongWords=False)),
            Paragraph(f'{it.quantity:g}', ParagraphStyle('item_number', parent=small, fontSize=9, wordWrap='LTR', splitLongWords=False)), 
            Paragraph(f'Rs.{it.rate:.2f}', ParagraphStyle('item_number', parent=small, fontSize=9, wordWrap='LTR', splitLongWords=False)), 
            Paragraph(f'{it.discount_percent:g}% / Rs.{discount_amount:.2f}' if it.discount_percent or discount_amount else '-', 
                     ParagraphStyle('item_text', parent=small, fontSize=9, wordWrap='LTR', splitLongWords=False)),
            Paragraph(f'Rs.{taxable_value:.2f}', ParagraphStyle('item_number', parent=small, fontSize=9, wordWrap='LTR', splitLongWords=False)),
            Paragraph(f'{it.gst_rate:g}%', ParagraphStyle('item_number', parent=small, fontSize=9, wordWrap='LTR', splitLongWords=False)), 
            Paragraph(f'Rs.{line_total:.2f}', ParagraphStyle('item_number', parent=small, fontSize=9, wordWrap='LTR', splitLongWords=False))
        ])
    
    # MAXIMUM WIDTH column widths to prevent ANY text wrapping - PERFECT ALIGNMENT
    items_tbl = Table(data, colWidths=[
        doc.width*0.25,  # Description - Maximum width
        doc.width*0.15,  # HSN/SAC - Maximum width
        doc.width*0.10,  # Unit - Maximum width
        doc.width*0.10,  # Qty - Maximum width
        doc.width*0.15,  # Rate - Maximum width (for Rs.100000.00)
        doc.width*0.16,  # Discount - Maximum width (for % / Rs.1000.00)
        doc.width*0.16,  # Taxable Value - Maximum width (for Rs.100000.00)
        doc.width*0.10,  # GST % - Maximum width (for 18%)
        doc.width*0.16   # Line Total - Maximum width (for Rs.118000.00)
    ])
    
    # COMPLETELY CLEAN table styling - ABSOLUTELY NO DECORATIVE ELEMENTS - PERFECT ALIGNMENT
    items_tbl.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        
        # Data rows styling
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (3,1), (-1,-1), 'RIGHT'),  # Right align numeric columns
        ('ALIGN', (0,1), (2,-1), 'CENTER'),  # Center align text columns
        
        # ABSOLUTELY NO BORDERS - Pure clean design
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        
        # Alternating row colors for better readability
        ('ROWBACKGROUNDS', (1,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')]),
        
        # PREVENT TEXT WRAPPING - Keep text on single line
        ('WORDWRAP', (0,0), (-1,-1), False),
        
        # PERFECT ALIGNMENT - Consistent positioning
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),  # Left align for consistent positioning
    ]))
    elems.append(items_tbl)
    elems.append(Spacer(1, 12))

    # Professional Totals Section - Clear CGST/SGST Separation
    totals_data = [
        [Paragraph('Subtotal:', ParagraphStyle('total_label', parent=normal, fontSize=11, textColor=colors.HexColor('#374151'))), 
         Paragraph(f'Rs.{invoice.subtotal:.2f}', ParagraphStyle('total_value', parent=normal, fontSize=11, textColor=colors.HexColor('#374151')))]
    ]
    
    # Add discount if applicable
    if invoice.discount and invoice.discount > 0:
        totals_data.append([
            Paragraph('Discount:', ParagraphStyle('total_label', parent=normal, fontSize=11, textColor=colors.HexColor('#dc2626'))), 
            Paragraph(f'Rs.{invoice.discount:.2f}', ParagraphStyle('total_value', parent=normal, fontSize=11, textColor=colors.HexColor('#dc2626')))
        ])
        totals_data.append([
            Paragraph('Taxable Value:', ParagraphStyle('total_label', parent=normal, fontSize=11, textColor=colors.HexColor('#374151'))), 
            Paragraph(f'Rs.{invoice.taxable_value:.2f}', ParagraphStyle('total_value', parent=normal, fontSize=11, textColor=colors.HexColor('#374151')))
        ])
    
    # Clear GST breakdown - CGST and SGST are separate
    if invoice.cgst > 0:
        totals_data.append([
            Paragraph('CGST (9%):', ParagraphStyle('gst_label', parent=normal, fontSize=11, textColor=colors.HexColor('#059669'))), 
            Paragraph(f'Rs.{invoice.cgst:.2f}', ParagraphStyle('gst_value', parent=normal, fontSize=11, textColor=colors.HexColor('#059669')))
        ])
    if invoice.sgst > 0:
        totals_data.append([
            Paragraph('SGST (9%):', ParagraphStyle('gst_label', parent=normal, fontSize=11, textColor=colors.HexColor('#059669'))), 
            Paragraph(f'Rs.{invoice.sgst:.2f}', ParagraphStyle('gst_value', parent=normal, fontSize=11, textColor=colors.HexColor('#059669')))
        ])
    if invoice.igst > 0:
        totals_data.append([
            Paragraph('IGST (18%):', ParagraphStyle('gst_label', parent=normal, fontSize=11, textColor=colors.HexColor('#059669'))), 
            Paragraph(f'Rs.{invoice.igst:.2f}', ParagraphStyle('gst_value', parent=normal, fontSize=11, textColor=colors.HexColor('#059669')))
        ])
    
    # Add round off if applicable
    if invoice.round_off and invoice.round_off != 0:
        totals_data.append([
            Paragraph('Round Off:', ParagraphStyle('total_label', parent=normal, fontSize=11, textColor=colors.HexColor('#6b7280'))), 
            Paragraph(f'Rs.{invoice.round_off:.2f}', ParagraphStyle('total_value', parent=normal, fontSize=11, textColor=colors.HexColor('#6b7280')))
        ])
    
    # Total amount
    totals_data.append([
        Paragraph('Total Amount:', ParagraphStyle('final_total_label', parent=normal, fontSize=14, textColor=primary_color, fontName='Helvetica-Bold')), 
        Paragraph(f'Rs.{invoice.total:.2f}', ParagraphStyle('final_total_value', parent=normal, fontSize=14, textColor=primary_color, fontName='Helvetica-Bold'))
    ])
    
    # Add total in words if available
    if invoice.total_in_words:
        totals_data.append([
            Paragraph('Amount in Words:', ParagraphStyle('words_label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))), 
            Paragraph(f'<i>{invoice.total_in_words}</i>', ParagraphStyle('words_value', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280')))
        ])
    
    totals_tbl = Table(totals_data, colWidths=[doc.width*0.6, doc.width*0.4])
    totals_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),  # Left align for consistent positioning
    ]))
    elems.append(totals_tbl)
    
    # Add business profile information
    if business_profile:
        elems.append(Spacer(1, 12))
        
        # Debug: Print business profile info
        print(f"DEBUG: Business Profile - Bank: {business_profile.bank_name}, IFSC: {business_profile.bank_ifsc}, Terms: {business_profile.default_terms}")
        print(f"DEBUG: Payment Details Count: {len(payment_details) if 'payment_details' in locals() else 'Not created yet'}")
        
        # Payment Details Section - ALWAYS SHOW ALL AVAILABLE INFO
        payment_details = []
        
        # Always show payment details section
        payment_details.append(Paragraph('<b>Payment Details:</b>', ParagraphStyle('section_title', parent=normal, fontSize=12, textColor=primary_color)))
        
        # Show all available bank information - NO BULLET POINTS
        if business_profile.bank_account_name:
            payment_details.append(Paragraph(f'Account Name: {business_profile.bank_account_name}', ParagraphStyle('detail', parent=small, fontSize=9)))
            print(f"DEBUG: Added Account Name: {business_profile.bank_account_name}")
        if business_profile.bank_name:
            payment_details.append(Paragraph(f'Bank: {business_profile.bank_name}', ParagraphStyle('detail', parent=small, fontSize=9)))
            print(f"DEBUG: Added Bank: {business_profile.bank_name}")
        if business_profile.bank_branch:
            payment_details.append(Paragraph(f'Branch: {business_profile.bank_branch}', ParagraphStyle('detail', parent=small, fontSize=9)))
            print(f"DEBUG: Added Branch: {business_profile.bank_branch}")
        if business_profile.bank_account_number:
            payment_details.append(Paragraph(f'Account No: {business_profile.bank_account_number}', ParagraphStyle('detail', parent=small, fontSize=9)))
            print(f"DEBUG: Added Account No: {business_profile.bank_account_number}")
        if business_profile.bank_ifsc:
            payment_details.append(Paragraph(f'IFSC: {business_profile.bank_ifsc}', ParagraphStyle('detail', parent=small, fontSize=9)))
            print(f"DEBUG: Added IFSC: {business_profile.bank_ifsc}")
        if business_profile.upi_id:
            payment_details.append(Paragraph(f'UPI ID: {business_profile.upi_id}', ParagraphStyle('detail', parent=small, fontSize=9)))
            print(f"DEBUG: Added UPI ID: {business_profile.upi_id}")
        
        # Cash Payment Information
        if business_profile.accepts_cash and business_profile.accepts_cash.upper() == 'YES':
            payment_details.append(Paragraph('<b>Cash Payment:</b>', ParagraphStyle('section_title', parent=normal, fontSize=12, textColor=primary_color)))
            if business_profile.cash_note:
                payment_details.append(Paragraph(business_profile.cash_note, ParagraphStyle('detail', parent=small, fontSize=9)))
        
        print(f"DEBUG: Total Payment Details: {len(payment_details)}")
        print(f"DEBUG: Payment Details Content: {[p.text for p in payment_details]}")
        
        # Always show payment details section
        payment_tbl = Table([payment_details], colWidths=[doc.width])
        payment_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elems.append(payment_tbl)
        elems.append(Spacer(1, 8))
        
        # Terms and Conditions from Business Profile
        terms_data = []
        
        # Always show default terms (even if empty, show a placeholder)
        terms_data.append([Paragraph('<b>Default Terms:</b>', ParagraphStyle('section_title', parent=normal, fontSize=12, textColor=primary_color)), 
                        Paragraph(business_profile.default_terms or 'Standard payment terms apply. Please pay within the due date.', ParagraphStyle('terms_text', parent=small, fontSize=9))])
        
        # Show invoice-specific terms if available
        if invoice.terms_and_conditions:
            terms_data.append([Paragraph('<b>Invoice Terms:</b>', ParagraphStyle('section_title', parent=normal, fontSize=12, textColor=primary_color)), 
                            Paragraph(invoice.terms_and_conditions, ParagraphStyle('terms_text', parent=small, fontSize=9))])
        
        # Always show terms section
        if terms_data:
            terms_tbl = Table(terms_data, colWidths=[doc.width*0.3, doc.width*0.7])
            terms_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            elems.append(terms_tbl)
            elems.append(Spacer(1, 8))
    
    # Add signature if available
    if business_profile and business_profile.signature_path and os.path.exists(business_profile.signature_path):
        try:
            from reportlab.platypus import Image
            signature = Image(business_profile.signature_path, width=80, height=40)
            signature_tbl = Table([[Paragraph('<b>Authorized Signatory</b>', small), signature]], colWidths=[doc.width*0.7, doc.width*0.3])
            signature_tbl.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (1,0), (1,-1), 'CENTER'),
            ]))
            elems.append(signature_tbl)
        except:
            pass

    doc.build(elems)
    buffer.seek(0)
    return buffer.getvalue()



