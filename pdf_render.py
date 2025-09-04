from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
import os

def render_invoice_pdf(invoice, business_profile=None, template=None) -> bytes:
    """
    Generate PDF invoice using default design.
    Template support removed for simplicity.
    """
    print(f"DEBUG: render_invoice_pdf called - using default PDF generation")
    return render_default_pdf(invoice, business_profile)

def render_default_pdf(invoice, business_profile=None) -> bytes:
    """
    Default PDF generation using ReportLab.
    Clean, professional invoice design with perfect alignment.
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
            logo = Image(business_profile.logo_path, width=80, height=40)
            company_header.append(logo)
        except:
            pass
    
    company_header.append(Paragraph(business_profile.business_name if business_profile and business_profile.business_name else 'invoiceGen', 
                                   ParagraphStyle('company_name', parent=h1, fontSize=24, textColor=primary_color, spaceAfter=6)))
    
    # Professional header layout - PERFECT ALIGNMENT
    header_tbl = Table([
        [company_header, 
         [Paragraph('Tax Invoice', ParagraphStyle('invoice_title', parent=h4, fontSize=18, textColor=primary_color, alignment=2)),
          Paragraph(f'Place of Supply: {invoice.place_of_supply or "Not specified"}', 
                   ParagraphStyle('subtitle', parent=normal, fontSize=10, textColor=colors.HexColor('#6b7280'), alignment=2))]
        ]
    ], colWidths=[doc.width*0.65, doc.width*0.35])
    
    header_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),  # FIXED: Add left padding
        ('RIGHTPADDING', (0,0), (-1,-1), 8), # FIXED: Add right padding
    ]))
    elems.append(header_tbl)
    elems.append(Spacer(1, 6))
    
    # FIXED: GST Compliance Header - Consistent with other sections
    if business_profile:
        gst_info = []
        if business_profile.pan:
            gst_info.append(f"PAN: {business_profile.pan}")
        if invoice.financial_year:
            gst_info.append(f"Financial Year: {invoice.financial_year}")
        
        if gst_info:
            # Use same column structure as header for perfect alignment
            gst_header_tbl = Table([gst_info, []], colWidths=[doc.width*0.65, doc.width*0.35])
            gst_header_tbl.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,0), 'LEFT'),  # PAN info left-aligned like other content
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#374151')),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
                ('LEFTPADDING', (0,0), (-1,-1), 8),  # FIXED: Match header padding
                ('RIGHTPADDING', (0,0), (-1,-1), 8), # FIXED: Match header padding
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            elems.append(gst_header_tbl)
            elems.append(Spacer(1, 6))

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
    
    party_tbl = Table([[seller_cell, buyer_cell]], colWidths=[doc.width*0.65, doc.width*0.35])
    party_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#f8fafc')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),  # FIXED: Consistent with header
        ('RIGHTPADDING', (0,0), (-1,-1), 8), # FIXED: Consistent with header
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    elems.append(party_tbl)
    elems.append(Spacer(1, 8))

    # Professional Invoice Meta Information
    meta_data = [
        [Paragraph(f'<b>Invoice No:</b> {invoice.invoice_number}', ParagraphStyle('meta_label', parent=normal, fontSize=10)),
         Paragraph(f'<b>Date:</b> {invoice.date.strftime("%d/%m/%Y")}', ParagraphStyle('meta_value', parent=normal, fontSize=10))],
        [Paragraph(f'<b>Due Date:</b> {invoice.due_date.strftime("%d/%m/%Y")}' if invoice.due_date else '<b>Due Date:</b> Not specified', 
                  ParagraphStyle('meta_label', parent=normal, fontSize=10)), 
         Paragraph(f'<b>Financial Year:</b> {invoice.financial_year}', ParagraphStyle('meta_value', parent=normal, fontSize=10))]
    ]
    
    meta_tbl = Table(meta_data, colWidths=[doc.width*0.65, doc.width*0.35])
    meta_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),  # FIXED: Consistent with other sections
        ('RIGHTPADDING', (0,0), (-1,-1), 8), # FIXED: Consistent with other sections
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    elems.append(meta_tbl)
    elems.append(Spacer(1, 8))

    # FIXED: Professional Items Table - PERFECT ALIGNMENT with other sections
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
    
    # FIXED: PERFECT ALIGNMENT - Items table uses EXACT same total width as other tables (100%)
    items_tbl = Table(data, colWidths=[
        doc.width*0.19,  # Description (reduced from 0.20)
        doc.width*0.12,  # HSN/SAC
        doc.width*0.08,  # Unit
        doc.width*0.08,  # Qty
        doc.width*0.12,  # Rate
        doc.width*0.12,  # Discount
        doc.width*0.12,  # Taxable Value
        doc.width*0.08,  # GST %
        doc.width*0.11   # Line Total (reduced from 0.12)
    ])
    
    # Clean table styling with perfect alignment
    items_tbl.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        
        # Data rows styling
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (3,1), (-1,-1), 'RIGHT'),  # Right align numeric columns
        ('ALIGN', (0,1), (2,-1), 'CENTER'),  # Center align text columns
        
        # FIXED: Consistent padding with other sections
        ('LEFTPADDING', (0,0), (-1,-1), 8),  # FIXED: Match other sections
        ('RIGHTPADDING', (0,0), (-1,-1), 8), # FIXED: Match other sections
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        
        # Alternating row colors for better readability
        ('ROWBACKGROUNDS', (1,1), (-1,-1), [colors.white, colors.HexColor('#f9fafb')]),
        
        # Prevent text wrapping
        ('WORDWRAP', (0,0), (-1,-1), False),
        
        # Perfect alignment
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    elems.append(items_tbl)
    elems.append(Spacer(1, 8))

    # Professional Totals Section
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
    
    # Clear GST breakdown
    if invoice.cgst > 0:
        totals_data.append([
            Paragraph('CGST (9%):', ParagraphStyle('gst_label', parent=normal, fontSize=11, textColor=colors.HexColor('#059669'))), 
            Paragraph(f'Rs.{invoice.cgst:.2f}', ParagraphStyle('gst_value', parent=normal, fontSize=11, textColor=colors.HexColor('#059669')))
        ])
    if invoice.sgst > 0:
        totals_data.append([
            Paragraph('SGST (9%):', ParagraphStyle('gst_label', parent=normal, fontSize=11, textColor=colors.HexColor('#059669'))), 
            Paragraph(f'Rs.{invoice.sgst:.2f}', ParagraphStyle('total_value', parent=normal, fontSize=11, textColor=colors.HexColor('#059669')))
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
    
    # FIXED: Perfect alignment with header and items table
    totals_tbl = Table(totals_data, colWidths=[doc.width*0.65, doc.width*0.35])
    totals_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),  # FIXED: Match other sections
        ('RIGHTPADDING', (0,0), (-1,-1), 8), # FIXED: Match other sections
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    elems.append(totals_tbl)
    
    # Add business profile information
    if business_profile:
        elems.append(Spacer(1, 8))
        
        # ENHANCED: Professional Payment Details Section
        payment_data = []
        
        # Create a clean, organized payment details table
        if business_profile.bank_account_name or business_profile.bank_name or business_profile.bank_account_number or business_profile.bank_ifsc or business_profile.upi_id:
            payment_data.append([
                Paragraph('<b>Payment Details</b>', ParagraphStyle('section_title', parent=normal, fontSize=12, textColor=primary_color)),
                Paragraph('', normal)  # Empty cell for alignment
            ])
            
            # Bank details in a clean format
            if business_profile.bank_account_name:
                payment_data.append([
                    Paragraph('Account Name:', ParagraphStyle('label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))),
                    Paragraph(business_profile.bank_account_name, ParagraphStyle('value', parent=small, fontSize=9, textColor=colors.HexColor('#374151')))
                ])
            
        if business_profile.bank_name:
                payment_data.append([
                    Paragraph('Bank Name:', ParagraphStyle('label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))),
                    Paragraph(business_profile.bank_name, ParagraphStyle('value', parent=small, fontSize=9, textColor=colors.HexColor('#374151')))
                ])
            
        if business_profile.bank_branch:
                payment_data.append([
                    Paragraph('Branch:', ParagraphStyle('label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))),
                    Paragraph(business_profile.bank_branch, ParagraphStyle('value', parent=small, fontSize=9, textColor=colors.HexColor('#374151')))
                ])
        
        if business_profile.bank_account_number:
                payment_data.append([
                    Paragraph('Account Number:', ParagraphStyle('label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))),
                    Paragraph(business_profile.bank_account_number, ParagraphStyle('value', parent=small, fontSize=9, textColor=colors.HexColor('#374151')))
                ])
            
        if business_profile.bank_ifsc:
                payment_data.append([
                    Paragraph('IFSC Code:', ParagraphStyle('label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))),
                    Paragraph(business_profile.bank_ifsc, ParagraphStyle('value', parent=small, fontSize=9, textColor=colors.HexColor('#374151')))
                ])
            
        if business_profile.upi_id:
                payment_data.append([
                    Paragraph('UPI ID:', ParagraphStyle('label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))),
                    Paragraph(business_profile.upi_id, ParagraphStyle('value', parent=small, fontSize=9, textColor=colors.HexColor('#374151')))
                ])
        
        # Cash Payment Information
        if business_profile.accepts_cash and business_profile.accepts_cash.upper() == 'YES':
            if business_profile.cash_note:
                    payment_data.append([
                        Paragraph('Cash Payment:', ParagraphStyle('label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))),
                        Paragraph(business_profile.cash_note, ParagraphStyle('value', parent=small, fontSize=9, textColor=colors.HexColor('#374151')))
                    ])
        
        # Create a clean, professional payment table only if there's data
        if payment_data:
            payment_tbl = Table(payment_data, colWidths=[doc.width*0.3, doc.width*0.7])
        payment_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f1f5f9')),  # Header background
                    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),  # Data background
                    ('LEFTPADDING', (0,0), (-1,-1), 12),  # More padding for better spacing
                    ('RIGHTPADDING', (0,0), (-1,-1), 12),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ALIGN', (0,0), (0,-1), 'LEFT'),  # Labels left-aligned
                    ('ALIGN', (1,0), (1,-1), 'LEFT'),  # Values left-aligned
                    ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),  # Header bold
                    ('FONTSIZE', (0,0), (0,0), 12),  # Header larger
                    ('TEXTCOLOR', (0,0), (0,0), primary_color),  # Header color
                    # Add subtle borders for better structure
                    ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#e5e7eb')),
                    ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#e5e7eb')),
        ]))
        elems.append(payment_tbl)
        elems.append(Spacer(1, 8))
        
        # ENHANCED: Professional Terms and Conditions Section
        terms_data = []
        
        # Always show default terms with better styling
        default_terms = business_profile.default_terms or 'Standard payment terms apply. Please pay within the due date.'
        terms_data.append([
            Paragraph('<b>Terms & Conditions</b>', ParagraphStyle('section_title', parent=normal, fontSize=12, textColor=primary_color)),
            Paragraph('', normal)  # Empty cell for alignment
        ])
        terms_data.append([
            Paragraph('Default Terms:', ParagraphStyle('label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))),
            Paragraph(default_terms, ParagraphStyle('terms_text', parent=small, fontSize=9, textColor=colors.HexColor('#374151')))
        ])
        
        # Show invoice-specific terms if available
        if invoice.terms_and_conditions:
            terms_data.append([
                Paragraph('Invoice Terms:', ParagraphStyle('label', parent=small, fontSize=9, textColor=colors.HexColor('#6b7280'))),
                Paragraph(invoice.terms_and_conditions, ParagraphStyle('terms_text', parent=small, fontSize=9, textColor=colors.HexColor('#374151')))
            ])
        
        # Always show terms section with professional styling
        if terms_data:
            terms_tbl = Table(terms_data, colWidths=[doc.width*0.3, doc.width*0.7])
            terms_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f1f5f9')),  # Header background
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),  # Data background
                ('LEFTPADDING', (0,0), (-1,-1), 12),  # More padding for better spacing
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (0,0), (0,-1), 'LEFT'),  # Labels left-aligned
                ('ALIGN', (1,0), (1,-1), 'LEFT'),  # Values left-aligned
                ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),  # Header bold
                ('FONTSIZE', (0,0), (0,0), 12),  # Header larger
                ('TEXTCOLOR', (0,0), (0,0), primary_color),  # Header color
                # Add subtle borders for better structure
                ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#e5e7eb')),
                ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#e5e7eb')),
            ]))
            elems.append(terms_tbl)
            elems.append(Spacer(1, 6))
    
    # Add signature if available
    if business_profile and business_profile.signature_path and os.path.exists(business_profile.signature_path):
        try:
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