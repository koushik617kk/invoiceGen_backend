from datetime import date, datetime, timedelta
from typing import List
import hashlib
import secrets

from fastapi import FastAPI, Depends, HTTPException, Query, Request, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

from database import Base, engine, get_db, run_startup_migrations
from models import User, BusinessProfile, Customer, Invoice, InvoiceItem, Payment, InvoiceTemplate, LibraryItem, ServiceTemplate, MasterService, HSNCode
from schemas import (
    UserOut,
    BusinessProfileIn,
    BusinessProfileOut,
    CustomerIn,
    CustomerOut,
    InvoiceCreate,
    InvoiceOut,
    PaymentIn,
    PaymentOut,
    InvoiceTemplateCreate,
    InvoiceTemplateUpdate,
    InvoiceTemplateOut,
    LibraryItemIn,
    LibraryItemOut,
    ServiceTemplateIn,
    ServiceTemplateOut,
    ServiceTemplateUpdate,
    MasterServiceOut,
    MasterServiceSearch,
    BusinessProfileCreate,
    UserOnboardingUpdate,
)
from security_cognito import get_current_user
from tax import extract_state_code, compute_totals
from hsn_service import suggest_hsn
from fastapi.responses import StreamingResponse
from pdf_render import render_invoice_pdf
from urllib.parse import quote


Base.metadata.create_all(bind=engine)
run_startup_migrations()

app = FastAPI(title="invoiceGen Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://192.168.29.125:5173", "http://192.168.0.8:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/auth/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/business", response_model=BusinessProfileOut)
async def get_business(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not bp:
        bp = BusinessProfile(user_id=current_user.id)
        db.add(bp)
        db.commit()
        db.refresh(bp)
    return bp


@app.put("/business", response_model=BusinessProfileOut)
async def update_business(body: BusinessProfileIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not bp:
        bp = BusinessProfile(user_id=current_user.id)
        db.add(bp)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(bp, k, v)
    db.commit()
    db.refresh(bp)
    return bp


@app.post("/customers", response_model=CustomerOut)
async def create_customer(body: CustomerIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cust = Customer(user_id=current_user.id, **body.model_dump())
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return cust


@app.get("/customers", response_model=List[CustomerOut])
async def list_customers(q: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    qry = db.query(Customer).filter(Customer.user_id == current_user.id)
    if q:
        like = f"%{q}%"
        qry = qry.filter(Customer.name.ilike(like))
    return qry.order_by(Customer.name).all()


@app.get("/customers/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cust = db.query(Customer).filter(Customer.user_id == current_user.id, Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    return cust


@app.put("/customers/{customer_id}", response_model=CustomerOut)
async def update_customer(customer_id: int, body: CustomerIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cust = db.query(Customer).filter(Customer.user_id == current_user.id, Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(cust, k, v)
    db.commit()
    db.refresh(cust)
    return cust


@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cust = db.query(Customer).filter(Customer.user_id == current_user.id, Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(cust)
    db.commit()
    return {"ok": True}


def next_invoice_number(db: Session, user_id: int) -> str:
    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).first()
    if not bp:
        bp = BusinessProfile(user_id=user_id)
        db.add(bp)
        db.commit()
        db.refresh(bp)
    seq = bp.next_invoice_seq or 1
    inv_no = f"INV-{date.today().year}-{seq:06d}"
    bp.next_invoice_seq = seq + 1
    db.commit()
    return inv_no


@app.post("/invoices", response_model=InvoiceOut)
async def create_invoice(body: InvoiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    buyer = db.query(Customer).filter(Customer.user_id == current_user.id, Customer.id == body.buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    # Validate template if provided
    template = None
    if body.template_id:
        template = db.query(InvoiceTemplate).filter(
            InvoiceTemplate.id == body.template_id,
            InvoiceTemplate.user_id == current_user.id
        ).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not bp:
        bp = BusinessProfile(user_id=current_user.id)
        db.add(bp)
        db.commit()
        db.refresh(bp)
    seller_state = bp.state_code or extract_state_code(bp.gstin)
    buyer_state = buyer.state_code or extract_state_code(buyer.gstin)

    # Parse date strings to date objects
    invoice_date = date.today()
    if body.date:
        try:
            invoice_date = datetime.strptime(body.date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid invoice date format. Use YYYY-MM-DD")
    
    due_date_obj = None
    if body.due_date:
        try:
            due_date_obj = datetime.strptime(body.due_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due date format. Use YYYY-MM-DD")

    # Determine financial year based on invoice date
    def get_financial_year(inv_date: date) -> str:
        if inv_date.month >= 4:  # April onwards
            return f"{inv_date.year}-{inv_date.year + 1}"
        else:  # January to March
            return f"{inv_date.year - 1}-{inv_date.year}"
    
    financial_year = get_financial_year(invoice_date)

    invoice = Invoice(
        user_id=current_user.id,
        invoice_number=next_invoice_number(db, current_user.id),
        financial_year=financial_year,  # Set the financial year
        date=invoice_date,
        due_date=due_date_obj,
        seller_gstin=bp.gstin,
        seller_state_code=seller_state,
        seller_pan=bp.pan,  # Add seller PAN
        buyer_id=buyer.id,
        place_of_supply=buyer.state_code,  # Set place of supply from buyer state
        place_of_supply_code=buyer.state_code,  # Set place of supply code
        reverse_charge=body.reverse_charge or False,  # Add reverse charge
        ecommerce_gstin=body.ecommerce_gstin,  # Add e-commerce GSTIN
        export_type=body.export_type,  # Add export type
        template_id=template.id if template else None,  # Set template ID if template was selected
        terms_and_conditions=body.terms_and_conditions,  # Add terms and conditions
        notes=body.notes,  # Add notes
        status="UNPAID",
    )
    for it in body.items:
        # Calculate item amounts
        amount = it.quantity * it.rate
        discount_amount = it.discount_amount or 0
        if it.discount_percent and it.discount_percent > 0:
            discount_amount = (amount * it.discount_percent) / 100
        
        taxable_value = amount - discount_amount
        
        invoice.items.append(InvoiceItem(
            description=it.description,
            hsn_code=it.hsn_code,
            sac_code=it.sac_code,  # Add SAC code
            quantity=it.quantity,
            unit=it.unit or 'Nos',  # Add unit
            rate=it.rate,
            discount_percent=it.discount_percent or 0,  # Add discount percentage
            discount_amount=discount_amount,  # Add discount amount
            taxable_value=taxable_value,  # Add taxable value
            gst_rate=it.gst_rate,
            # GST amounts will be calculated by compute_totals function
        ))

    subtotal, cgst, sgst, igst, total = compute_totals(invoice.items, seller_state, buyer_state)
    invoice.subtotal = subtotal
    invoice.cgst = cgst
    invoice.sgst = sgst
    invoice.igst = igst
    invoice.total = total

    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@app.get("/invoices", response_model=List[InvoiceOut])
async def list_invoices(
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    customer_id: int | None = Query(default=None),
    sort_by: str | None = Query(default="date"),  # date | total | number
    sort_dir: str | None = Query(default="desc"),  # asc | desc
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Query invoices with template information
    qry = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    
    if status:
        qry = qry.filter(Invoice.status == status.upper())
    if date_from:
        qry = qry.filter(Invoice.date >= date_from)
    if date_to:
        qry = qry.filter(Invoice.date <= date_to)
    if customer_id:
        qry = qry.filter(Invoice.buyer_id == customer_id)
    if q:
        like = f"%{q}%"
        qry = qry.join(Customer).filter((Invoice.invoice_number.ilike(like)) | (Customer.name.ilike(like)))
    
    # Sorting
    if sort_by == "total":
        order_col = Invoice.total
    elif sort_by == "number":
        order_col = Invoice.invoice_number
    else:
        order_col = Invoice.date
    if (sort_dir or "").lower() == "asc":
        qry = qry.order_by(order_col.asc())
    else:
        qry = qry.order_by(order_col.desc())
    
    # Execute query
    invoices = qry.all()
    
    # Add template names to invoices
    for invoice in invoices:
        if invoice.template_id:
            template = db.query(InvoiceTemplate).filter(InvoiceTemplate.id == invoice.template_id).first()
            if template:
                invoice.template_name = template.name
    
    # Debug logging
    print(f"DEBUG: Found {len(invoices)} invoices for user {current_user.id}")
    for inv in invoices[:3]:  # Log first 3 invoices
        print(f"DEBUG: Invoice {inv.id}: {inv.invoice_number} - {inv.date} - Status: {inv.status}")
    
    return invoices


@app.get("/my/invoices/{invoice_id:int}", response_model=InvoiceOut)
async def get_my_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Query invoice with template information
    invoice = db.query(Invoice).filter(
        Invoice.user_id == current_user.id, 
        Invoice.id == invoice_id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Add template name if template exists
    if invoice.template_id:
        template = db.query(InvoiceTemplate).filter(InvoiceTemplate.id == invoice.template_id).first()
        if template:
            invoice.template_name = template.name
    
    # Debug logging
    print(f"DEBUG: Retrieved invoice {invoice.id}: {invoice.invoice_number}")
    
    return invoice


# Payments API
@app.get("/my/invoices/{invoice_id:int}/payments", response_model=List[PaymentOut])
async def list_my_invoice_payments(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return (
        db.query(Payment)
        .filter(Payment.invoice_id == inv.id)
        .order_by(Payment.date.desc(), Payment.id.desc())
        .all()
    )


@app.post("/invoices/{invoice_id:int}/payments", response_model=PaymentOut)
async def add_payment(invoice_id: int, body: PaymentIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    # normalize date from optional string
    pay_date = None
    if body.date:
        try:
            pay_date = datetime.strptime(body.date, "%Y-%m-%d").date()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    p = Payment(
        invoice_id=inv.id,
        amount=body.amount,
        method=body.method,
        date=pay_date or date.today(),
        ref=body.ref,
        note=body.note,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    # Update derived status
    total_paid = (
        db.query(Payment)
        .filter(Payment.invoice_id == inv.id)
        .with_entities(func.coalesce(func.sum(Payment.amount), 0.0))
        .scalar()
    )
    if total_paid >= (inv.total or 0):
        inv.status = "PAID"
        inv.paid_on = p.date
    elif total_paid > 0:
        inv.status = "PARTIALLY_PAID"
        inv.paid_on = None
    else:
        inv.status = "UNPAID"
        inv.paid_on = None
    db.commit()
    return p


@app.delete("/payments/{payment_id:int}")
async def delete_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = (
        db.query(Payment)
        .join(Invoice, Payment.invoice_id == Invoice.id)
        .filter(Invoice.user_id == current_user.id, Payment.id == payment_id)
        .first()
    )
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")
    inv_id = p.invoice_id
    db.delete(p)
    db.commit()
    inv = db.query(Invoice).filter(Invoice.id == inv_id).first()
    total_paid = (
        db.query(Payment)
        .filter(Payment.invoice_id == inv.id)
        .with_entities(func.coalesce(func.sum(Payment.amount), 0.0))
        .scalar()
    )
    if total_paid >= (inv.total or 0):
        inv.status = "PAID"
        inv.paid_on = date.today()
    elif total_paid > 0:
        inv.status = "PARTIALLY_PAID"
        inv.paid_on = None
    else:
        inv.status = "UNPAID"
        inv.paid_on = None
    db.commit()
    return {"ok": True}


@app.put("/invoices/{invoice_id:int}", response_model=InvoiceOut)
async def update_invoice(
    invoice_id: int,
    body: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    buyer = db.query(Customer).filter(Customer.user_id == current_user.id, Customer.id == body.buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not bp:
        raise HTTPException(status_code=400, detail="Business profile incomplete")
    seller_state = bp.state_code or extract_state_code(bp.gstin)
    buyer_state = buyer.state_code or extract_state_code(buyer.gstin)

    # Update invoice header
    if body.date:
        try:
            inv.date = datetime.strptime(body.date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    if body.due_date:
        try:
            inv.due_date = datetime.strptime(body.due_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date format. Use YYYY-MM-DD")
    inv.buyer_id = buyer.id
    inv.seller_gstin = bp.gstin
    inv.seller_state_code = seller_state
    inv.updated_at = datetime.utcnow()

    # Replace items
    inv.items.clear()
    for it in body.items:
        inv.items.append(InvoiceItem(
            description=it.description,
            hsn_code=it.hsn_code,
            quantity=it.quantity,
            rate=it.rate,
            gst_rate=it.gst_rate,
        ))

    subtotal, cgst, sgst, igst, total = compute_totals(inv.items, seller_state, buyer_state)
    inv.subtotal = subtotal
    inv.cgst = cgst
    inv.sgst = sgst
    inv.igst = igst
    inv.total = total

    db.commit()
    db.refresh(inv)
    return inv


@app.post("/invoices/{invoice_id:int}/mark-paid", response_model=InvoiceOut)
async def mark_paid(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    inv.status = "PAID"
    db.commit()
    db.refresh(inv)
    return inv


@app.post("/invoices/{invoice_id:int}/mark-unpaid", response_model=InvoiceOut)
async def mark_unpaid(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    inv.status = "UNPAID"
    db.commit()
    db.refresh(inv)
    return inv


@app.post("/invoices/{invoice_id:int}/duplicate", response_model=InvoiceOut)
async def duplicate_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    src = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not src:
        raise HTTPException(status_code=404, detail="Invoice not found")
    dup = Invoice(
        user_id=current_user.id,
        invoice_number=next_invoice_number(db, current_user.id),
        date=date.today(),
        due_date=src.due_date,
        seller_gstin=src.seller_gstin,
        seller_state_code=src.seller_state_code,
        buyer_id=src.buyer_id,
        status="UNPAID",
    )
    for it in src.items:
        dup.items.append(InvoiceItem(
            description=it.description,
            hsn_code=it.hsn_code,
            quantity=it.quantity,
            rate=it.rate,
            gst_rate=it.gst_rate,
        ))
    subtotal, cgst, sgst, igst, total = compute_totals(dup.items, src.seller_state_code, src.buyer.state_code)
    dup.subtotal, dup.cgst, dup.sgst, dup.igst, dup.total = subtotal, cgst, sgst, igst, total
    db.add(dup)
    db.commit()
    db.refresh(dup)
    return dup


@app.delete("/invoices/{invoice_id:int}")
async def delete_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(inv)
    db.commit()
    return {"ok": True}


# ================================================
# HSN/SAC Database Search API
# ================================================

@app.get("/hsn/search")
async def search_hsn_codes(
    q: str = Query(..., min_length=1, description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
    type: str | None = Query(None, description="Filter by type (HSN/SAC)"),
    limit: int = Query(10, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search HSN/SAC codes from database with intelligent filtering"""
    q = q.strip()
    print(f"DEBUG: HSN search query: {q}, category: {category}, type: {type}")
    
    # Base query
    query = db.query(HSNCode).filter(HSNCode.is_active == True)
    
    # Text search across code, description, and keywords
    search_term = f"%{q.lower()}%"
    text_filter = (
        func.lower(HSNCode.code).like(search_term) |
        func.lower(HSNCode.description).like(search_term) |
        func.lower(HSNCode.keywords).like(search_term)
    )
    query = query.filter(text_filter)
    
    # Category filter
    if category:
        query = query.filter(func.lower(HSNCode.category) == category.lower())
    
    # Type filter (HSN for products, SAC for services)
    if type:
        query = query.filter(func.lower(HSNCode.type) == type.lower())
    
    # Order by usage count (popularity) and then by code
    query = query.order_by(HSNCode.usage_count.desc(), HSNCode.code)
    
    # Execute query
    results = query.limit(limit).all()
    
    print(f"DEBUG: Found {len(results)} HSN/SAC codes")
    
    # Format response
    return [
        {
            "id": hsn.id,
            "code": hsn.code,
            "desc": hsn.description,
            "description": hsn.description,
            "gst": hsn.gst_rate,
            "gst_rate": hsn.gst_rate,
            "type": hsn.type,
            "category": hsn.category,
            "subcategory": hsn.subcategory,
            "unit": hsn.unit,
            "keywords": hsn.keywords
        }
        for hsn in results
    ]

@app.post("/hsn/{hsn_id}/use")
async def record_hsn_usage(hsn_id: int, db: Session = Depends(get_db)):
    """Record HSN code usage for analytics"""
    hsn = db.query(HSNCode).filter(HSNCode.id == hsn_id).first()
    if hsn:
        hsn.usage_count += 1
        db.commit()
    return {"status": "recorded"}

# Legacy HSN API (for backward compatibility)
@app.get("/hsn/suggest")
async def hsn_suggest(q: str, db: Session = Depends(get_db)):
    """Legacy HSN suggest endpoint - now uses database instead of JSON"""
    # Use the new database search but format as old response
    try:
        results = await search_hsn_codes(q=q, limit=8, db=db)
        return results
    except Exception as e:
        print(f"HSN search error: {e}")
        # Fallback to old system if needed
        from hsn_service import suggest_hsn
    return suggest_hsn(q)


# ---- PDF preview/generation (MVP HTML-to-PDF placeholder) ----
@app.get("/invoices/{invoice_id:int}/preview")
async def invoice_preview(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {
        "invoice_number": inv.invoice_number,
        "date": str(inv.date),
        "due_date": str(inv.due_date) if inv.due_date else None,
        "buyer": {
            "id": inv.buyer.id,
            "name": inv.buyer.name,
            "gstin": inv.buyer.gstin,
            "state_code": inv.buyer.state_code,
            "address": inv.buyer.address,
        },
        "items": [
            {
                "description": it.description,
                "hsn_code": it.hsn_code,
                "quantity": it.quantity,
                "rate": it.rate,
                "gst_rate": it.gst_rate,
                "amount": it.amount,
                "tax_amount": it.tax_amount,
            }
            for it in inv.items
        ],
        "subtotal": inv.subtotal,
        "cgst": inv.cgst,
        "sgst": inv.sgst,
        "igst": inv.igst,
        "total": inv.total,
        "status": inv.status,
        "seller": {
            "gstin": inv.seller_gstin,
            "state_code": inv.seller_state_code,
        },
    }


@app.get("/my/invoices/{invoice_id:int}/pdf")
async def my_invoice_pdf(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Get business profile
    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    
    # Debug business profile data
    if bp:
        print(f"DEBUG: Business Profile found for user {current_user.id}")
        print(f"DEBUG: Bank Name: {bp.bank_name}")
        print(f"DEBUG: Bank IFSC: {bp.bank_ifsc}")
        print(f"DEBUG: Default Terms: {bp.default_terms}")
        print(f"DEBUG: Primary Color: {bp.primary_color}")
    else:
        print(f"DEBUG: No Business Profile found for user {current_user.id}")
    
    # Get template if invoice was created with one
    template = None
    if inv.template_id:
        template = db.query(InvoiceTemplate).filter(
            InvoiceTemplate.id == inv.template_id,
            InvoiceTemplate.user_id == current_user.id
        ).first()
        print(f"DEBUG: Invoice {inv.id} has template_id: {inv.template_id}")
        print(f"DEBUG: Template found: {template.name if template else 'None'}")
        if template:
            print(f"DEBUG: Template file path: {template.template_file_path}")
    else:
        print(f"DEBUG: Invoice {inv.id} has no template_id")
    
    pdf_bytes = render_invoice_pdf(inv, bp, template)
    return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf", headers={"Content-Disposition": f"inline; filename={inv.invoice_number}.pdf"})


# Backward compatibility - deprecated endpoint
@app.get("/invoices/{invoice_id:int}/pdf", deprecated=True)
async def invoice_pdf_deprecated(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Deprecated: Use /my/invoices/{invoice_id}/pdf instead"""
    return await my_invoice_pdf(invoice_id, db, current_user)


def generate_public_token(invoice_id: int, secret_key: str = "your-secret-key") -> str:
    """Generate a secure token for public invoice access"""
    # Simplified approach - just use invoice ID and secret for now
    secret = os.getenv("PDF_SECRET_KEY", secret_key)
    token_data = f"{invoice_id}:{secret}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    print(f"DEBUG: Generated token for invoice {invoice_id}: {token[:20]}...")
    return token


def verify_public_token(invoice_id: int, token: str, secret_key: str = "your-secret-key") -> bool:
    """Verify the public access token"""
    secret = os.getenv("PDF_SECRET_KEY", secret_key)
    token_data = f"{invoice_id}:{secret}"
    expected_token = hashlib.sha256(token_data.encode()).hexdigest()
    
    print(f"DEBUG: Verifying token for invoice {invoice_id}")
    print(f"DEBUG: Expected token: {expected_token[:20]}...")
    print(f"DEBUG: Received token: {token[:20]}...")
    print(f"DEBUG: Tokens match: {token == expected_token}")
    
    return token == expected_token


@app.get("/public/invoices/{invoice_id:int}/pdf")
async def public_invoice_pdf(invoice_id: int, token: str, db: Session = Depends(get_db)):
    """
    Public PDF endpoint for customers to access invoice PDFs without authentication.
    Requires a secure, time-limited token for access.
    """
    # Verify the token
    if not verify_public_token(invoice_id, token):
        raise HTTPException(status_code=403, detail="Invalid access token")
    
    # Get invoice and verify it exists
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Additional security: Verify the user still exists and is active
    user = db.query(User).filter(User.id == inv.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invoice no longer available")
    
    # Get business profile
    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == inv.user_id).first()
    
    # Get template if invoice was created with one
    template = None
    if inv.template_id:
        template = db.query(InvoiceTemplate).filter(
            InvoiceTemplate.id == inv.template_id,
            InvoiceTemplate.user_id == inv.user_id
        ).first()
    
    pdf_bytes = render_invoice_pdf(inv, bp, template)
    return StreamingResponse(
        iter([pdf_bytes]), 
        media_type="application/pdf", 
        headers={
            "Content-Disposition": f"attachment; filename={inv.invoice_number}.pdf",  # Force download
            "Cache-Control": "private, max-age=1800"  # 30 minutes private cache
        }
    )


@app.get("/my/invoices/{invoice_id:int}/share")
async def my_invoice_share(invoice_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.id == invoice_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    base = str(request.base_url).rstrip('/')
    
    # Generate secure public PDF URL
    token = generate_public_token(invoice_id)
    public_pdf_url = f"{base}/public/invoices/{invoice_id}/pdf?token={token}"
    
    # Professional message format for WhatsApp
    business_name = "Your Business"  # Default fallback
    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if bp and bp.business_name:
        business_name = bp.business_name
    
    # Professional message format
    msg = f"""🧾 *Invoice from {business_name}*

📋 Invoice: {inv.invoice_number}
💰 Amount: ₹{inv.total:.2f}
📅 Date: {inv.date.strftime('%d %b %Y') if inv.date else 'N/A'}

📄 Download PDF: {public_pdf_url}

Thank you for your business! 🙏"""
    
    # Generic WhatsApp share (no preset recipient)
    whatsapp_url = f"https://wa.me/?text={quote(msg)}"
    
    # Direct WhatsApp to buyer phone, if available
    whatsapp_direct = None
    phone = getattr(inv.buyer, 'phone', None)
    if phone:
        digits = ''.join(ch for ch in phone if ch.isdigit())
        # If Indian 10-digit number, prefix 91
        if len(digits) == 10:
            digits = '91' + digits
        if len(digits) >= 11:  # basic sanity
            whatsapp_direct = f"https://wa.me/{digits}?text={quote(msg)}"
    
    email_subject = quote(f"Invoice {inv.invoice_number} from {business_name}")
    email_body = quote(f"Please find your invoice attached. Amount: ₹{inv.total:.2f}. Download: {public_pdf_url}")
    
    return {
        "pdf_url": public_pdf_url,  # Now returns public URL
        "whatsapp_url": whatsapp_url, 
        "whatsapp_direct": whatsapp_direct, 
        "email_subject": email_subject, 
        "email_body": email_body,
        "professional_message": msg  # Include formatted message
    }


# ---- Dashboard summary ----
@app.get("/invoices/summary")
async def invoices_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    # Outstanding: unpaid/overdue sums
    unpaid = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.status != "PAID")
        .all()
    )
    outstanding_total = sum(i.total or 0 for i in unpaid)
    overdue = [
        {
            "id": i.id,
            "invoice_number": i.invoice_number,
            "customer": i.buyer.name if i.buyer else None,
            "due_date": str(i.due_date) if i.due_date else None,
            "days_overdue": (today - i.due_date).days if i.due_date and i.due_date < today else 0,
            "total": i.total,
        }
        for i in unpaid
        if i.due_date and i.due_date < today
    ]
    overdue.sort(key=lambda x: x["days_overdue"], reverse=True)

    # This month
    start_month = today.replace(day=1)
    this_month_paid = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.status == "PAID", Invoice.date >= start_month, Invoice.date <= today)
        .all()
    )
    this_month_revenue = sum(i.total or 0 for i in this_month_paid)
    invoices_this_month = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.date >= start_month, Invoice.date <= today)
        .count()
    )

    # Last 6 months revenue series
    series = []
    for m in range(5, -1, -1):
        ref = (start_month - timedelta(days=1)).replace(day=1)
        # compute month by stepping back
        ref_dt = (start_month.replace(day=1) - timedelta(days=1))
        # Adjust for m steps
        dt = start_month
        for _ in range(m):
            dt = (dt.replace(day=1) - timedelta(days=1)).replace(day=1)
        month_start = dt
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        month_end = next_month - timedelta(days=1)
        rows = (
            db.query(Invoice)
            .filter(Invoice.user_id == current_user.id, Invoice.status == "PAID", Invoice.date >= month_start, Invoice.date <= month_end)
            .all()
        )
        total = sum(i.total or 0 for i in rows)
        label = month_start.strftime("%b")
        series.append({"label": label, "total": round(total, 2)})

    # Top customers by total (last 90 days)
    since = today - timedelta(days=90)
    recent = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id, Invoice.date >= since)
        .all()
    )
    cust_totals = {}
    for i in recent:
        name = i.buyer.name if i.buyer else "-"
        cust_totals[name] = cust_totals.get(name, 0) + (i.total or 0)
    top_customers = [
        {"name": k, "total": round(v, 2)} for k, v in sorted(cust_totals.items(), key=lambda kv: kv[1], reverse=True)[:5]
    ]

    return {
        "outstanding_total": round(outstanding_total, 2),
        "overdue_count": len(overdue),
        "this_month_revenue": round(this_month_revenue, 2),
        "invoices_this_month": invoices_this_month,
        "monthly_revenue": series,
        "overdue_list": overdue[:5],
        "top_customers": top_customers,
    }


# Alias to avoid routing conflict with /invoices/{invoice_id}
@app.get("/summary")
async def summary_alias(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await invoices_summary(db=db, current_user=current_user)


# Export endpoints
@app.get("/invoices/export")
async def export_invoices(
    status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    customer_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export invoices to CSV format"""
    from fastapi.responses import Response
    import csv
    from io import StringIO
    
    # Build query same as list_invoices
    qry = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    if status:
        qry = qry.filter(Invoice.status == status.upper())
    if date_from:
        qry = qry.filter(Invoice.date >= date_from)
    if date_to:
        qry = qry.filter(Invoice.date <= date_to)
    if customer_id:
        qry = qry.filter(Invoice.buyer_id == customer_id)
    
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
    
    filename = f"invoices_export_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/customers/{customer_id}/invoices/export")
async def export_customer_invoices(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export customer-specific invoices to CSV"""
    from fastapi.responses import Response
    import csv
    from io import StringIO
    
    # Get customer
    customer = db.query(Customer).filter(Customer.user_id == current_user.id, Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get invoices for this customer
    invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.buyer_id == customer_id
    ).order_by(Invoice.date.desc()).all()
    
    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Invoice Number', 'Date', 'Subtotal', 'CGST', 'SGST', 'IGST', 
        'Total', 'Status', 'Paid On'
    ])
    
    # Data rows
    for inv in invoices:
        writer.writerow([
            inv.invoice_number,
            inv.date.strftime('%Y-%m-%d') if inv.date else '',
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
    
    filename = f"invoices_{customer.name}_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# Template management endpoints
@app.post("/templates", response_model=InvoiceTemplateOut)
async def create_template(
    template: InvoiceTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new invoice template for the user"""
    # If this is the first template, make it default
    existing_templates = db.query(InvoiceTemplate).filter(InvoiceTemplate.user_id == current_user.id).count()
    is_default = existing_templates == 0
    
    db_template = InvoiceTemplate(
        **template.model_dump(),
        user_id=current_user.id,
        is_default=is_default
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@app.get("/templates", response_model=List[InvoiceTemplateOut])
async def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all templates for the user"""
    return db.query(InvoiceTemplate).filter(InvoiceTemplate.user_id == current_user.id).all()


@app.get("/templates/{template_id}", response_model=InvoiceTemplateOut)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific template"""
    template = db.query(InvoiceTemplate).filter(
        InvoiceTemplate.id == template_id,
        InvoiceTemplate.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@app.put("/templates/{template_id}", response_model=InvoiceTemplateOut)
async def update_template(
    template_id: int,
    template: InvoiceTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a template"""
    db_template = db.query(InvoiceTemplate).filter(
        InvoiceTemplate.id == template_id,
        InvoiceTemplate.user_id == current_user.id
    ).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # If setting as default, unset other defaults
    if template.is_default:
        db.query(InvoiceTemplate).filter(
            InvoiceTemplate.user_id == current_user.id,
            InvoiceTemplate.is_default == True
        ).update({"is_default": False})
    
    for field, value in template.model_dump(exclude_unset=True).items():
        setattr(db_template, field, value)
    
    db_template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_template)
    return db_template


@app.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a template"""
    template = db.query(InvoiceTemplate).filter(
        InvoiceTemplate.id == template_id,
        InvoiceTemplate.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Don't allow deletion of default template if it's the only one
    if template.is_default:
        total_templates = db.query(InvoiceTemplate).filter(InvoiceTemplate.user_id == current_user.id).count()
        if total_templates == 1:
            raise HTTPException(status_code=400, detail="Cannot delete the only template")
    
    # Remove template file
    if template.template_file_path and os.path.exists(template.template_file_path):
        try:
            os.remove(template.template_file_path)
        except Exception:
            pass  # Don't fail if file removal fails
    
    db.delete(template)
    db.commit()
    return {"message": "Template deleted"}


@app.post("/templates/{template_id}/upload")
async def upload_template_file(
    template_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload PDF template file for Gemini analysis"""
    # Verify template belongs to user
    template = db.query(InvoiceTemplate).filter(
        InvoiceTemplate.id == template_id,
        InvoiceTemplate.user_id == current_user.id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Validate file type
    if not file.content_type == 'application/pdf':
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/templates"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f"template_{template_id}_{int(datetime.utcnow().timestamp())}.pdf"
    file_path = os.path.join(upload_dir, filename)
    
    # Save PDF file
    try:
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Update template with file path
        template.template_file_path = file_path
        db.commit()
        
        return {
            "message": "Template file uploaded successfully! The system will automatically detect form fields and fill them with invoice data.",
            "file_path": file_path,
            "template_name": template.name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save template file: {str(e)}")


@app.get("/templates/{template_id}/download")
async def download_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download template file"""
    template = db.query(InvoiceTemplate).filter(
        InvoiceTemplate.id == template_id,
        InvoiceTemplate.user_id == current_user.id
    ).first()
    if not template or not template.template_file_path:
        raise HTTPException(status_code=404, detail="Template file not found")
    
    # Return the template file
    if os.path.exists(template.template_file_path):
        from fastapi.responses import FileResponse
        return FileResponse(
            template.template_file_path,
            media_type="application/pdf",
            filename=f"{template.name}.pdf"
        )
    else:
        raise HTTPException(status_code=404, detail="Template file not found")


# ============================================================================
# ITEM LIBRARY ENDPOINTS
# ============================================================================

@app.post("/item-library", response_model=LibraryItemOut)
async def create_library_item(
    body: LibraryItemIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new item in the user's library"""
    library_item = LibraryItem(user_id=current_user.id, **body.model_dump())
    db.add(library_item)
    db.commit()
    db.refresh(library_item)
    return library_item


@app.get("/item-library", response_model=List[LibraryItemOut])
async def list_library_items(
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all items in the user's library with optional search"""
    qry = db.query(LibraryItem).filter(LibraryItem.user_id == current_user.id)
    
    if q:
        like = f"%{q}%"
        qry = qry.filter(
            LibraryItem.description.ilike(like) |
            LibraryItem.hsn_code.ilike(like) |
            LibraryItem.category.ilike(like)
        )
    
    return qry.order_by(LibraryItem.description).all()


@app.get("/item-library/{item_id}", response_model=LibraryItemOut)
async def get_library_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific library item"""
    item = db.query(LibraryItem).filter(
        LibraryItem.id == item_id,
        LibraryItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found")
    
    return item


@app.put("/item-library/{item_id}", response_model=LibraryItemOut)
async def update_library_item(
    item_id: int,
    body: LibraryItemIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a library item"""
    item = db.query(LibraryItem).filter(
        LibraryItem.id == item_id,
        LibraryItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found")
    
    # Update fields
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


@app.delete("/item-library/{item_id}")
async def delete_library_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a library item"""
    item = db.query(LibraryItem).filter(
        LibraryItem.id == item_id,
        LibraryItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Library item deleted successfully"}


@app.post("/item-library/sample-data")
async def add_sample_library_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add sample library items for testing (only for development)"""
    sample_items = [
        {
            "description": "Laptop Computer",
            "hsn_code": "8471",
            "sac_code": "",
            "gst_rate": 18.0,
            "unit": "Nos",
            "category": "Electronics",
            "is_active": True
        },
        {
            "description": "Office Chair",
            "hsn_code": "9401",
            "sac_code": "",
            "gst_rate": 18.0,
            "unit": "Nos",
            "category": "Furniture",
            "is_active": True
        },
        {
            "description": "Web Development Services",
            "hsn_code": "",
            "sac_code": "998314",
            "gst_rate": 18.0,
            "unit": "Hours",
            "category": "Services",
            "is_active": True
        }
    ]
    
    created_items = []
    for item_data in sample_items:
        item = LibraryItem(user_id=current_user.id, **item_data)
        db.add(item)
        created_items.append(item)
    
    db.commit()
    
    for item in created_items:
        db.refresh(item)
    
    return {"message": f"Added {len(created_items)} sample items", "items": created_items}


# ============================================================================
# NEW ONBOARDING & SERVICE TEMPLATE ENDPOINTS
# ============================================================================

@app.put("/users/onboarding", response_model=UserOut)
async def update_user_onboarding(
    body: UserOnboardingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user onboarding status and business type"""
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(current_user, k, v)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    return current_user


@app.get("/users/onboarding")
async def get_user_onboarding_status(
    current_user: User = Depends(get_current_user)
):
    """Get current user's onboarding status"""
    return {
        "completed": current_user.onboarding_completed,
        "step": current_user.onboarding_step,
        "business_type": current_user.business_type
    }


@app.post("/business-profile", response_model=BusinessProfileOut)
async def create_business_profile(
    body: BusinessProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update business profile"""
    # Check if business profile exists
    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    
    if not bp:
        # Create new business profile - only use fields that exist in the model
        profile_data = body.model_dump()
        
        # Filter to only include fields that exist in BusinessProfile model
        valid_fields = {
            'business_name', 'gstin', 'pan', 'address', 'state_code', 'phone', 'email',
            'turnover_category', 'current_financial_year', 'next_invoice_seq', 'invoice_prefix',
            'logo_path', 'signature_path', 'primary_color', 'bank_account_name', 'bank_name',
            'bank_branch', 'bank_account_number', 'bank_ifsc', 'upi_id', 'default_terms',
            'accepts_cash', 'cash_note'
        }
        
        # Only include fields that exist in the model
        filtered_data = {k: v for k, v in profile_data.items() if k in valid_fields}
        
        bp = BusinessProfile(user_id=current_user.id, **filtered_data)
        db.add(bp)
    else:
        # Update existing business profile - only update fields that exist
        profile_data = body.model_dump(exclude_unset=True)
        
        # Only update fields that exist in the model
        valid_fields = {
            'business_name', 'gstin', 'pan', 'address', 'state_code', 'phone', 'email',
            'turnover_category', 'current_financial_year', 'next_invoice_seq', 'invoice_prefix',
            'logo_path', 'signature_path', 'primary_color', 'bank_account_name', 'bank_name',
            'bank_branch', 'bank_account_number', 'bank_ifsc', 'upi_id', 'default_terms',
            'accepts_cash', 'cash_note'
        }
        
        for k, v in profile_data.items():
            if k in valid_fields:
                setattr(bp, k, v)
    
    db.commit()
    db.refresh(bp)
    return bp


@app.post("/service-templates", response_model=ServiceTemplateOut)
async def create_service_template(
    body: ServiceTemplateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new service template"""
    try:
        print(f"DEBUG: Creating service template for user {current_user.id}")
        print(f"DEBUG: Request body: {body.model_dump()}")
        
        # Get or create business profile
        bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
        if not bp:
            print(f"DEBUG: No business profile found for user {current_user.id}")
            raise HTTPException(status_code=400, detail="Business profile not found. Please create business profile first.")
        
        print(f"DEBUG: Found business profile {bp.id}")
        
        # Create service template
        template_data = body.model_dump()
        template = ServiceTemplate(
            user_id=current_user.id,
            business_profile_id=bp.id,
            **template_data
        )
        
        print(f"DEBUG: Created template object: {template}")
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        print(f"DEBUG: Successfully created template with ID {template.id}")
        return template
        
    except Exception as e:
        print(f"ERROR: Failed to create service template: {e}")
        print(f"ERROR: Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Failed to create service template: {str(e)}")


@app.get("/service-templates", response_model=List[ServiceTemplateOut])
async def get_service_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all service templates for the current user"""
    templates = db.query(ServiceTemplate).filter(
        ServiceTemplate.user_id == current_user.id,
        ServiceTemplate.is_active == True
    ).order_by(ServiceTemplate.description).all()
    
    return templates


@app.get("/service-templates/{template_id}", response_model=ServiceTemplateOut)
async def get_service_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific service template"""
    template = db.query(ServiceTemplate).filter(
        ServiceTemplate.id == template_id,
        ServiceTemplate.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Service template not found")
    
    return template


@app.put("/service-templates/{template_id}", response_model=ServiceTemplateOut)
async def update_service_template(
    template_id: int,
    body: ServiceTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a service template"""
    template = db.query(ServiceTemplate).filter(
        ServiceTemplate.id == template_id,
        ServiceTemplate.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Service template not found")
    
    # Update fields
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(template, k, v)
    
    template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(template)
    return template


@app.delete("/service-templates/{template_id}")
async def delete_service_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a service template"""
    template = db.query(ServiceTemplate).filter(
        ServiceTemplate.id == template_id,
        ServiceTemplate.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Service template not found")
    
    db.delete(template)
    db.commit()
    return {"message": "Service template deleted successfully"}


@app.post("/service-templates/generate-from-services")
async def generate_service_templates(
    service_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate service templates from selected service categories"""
    # Get or create business profile
    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not bp:
        raise HTTPException(status_code=400, detail="Business profile not found. Please create business profile first.")
    
    # Service categories with SAC codes and GST rates
    service_categories = {
        'web_development': {
            'name': 'Web Development',
            'sac_code': '998314',
            'gst_rate': 18.0,
            'description': 'Professional web development services including frontend, backend, and full-stack development',
            'base_rate': 25000.0
        },
        'mobile_app_development': {
            'name': 'Mobile App Development',
            'sac_code': '998314',
            'gst_rate': 18.0,
            'description': 'Mobile application development for iOS and Android platforms',
            'base_rate': 35000.0
        },
        'digital_marketing': {
            'name': 'Digital Marketing',
            'sac_code': '998315',
            'gst_rate': 18.0,
            'description': 'Comprehensive digital marketing services including SEO, SEM, and social media',
            'base_rate': 15000.0
        },
        'ui_ux_design': {
            'name': 'UI/UX Design',
            'sac_code': '998314',
            'gst_rate': 18.0,
            'description': 'User interface and user experience design services',
            'base_rate': 20000.0
        },
        'seo_services': {
            'name': 'SEO Services',
            'sac_code': '998315',
            'gst_rate': 18.0,
            'description': 'Search engine optimization and organic traffic improvement',
            'base_rate': 12000.0
        },
        'content_writing': {
            'name': 'Content Writing',
            'sac_code': '998315',
            'gst_rate': 18.0,
            'description': 'Professional content creation for websites, blogs, and marketing',
            'base_rate': 8000.0
        },
        'business_consulting': {
            'name': 'Business Consulting',
            'sac_code': '998314',
            'gst_rate': 18.0,
            'description': 'Strategic business consulting and advisory services',
            'base_rate': 30000.0
        },
        'graphic_design': {
            'name': 'Graphic Design',
            'sac_code': '998314',
            'gst_rate': 18.0,
            'description': 'Creative graphic design services for branding and marketing',
            'base_rate': 15000.0
        }
    }
    
    created_templates = []
    
    for service_id in service_ids:
        if service_id in service_categories:
            service_data = service_categories[service_id]
            
            # Check if template already exists
            existing = db.query(ServiceTemplate).filter(
                ServiceTemplate.user_id == current_user.id,
                ServiceTemplate.description == service_data['name']
            ).first()
            
            if not existing:
                template = ServiceTemplate(
                    user_id=current_user.id,
                    business_profile_id=bp.id,
                    description=service_data['name'],  # Changed from service_name to description
                    sac_code=service_data['sac_code'],
                    gst_rate=service_data['gst_rate'],
                    unit='Nos',  # Default unit for services
                    base_rate=service_data['base_rate']
                )
                
                db.add(template)
                created_templates.append(template)
    
    if created_templates:
        db.commit()
        for template in created_templates:
            db.refresh(template)
    
    return {
        "message": f"Generated {len(created_templates)} service templates",
        "templates": created_templates
    }


@app.post("/service-templates/generate-from-products")
async def generate_product_templates(
    product_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate product templates from selected product categories"""
    # Get or create business profile
    bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not bp:
        raise HTTPException(status_code=400, detail="Business profile not found. Please create business profile first.")
    
    created_templates = []
    
    for product_id in product_ids:
        # Get the product details from HSN codes
        product = db.query(HSNCode).filter(
            HSNCode.id == int(product_id),
            HSNCode.type == 'HSN'
        ).first()
        
        if product:
            # Check if template already exists
            existing = db.query(ServiceTemplate).filter(
                ServiceTemplate.user_id == current_user.id,
                ServiceTemplate.description == product.description
            ).first()
            
            if not existing:
                template = ServiceTemplate(
                    user_id=current_user.id,
                    business_profile_id=bp.id,
                    description=product.description,
                    sac_code=product.code,  # Use HSN code as SAC code for products
                    gst_rate=product.gst_rate,
                    hsn_code=product.code,  # Store the actual HSN code
                    unit='Nos',  # Default unit for products
                    base_rate=1000.0  # Default base rate for products
                )
                
                db.add(template)
                created_templates.append(template)
    
    if created_templates:
        db.commit()
        for template in created_templates:
            db.refresh(template)
    
    return {
        "message": f"Generated {len(created_templates)} product templates",
        "templates": created_templates
    }


# ================================================
# Master Services API
# ================================================

@app.get("/debug/user-status")
async def debug_user_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check user authentication and business profile"""
    try:
        bp = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
        
        return {
            "user_id": current_user.id,
            "user_email": current_user.email,
            "has_business_profile": bp is not None,
            "business_profile_id": bp.id if bp else None,
            "business_name": bp.business_name if bp else None,
            "authentication_working": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "authentication_working": False
        }

@app.get("/debug/database-status")
async def debug_database_status(db: Session = Depends(get_db)):
    """Debug endpoint to check database connection and content"""
    import os
    from database import DATABASE_URL
    
    try:
        total_count = db.query(MasterService).count()
        active_count = db.query(MasterService).filter(MasterService.is_active == True).count()
        
        # Get first few services for verification
        services = db.query(MasterService).limit(3).all()
        service_names = [s.name for s in services]
        
        return {
            "database_url": DATABASE_URL,
            "working_directory": os.getcwd(),
            "total_services": total_count,
            "active_services": active_count,
            "sample_services": service_names,
            "database_file_exists": os.path.exists("invoicegen.db"),
            "current_time": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "database_url": DATABASE_URL,
            "working_directory": os.getcwd()
        }

@app.get("/master-services/search", response_model=List[MasterServiceOut])
async def search_master_services(
    q: str = Query(..., min_length=1, description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
    business_type: str | None = Query(None, description="Filter by business type"),
    limit: int = Query(10, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search master services with intelligent filtering"""
    # Clean the search query
    q = q.strip()
    print(f"DEBUG: Search query: {q}, category: {category}, business_type: {business_type}")
    
    # First, check if we have any master services at all
    total_count = db.query(MasterService).count()
    print(f"DEBUG: Total master services in DB: {total_count}")
    
    query = db.query(MasterService).filter(MasterService.is_active == True)
    active_count = query.count()
    print(f"DEBUG: Active master services: {active_count}")
    
    # Simplified search - just search names first
    search_term = f"%{q.lower()}%"
    query = query.filter(func.lower(MasterService.name).like(search_term))
    
    search_count = query.count()
    print(f"DEBUG: Services matching search term '{search_term}': {search_count}")
    
    # Category filter
    if category:
        query = query.filter(func.lower(MasterService.category) == category.lower())
    
    # Business type filter
    if business_type:
        query = query.filter(
            (MasterService.business_type == business_type) |
            (MasterService.business_type == "both")
        )
    
    # Order by usage count (popularity) and then alphabetically
    services = query.order_by(
        MasterService.usage_count.desc(),
        MasterService.name
    ).limit(limit).all()
    
    print(f"DEBUG: Final results count: {len(services)}")
    for service in services:
        print(f"DEBUG: - {service.name}")
    
    return services


@app.get("/master-services/categories")
async def get_master_service_categories(db: Session = Depends(get_db)):
    """Get all available service categories"""
    categories = db.query(MasterService.category).filter(
        MasterService.is_active == True
    ).distinct().all()
    
    return [{"name": cat[0], "display_name": cat[0].replace("_", " ").title()} for cat in categories]


@app.post("/master-services/{service_id}/use")
async def increment_service_usage(
    service_id: int,
    db: Session = Depends(get_db)
):
    """Increment usage count for analytics"""
    service = db.query(MasterService).filter(MasterService.id == service_id).first()
    if service:
        service.usage_count += 1
        db.commit()
    return {"message": "Usage recorded"}


@app.get("/service-categories")
async def get_service_categories(db: Session = Depends(get_db)):
    """
    ENHANCED: Get service categories and their specific services for onboarding
    Now returns both categories AND specific services within each category
    """
    
    # Get all unique categories from our specific services
    categories = db.query(MasterService.category).filter(
        MasterService.is_active == True
    ).distinct().all()
    
    result = {"categories": []}
    
    for category_tuple in categories:
        category_name = category_tuple[0]
        
        # Get specific services for this category (limit to popular ones for onboarding)
        specific_services = db.query(MasterService).filter(
            MasterService.category == category_name,
            MasterService.is_active == True
        ).order_by(MasterService.usage_count.desc()).limit(8).all()
        
        if specific_services:
            # Use the first service's data as category defaults
            first_service = specific_services[0]
            
            category_data = {
                "id": category_name.lower().replace(" ", "_").replace("_services", ""),
                "name": category_name.replace("_", " ").title(),
                "description": f"Professional {category_name.replace('_', ' ').lower()} services",
                "sac_code": first_service.sac_code,
                "gst_rate": first_service.gst_rate,
                "category": category_name,
                # NEW: Include specific services for this category
                "specific_services": [
                    {
                        "id": f"service_{service.id}",
                        "name": service.name,
                        "description": service.description,
                        "sac_code": service.sac_code,
                        "gst_rate": service.gst_rate,
                        "keywords": service.keywords
                    }
                    for service in specific_services
                ]
            }
            
            result["categories"].append(category_data)
    
    return result


# ============================================================================
# MASTER PRODUCTS API ENDPOINTS
# ============================================================================

@app.get("/master-products/search")
async def search_master_products(
    q: str = Query(..., min_length=1, description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(10, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search master products with intelligent filtering"""
    # Clean the search query
    q = q.strip()
    print(f"DEBUG: Product search query: {q}, category: {category}")
    
    # Build the query - use the correct field that exists
    query = db.query(HSNCode).filter(
        HSNCode.type == 'HSN',  # Use 'type' field that actually exists
        HSNCode.description.ilike(f"%{q}%")
    )
    
    # Category filter
    if category:
        query = query.filter(HSNCode.category == category)
    
    # Order by relevance and then alphabetically
    products = query.order_by(
        HSNCode.description
    ).limit(limit).all()
    
    print(f"DEBUG: Products found: {len(products)}")
    
    # Convert to product format
    result = []
    for product in products:
        result.append({
            "id": product.id,
            "name": product.description,
            "hsn_code": product.code,
            "gst_rate": product.gst_rate,
            "category": product.category,
            "code_type": "product"
        })
    
    return result


@app.get("/master-products/categories")
async def get_master_product_categories(db: Session = Depends(get_db)):
    """Get all available product categories with full product information"""
    products = db.query(HSNCode).filter(
        HSNCode.type == 'HSN'  # Use type field that actually exists
    ).all()
    
    # Return the products in the format the frontend expects
    return {"categories": [
        {
            "id": str(product.id),
            "name": product.description,  # Use description as name
            "description": product.description,
            "category": product.category,
            "hsn_code": product.code,  # Use code as hsn_code
            "gst_rate": product.gst_rate
        }
        for product in products
    ]}


@app.get("/master-data/search")
async def search_master_data(
    q: str = Query(..., min_length=1, description="Search query"),
    data_type: str | None = Query(None, description="Filter by type: 'service', 'product', or 'all'"),
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(15, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    ENHANCED: Unified search for both services and products
    Now prioritizes SPECIFIC services over generic categories
    """
    q = q.strip()
    print(f"DEBUG: Enhanced search query: {q}, type: {data_type}, category: {category}")
    
    results = []
    
    # Search services if requested
    if data_type in [None, 'all', 'service']:
        # ENHANCED SEARCH LOGIC: Multi-level search for better results
        
        # 1. EXACT MATCH: Search for exact name matches (highest priority)
        exact_matches = db.query(MasterService).filter(
            MasterService.is_active == True,
            func.lower(MasterService.name) == q.lower()
        ).limit(3).all()
        
        # 2. SPECIFIC SERVICES: Search in name and keywords (high priority)
        specific_matches = db.query(MasterService).filter(
            MasterService.is_active == True,
            (func.lower(MasterService.name).like(f"%{q.lower()}%") |
             func.lower(MasterService.keywords).like(f"%{q.lower()}%") |
             func.lower(MasterService.description).like(f"%{q.lower()}%"))
        ).filter(
            # Exclude exact matches to avoid duplicates
            ~MasterService.id.in_([s.id for s in exact_matches])
        ).order_by(
            # Prioritize by relevance: name match > keyword match > usage count
            func.lower(MasterService.name).like(f"%{q.lower()}%").desc(),
            MasterService.usage_count.desc()
        ).limit(limit // 2).all()
        
        # Combine results with exact matches first
        all_service_matches = exact_matches + specific_matches
        
        # Apply category filter if specified
        if category:
            all_service_matches = [s for s in all_service_matches 
                                 if s.category.lower() == category.lower()]
        
        # Convert to response format
        for service in all_service_matches[:limit // 2]:
            # Calculate relevance score for debugging
            relevance_score = 0
            q_lower = q.lower()
            
            if q_lower == service.name.lower():
                relevance_score = 100  # Exact match
            elif q_lower in service.name.lower():
                relevance_score = 80   # Name contains query
            elif service.keywords and q_lower in service.keywords.lower():
                relevance_score = 60   # Keywords contain query
            elif q_lower in service.description.lower():
                relevance_score = 40   # Description contains query
            
            results.append({
                "id": f"service_{service.id}",
                "name": service.name,
                "description": service.description,
                "category": service.category,
                "subcategory": service.subcategory,
                "code": service.sac_code,
                "gst_rate": service.gst_rate,
                "type": "service",
                "usage_count": service.usage_count,
                "relevance_score": relevance_score,  # For debugging
                "keywords": service.keywords  # For debugging
            })
    
    # Search products if requested
    if data_type in [None, 'all', 'product']:
        product_query = db.query(HSNCode).filter(
            HSNCode.type == 'HSN',  # Use type field that actually exists
            HSNCode.description.ilike(f"%{q}%")
        )
        
        if category:
            product_query = product_query.filter(HSNCode.category == category)
        
        products = product_query.order_by(HSNCode.description).limit(limit // 2).all()
        
        for product in products:
            results.append({
                "id": f"product_{product.id}",
                "name": product.description,
                "description": product.description,
                "category": product.category,
                "code": product.code,
                "gst_rate": product.gst_rate,
                "type": "product"
            })
    
    # Sort results by relevance and limit
    results = sorted(results, key=lambda x: (
        x.get('usage_count', 0) if x['type'] == 'service' else 0,
        x['name'].lower()
    ), reverse=True)[:limit]
    
    print(f"DEBUG: Unified search results: {len(results)}")
    return results


@app.get("/master-data/categories")
async def get_master_data_categories(db: Session = Depends(get_db)):
    """Get all available categories for both services and products"""
    # Service categories
    service_categories = db.query(MasterService.category).filter(
        MasterService.is_active == True
    ).distinct().all()
    
    # Product categories
    product_categories = db.query(HSNCode.category).filter(
        HSNCode.type == 'HSN'  # Use type field that actually exists
    ).distinct().all()
    
    return {
        "services": [{"name": cat[0], "display_name": cat[0].replace("_", " ").title()} for cat in service_categories],
        "products": [{"name": cat[0], "display_name": cat[0]} for cat in product_categories]
    }
