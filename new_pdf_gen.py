def render_default_pdf(invoice, business_profile=None) -> bytes:
    """
    Professional GST-compliant Invoice PDF with WOW design.
    """
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from io import BytesIO
    import os

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
    normal = styles['Normal']
    small = ParagraphStyle('small', parent=normal, fontSize=9)
    h1 = ParagraphStyle('h1', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1e3a8a'))
    h2 = ParagraphStyle('h2', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1e3a8a'))

    elems = []

    # --- HEADER ---
    header_content = []
    if business_profile and business_profile.logo_path and os.path.exists(business_profile.logo_path):
        try:
            logo = Image(business_profile.logo_path, width=80, height=40)
            header_content.append(logo)
        except:
            pass

    company_name = business_profile.business_name if business_profile and business_profile.business_name else 'Company Name'
    header_content.append(Paragraph(company_name, h1))
    if business_profile and business_profile.gstin:
        header_content.append(Paragraph(f"GSTIN: {business_profile.gstin}", normal))
    if business_profile and business_profile.pan:
        header_content.append(Paragraph(f"PAN: {business_profile.pan}", normal))

    header_tbl = Table([
        [header_content, Paragraph('<b>Tax Invoice</b>', h2)]
    ], colWidths=[doc.width*0.65, doc.width*0.35])
    header_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elems.append(header_tbl)
    elems.append(Spacer(1, 12))

    # --- SELLER & BUYER ---
    seller_cell = [Paragraph('<b>From</b>', h2),
                   Paragraph(company_name, normal),
                   Paragraph(business_profile.address or '', small),
                   Paragraph(f"Phone: {business_profile.phone}" if getattr(business_profile, 'phone', None) else '', small),
                   Paragraph(f"Email: {business_profile.email}" if getattr(business_profile, 'email', None) else '', small)]

    buyer = invoice.buyer
    buyer_cell = [Paragraph('<b>Bill To</b>', h2),
                  Paragraph(buyer.name or '', normal),
                  Paragraph(buyer.address or '', small),
                  Paragraph(f"GSTIN: {buyer.gstin}" if buyer.gstin else '', small),
                  Paragraph(f"Phone: {buyer.phone}" if buyer.phone else '', small),
                  Paragraph(f"Email: {buyer.email}" if buyer.email else '', small)]

    party_tbl = Table([[seller_cell, buyer_cell]], colWidths=[doc.width/2, doc.width/2])
    party_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#d1d5db')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elems.append(party_tbl)
    elems.append(Spacer(1, 12))

    # --- INVOICE META ---
    meta_data = [
        [Paragraph(f"Invoice No: <b>{invoice.invoice_number}</b>", normal),
         Paragraph(f"Date: <b>{invoice.date.strftime('%d/%m/%Y')}</b>", normal)],
        [Paragraph(f"Due Date: <b>{invoice.due_date.strftime('%d/%m/%Y') if invoice.due_date else 'N/A'}</b>", normal),
         Paragraph(f"Place of Supply: <b>{invoice.place_of_supply or 'N/A'}</b>", normal)]
    ]
    meta_tbl = Table(meta_data, colWidths=[doc.width/2, doc.width/2])
    meta_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#d1d5db')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elems.append(meta_tbl)
    elems.append(Spacer(1, 12))

    # --- ITEMIZED TABLE ---
    data = [[Paragraph('<b>Description</b>', normal),
             Paragraph('<b>HSN/SAC</b>', normal),
             Paragraph('<b>Unit</b>', normal),
             Paragraph('<b>Qty</b>', normal),
             Paragraph('<b>Rate</b>', normal),
             Paragraph('<b>Discount</b>', normal),
             Paragraph('<b>Taxable Value</b>', normal),
             Paragraph('<b>GST %</b>', normal),
             Paragraph('<b>Line Total</b>', normal)]]

    for it in invoice.items:
        amount = (it.quantity or 0) * (it.rate or 0)
        discount_amount = it.discount_amount or 0
        if it.discount_percent:
            discount_amount = (amount * it.discount_percent) / 100
        taxable_value = amount - discount_amount
        tax_amount = (taxable_value * (it.gst_rate or 0)) / 100
        line_total = taxable_value + tax_amount

        data.append([
            Paragraph(it.description or '', small),
            Paragraph(it.hsn_code or it.sac_code or '', small),
            Paragraph(it.unit or 'Nos', small),
            Paragraph(f"{it.quantity:g}", small),
            Paragraph(f"{it.rate:.2f}", small),
            Paragraph(f"{discount_amount:.2f}", small),
            Paragraph(f"{taxable_value:.2f}", small),
            Paragraph(f"{it.gst_rate:g}%", small),
            Paragraph(f"{line_total:.2f}", small)
        ])

    items_tbl = Table(data, colWidths=[doc.width*0.22, doc.width*0.1, doc.width*0.08, doc.width*0.08,
                                       doc.width*0.12, doc.width*0.12, doc.width*0.12, doc.width*0.08, doc.width*0.12])
    items_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#d1d5db')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    elems.append(items_tbl)
    elems.append(Spacer(1, 12))

    # --- TOTALS ---
    totals_data = []
    totals_data.append(["Subtotal", f"{invoice.subtotal:.2f}"])
    if invoice.cgst: totals_data.append(["CGST", f"{invoice.cgst:.2f}"])
    if invoice.sgst: totals_data.append(["SGST", f"{invoice.sgst:.2f}"])
    if invoice.igst: totals_data.append(["IGST", f"{invoice.igst:.2f}"])
    if invoice.round_off: totals_data.append(["Round Off", f"{invoice.round_off:.2f}"])
    totals_data.append(["<b>Total Amount</b>", f"<b>{invoice.total:.2f}</b>"])
    if invoice.total_in_words:
        totals_data.append(["Amount in Words", f"{invoice.total_in_words}"])

    totals_tbl = Table(totals_data, colWidths=[doc.width*0.6, doc.width*0.4])
    totals_tbl.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#d1d5db')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elems.append(totals_tbl)
    elems.append(Spacer(1, 12))

    # --- PAYMENT DETAILS ---
    if business_profile:
        pay_details = []
        pay_details.append(Paragraph('<b>Payment Details</b>', h2))
        if business_profile.bank_account_name:
            pay_details.append(Paragraph(f"Account Name: {business_profile.bank_account_name}", small))
        if business_profile.bank_name:
            pay_details.append(Paragraph(f"Bank: {business_profile.bank_name}", small))
        if business_profile.bank_branch:
            pay_details.append(Paragraph(f"Branch: {business_profile.bank_branch}", small))
        if business_profile.bank_account_number:
            pay_details.append(Paragraph(f"Account No: {business_profile.bank_account_number}", small))
        if business_profile.bank_ifsc:
            pay_details.append(Paragraph(f"IFSC: {business_profile.bank_ifsc}", small))
        if business_profile.upi_id:
            pay_details.append(Paragraph(f"UPI ID: {business_profile.upi_id}", small))

        pay_tbl = Table([pay_details], colWidths=[doc.width])
        pay_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#d1d5db')),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        elems.append(pay_tbl)
        elems.append(Spacer(1, 12))

    # --- TERMS & CONDITIONS ---
    terms_data = []
    terms_data.append([Paragraph('<b>Terms & Conditions</b>', h2), Paragraph(business_profile.default_terms or 'Standard payment terms apply.', small)])
    if invoice.terms_and_conditions:
        terms_data.append([Paragraph('<b>Invoice Terms</b>', h2), Paragraph(invoice.terms_and_conditions, small)])

    terms_tbl = Table(terms_data, colWidths=[doc.width*0.3, doc.width*0.7])
    terms_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#d1d5db')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elems.append(terms_tbl)
    elems.append(Spacer(1, 12))

    # --- SIGNATURE ---
    if business_profile and business_profile.signature_path and os.path.exists(business_profile.signature_path):
        try:
            sign = Image(business_profile.signature_path, width=80, height=40)
            sign_tbl = Table([[Paragraph('<b>Authorized Signatory</b>', small), sign]], colWidths=[doc.width*0.7, doc.width*0.3])
            sign_tbl.setStyle(TableStyle([
                ('ALIGN', (1,0), (1,-1), 'CENTER')
            ]))
            elems.append(sign_tbl)
        except:
            pass

    # Build PDF
    doc.build(elems)
    buffer.seek(0)
    return buffer.getvalue()
