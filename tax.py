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
    cgst = 0.0
    sgst = 0.0
    igst = 0.0
    for item in items:
        line_amount = round(item.quantity * item.rate, 2)
        item.amount = line_amount
        tax_rate = item.gst_rate or 0.0
        tax_amount = round(line_amount * (tax_rate / 100.0), 2)
        item.tax_amount = tax_amount
        if is_intrastate(seller_state, buyer_state):
            cgst += tax_amount / 2
            sgst += tax_amount / 2
        else:
            igst += tax_amount
        subtotal += line_amount
    total = round(subtotal + cgst + sgst + igst, 2)
    return round(subtotal, 2), round(cgst, 2), round(sgst, 2), round(igst, 2), total
