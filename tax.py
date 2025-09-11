from typing import Optional, Tuple


def extract_state_code(gstin: Optional[str]) -> Optional[str]:
    if not gstin or len(gstin) < 2:
        return None
    return gstin[:2]


def is_intrastate(seller_state: Optional[str], buyer_state: Optional[str]) -> bool:
    if not seller_state or not buyer_state:
        return True
    return seller_state == buyer_state


def compute_totals(items, seller_state: Optional[str], buyer_state: Optional[str]):
    subtotal = 0.0
    taxable_value = 0.0
    cgst = 0.0
    sgst = 0.0
    igst = 0.0
    
    for item in items:
        # Calculate line amount (quantity * rate)
        line_amount = round(item.quantity * item.rate, 2)
        item.amount = line_amount
        
        # Calculate discount
        discount_amount = 0.0
        if item.discount_percent and item.discount_percent > 0:
            discount_amount = round(line_amount * (item.discount_percent / 100.0), 2)
        elif item.discount_amount and item.discount_amount > 0:
            discount_amount = item.discount_amount
        
        # Calculate taxable value (after discount)
        item_taxable_value = round(line_amount - discount_amount, 2)
        item.taxable_value = item_taxable_value
        
        # Calculate tax on taxable value
        tax_rate = item.gst_rate or 0.0
        tax_amount = round(item_taxable_value * (tax_rate / 100.0), 2)
        item.tax_amount = tax_amount
        
        # Calculate line total (taxable value + tax)
        item.line_total = round(item_taxable_value + tax_amount, 2)
        
        # Add to totals
        subtotal += item.line_total  # Subtotal is now sum of line totals
        taxable_value += item_taxable_value
        
        # Split tax between CGST/SGST or IGST
        if is_intrastate(seller_state, buyer_state):
            cgst += tax_amount / 2
            sgst += tax_amount / 2
        else:
            igst += tax_amount
    
    total = round(subtotal, 2)  # Total is same as subtotal since subtotal already includes GST
    return round(subtotal, 2), round(taxable_value, 2), round(cgst, 2), round(sgst, 2), round(igst, 2), total
