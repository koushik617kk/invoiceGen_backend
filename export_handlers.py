"""
Export handlers for different invoice export types.
This module contains all export-related functions to keep main.py clean.
"""

from datetime import date
from fastapi.responses import Response
from fastapi import HTTPException
import csv
from io import StringIO
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import Invoice, InvoiceItem


async def export_complete_invoices(qry, db):
    """Export complete invoice details"""
    invoices = qry.order_by(Invoice.date.desc()).all()
    
    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Invoice Number', 'Date', 'Customer', 'GSTIN', 'State', 'Subtotal', 
        'CGST', 'SGST', 'IGST', 'Total', 'Status', 'Paid On'
    ])
    
    # Data rows
    for inv in invoices:
        writer.writerow([
            inv.invoice_number,
            inv.date.strftime('%Y-%m-%d') if inv.date else '',
            inv.buyer.name if inv.buyer else '',
            inv.buyer.gstin if inv.buyer else '',
            inv.buyer.state_code if inv.buyer else '',
            f"{inv.subtotal:.2f}" if inv.subtotal else '0.00',
            f"{inv.cgst:.2f}" if inv.cgst else '0.00',
            f"{inv.sgst:.2f}" if inv.sgst else '0.00',
            f"{inv.igst:.2f}" if inv.igst else '0.00',
            f"{inv.total:.2f}" if inv.total else '0.00',
            inv.status or 'UNPAID',
            inv.paid_on.strftime('%Y-%m-%d') if inv.paid_on else ''
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    filename = f"invoices_complete_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


async def export_hsn_wise_invoices(qry, db, user_id):
    """Export HSN code wise detailed invoices with summary"""
    # Get all invoices with their items for the user
    invoices = qry.order_by(Invoice.date.desc()).all()
    
    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write title
    writer.writerow(['HSN CODE WISE INVOICE EXPORT'])
    writer.writerow(['Generated on:', date.today().strftime('%Y-%m-%d')])
    writer.writerow([])  # Empty row
    
    # Group invoices by HSN code
    hsn_groups = {}
    for invoice in invoices:
        for item in invoice.items:
            hsn_code = item.hsn_code or 'N/A'
            if hsn_code not in hsn_groups:
                hsn_groups[hsn_code] = []
            hsn_groups[hsn_code].append({
                'invoice': invoice,
                'item': item
            })
    
    # Sort HSN codes by total turnover
    hsn_totals = {}
    for hsn_code, items in hsn_groups.items():
        total_turnover = sum(item['item'].taxable_value or 0 for item in items)
        hsn_totals[hsn_code] = total_turnover
    
    sorted_hsn_codes = sorted(hsn_totals.keys(), key=lambda x: hsn_totals[x], reverse=True)
    
    # Write detailed invoice data for each HSN code
    for hsn_code in sorted_hsn_codes:
        items = hsn_groups[hsn_code]
        
        # HSN Code Header
        writer.writerow([f'HSN CODE: {hsn_code}'])
        writer.writerow(['=' * 50])
        
        # Detailed invoice header
        writer.writerow([
            'Invoice Number', 'Invoice Date', 'Customer Name', 'Customer GSTIN',
            'Item Description', 'Quantity', 'Rate', 'Taxable Value', 
            'GST Rate (%)', 'GST Amount', 'Line Total'
        ])
        
        # Detailed invoice data
        for item_data in items:
            invoice = item_data['invoice']
            item = item_data['item']
            
            gst_amount = (item.taxable_value or 0) * (item.gst_rate or 0) / 100
            line_total = (item.taxable_value or 0) + gst_amount
            
            writer.writerow([
                invoice.invoice_number,
                invoice.date.strftime('%Y-%m-%d') if invoice.date else '',
                invoice.buyer.name if invoice.buyer else '',
                invoice.buyer.gstin if invoice.buyer else '',
                item.description or '',
                f"{item.quantity or 0}",
                f"{item.rate or 0:.2f}",
                f"{item.taxable_value or 0:.2f}",
                f"{item.gst_rate or 0:.1f}",
                f"{gst_amount:.2f}",
                f"{line_total:.2f}"
            ])
        
        writer.writerow([])  # Empty row after each HSN code
    
    # Summary Section
    writer.writerow(['SUMMARY BY HSN CODE'])
    writer.writerow(['=' * 50])
    writer.writerow([
        'HSN Code', 'Total Taxable Value', 'Total GST Amount', 'Total Amount',
        'Item Count', 'Invoice Count', 'Average Item Value'
    ])
    
    # Calculate summary for each HSN code
    for hsn_code in sorted_hsn_codes:
        items = hsn_groups[hsn_code]
        
        total_taxable_value = sum(item['item'].taxable_value or 0 for item in items)
        total_gst = sum((item['item'].taxable_value or 0) * (item['item'].gst_rate or 0) / 100 for item in items)
        total_amount = total_taxable_value + total_gst
        item_count = len(items)
        invoice_count = len(set(item['invoice'].id for item in items))
        avg_value = total_taxable_value / item_count if item_count > 0 else 0
        
        writer.writerow([
            hsn_code,
            f"{total_taxable_value:.2f}",
            f"{total_gst:.2f}",
            f"{total_amount:.2f}",
            item_count,
            invoice_count,
            f"{avg_value:.2f}"
        ])
    
    # Grand Total
    grand_taxable = sum(hsn_totals.values())
    grand_gst = sum(sum((item['item'].taxable_value or 0) * (item['item'].gst_rate or 0) / 100 for item in items) for items in hsn_groups.values())
    grand_total = grand_taxable + grand_gst
    total_items = sum(len(items) for items in hsn_groups.values())
    total_invoices = len(set(item['invoice'].id for items in hsn_groups.values() for item in items))
    
    writer.writerow([])
    writer.writerow(['GRAND TOTAL', f"{grand_taxable:.2f}", f"{grand_gst:.2f}", f"{grand_total:.2f}", total_items, total_invoices, f"{grand_taxable/total_items:.2f}" if total_items > 0 else "0.00"])
    
    csv_content = output.getvalue()
    output.close()
    
    filename = f"invoices_hsn_wise_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


async def export_gst_slab_wise_invoices(qry, db, user_id):
    """Export GST slab wise turnover summary"""
    # Query to get GST slab wise turnover
    gst_data = db.query(
        InvoiceItem.gst_rate,
        func.sum(InvoiceItem.taxable_value).label('total_taxable_value'),
        func.sum(InvoiceItem.taxable_value * InvoiceItem.gst_rate / 100).label('total_gst'),
        func.sum(InvoiceItem.taxable_value + (InvoiceItem.taxable_value * InvoiceItem.gst_rate / 100)).label('total_amount'),
        func.count(InvoiceItem.id).label('item_count'),
        func.count(func.distinct(InvoiceItem.invoice_id)).label('invoice_count')
    ).join(Invoice, InvoiceItem.invoice_id == Invoice.id).filter(
        Invoice.user_id == user_id
    ).group_by(InvoiceItem.gst_rate).order_by(InvoiceItem.gst_rate).all()
    
    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'GST Rate (%)', 'Taxable Value', 'GST Amount', 'Total Amount', 
        'Item Count', 'Invoice Count', 'Average Item Value'
    ])
    
    # Data rows
    for row in gst_data:
        avg_value = row.total_taxable_value / row.item_count if row.item_count > 0 else 0
        writer.writerow([
            f"{row.gst_rate:.1f}%" if row.gst_rate else "0.0%",
            f"{row.total_taxable_value:.2f}",
            f"{row.total_gst:.2f}",
            f"{row.total_amount:.2f}",
            row.item_count,
            row.invoice_count,
            f"{avg_value:.2f}"
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    filename = f"invoices_gst_slab_wise_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
