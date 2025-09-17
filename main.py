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
from models import User, BusinessProfile, Customer, Invoice, InvoiceItem, Payment, InvoiceTemplate, LibraryItem, ServiceTemplate, MasterService, HSNCode, CAScheduling, SubscriptionPlan, UserSubscription, SubscriptionPayment

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get frontend URL from environment
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
from admin_auth import verify_admin_credentials, create_admin_session, get_current_admin
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
# from cognito_admin import cognito_admin  # Commented out - file not found
from tax import extract_state_code, compute_totals
from hsn_service import suggest_hsn
from fastapi.responses import StreamingResponse
from pdf_render_modern import render_invoice_pdf
from urllib.parse import quote
from export_handlers import export_complete_invoices, export_hsn_wise_invoices, export_gst_slab_wise_invoices


# ===== SUBSCRIPTION HELPER FUNCTIONS =====

def check_subscription_access(user: User, db: Session) -> bool:
    """Check if user has active subscription (trial or paid)"""
    
    subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user.id,
        UserSubscription.status.in_(["trial", "active"])
    ).first()
    
    if not subscription:
        return False
    
    # Check if trial expired
    if subscription.status == "trial" and subscription.trial_end_date:
        if datetime.now() > subscription.trial_end_date:
            # Mark as expired
            subscription.status = "expired"
            db.commit()
            return False
    
    return True

def get_user_subscription(user: User, db: Session) -> UserSubscription:
    """Get user's current subscription"""
    return db.query(UserSubscription).filter(
        UserSubscription.user_id == user.id,
        UserSubscription.status.in_(["trial", "active"])
    ).first()

def get_days_remaining(subscription: UserSubscription) -> int:
    """Calculate days remaining in trial"""
    if subscription and subscription.status == "trial" and subscription.trial_end_date:
        remaining = (subscription.trial_end_date - datetime.utcnow()).days
        return max(0, remaining)  # Don't return negative
    return None

def check_read_only_access(user: User, db: Session) -> bool:
    """Check if user should have read-only access (trial expired)"""
    subscription = get_user_subscription(user, db)
    if subscription and subscription.status == "expired":
        return True
    return False

def is_trial_expiring_soon(subscription: UserSubscription, days_threshold: int = 3) -> bool:
    """Check if trial is expiring soon"""
    if subscription and subscription.status == "trial":
        days_remaining = get_days_remaining(subscription)
        return days_remaining is not None and days_remaining <= days_threshold
    return False

def give_user_free_trial(user: User, db: Session) -> UserSubscription:
    """Give user a free trial subscription (from first login)"""
    
    # Get free trial plan
    free_trial_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == "free_trial"
    ).first()
    
    if not free_trial_plan:
        raise HTTPException(status_code=500, detail="Free trial plan not found")
    
    # Check if user already has subscription
    existing_sub = db.query(UserSubscription).filter(
        UserSubscription.user_id == user.id
    ).first()
    
    if existing_sub:
        return existing_sub
    
    # Create free trial subscription (trial starts from first login)
    trial_start = datetime.utcnow()  # First login time
    trial_end = trial_start + timedelta(days=14)
    
    subscription = UserSubscription(
        user_id=user.id,
        plan_id=free_trial_plan.id,
        status="trial",
        trial_start_date=trial_start,  # Store trial start date
        trial_end_date=trial_end
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return subscription

def require_subscription(func):
    """Decorator to require active subscription for endpoint access"""
    async def wrapper(*args, **kwargs):
        # Extract current_user and db from kwargs
        current_user = None
        db = None
        
        for key, value in kwargs.items():
            if isinstance(value, User):
                current_user = value
            elif hasattr(value, 'query'):  # Session object
                db = value
        
        if not current_user or not db:
            raise HTTPException(status_code=500, detail="User or database session not found")
        
        # Check subscription access
        if not check_subscription_access(current_user, db):
            subscription = get_user_subscription(current_user, db)
            if subscription and subscription.status == "expired":
                # Trial expired - allow read-only access
                raise HTTPException(
                    status_code=402, 
                    detail={
                        "error": "Trial expired",
                        "message": "Your free trial has expired. Upgrade to continue creating invoices.",
                        "upgrade_required": True,
                        "read_only_mode": True,
                        "plan_price": 158,
                        "days_remaining": 0
                    }
                )
            else:
                # No subscription at all
                raise HTTPException(
                    status_code=402, 
                    detail={
                        "error": "Subscription required",
                        "message": "Please subscribe to access this feature.",
                        "upgrade_required": True,
                        "plan_price": 158
                    }
                )
        
        return await func(*args, **kwargs)
    return wrapper


# Alternative approach: Create a dependency function instead of decorator
async def require_subscription_dependency(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dependency to require active subscription for endpoint access"""
    # Check subscription access
    if not check_subscription_access(current_user, db):
        subscription = get_user_subscription(current_user, db)
        if subscription and subscription.status == "expired":
            # Trial expired - allow read-only access
            raise HTTPException(
                status_code=402, 
                detail={
                    "error": "Trial expired",
                    "message": "Your free trial has expired. Upgrade to continue creating invoices.",
                    "upgrade_required": True,
                    "read_only_mode": True,
                    "plan_price": 158,
                    "days_remaining": 0
                }
            )
        else:
            # No subscription at all
            raise HTTPException(
                status_code=402, 
                detail={
                    "error": "Subscription required",
                    "message": "Please subscribe to access this feature.",
                    "upgrade_required": True,
                    "plan_price": 158
                }
            )
    
    return current_user


Base.metadata.create_all(bind=engine)
run_startup_migrations()

app = FastAPI(title="invoiceGen Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Use environment variable
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
async def create_customer(body: CustomerIn, db: Session = Depends(get_db), current_user: User = Depends(require_subscription_dependency)):
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
    
    # Start with the stored sequence number
    seq = bp.next_invoice_seq or 1
    
    # Keep generating invoice numbers until we find one that doesn't exist
    while True:
        inv_no = f"INV-{date.today().year}-{seq:06d}"
        
        # Check if this invoice number already exists for this user
        existing = db.query(Invoice).filter(
            Invoice.invoice_number == inv_no,
            Invoice.user_id == user_id
        ).first()
        if not existing:
            # Found a unique invoice number, update the sequence and return
            bp.next_invoice_seq = seq + 1
            db.commit()
            return inv_no
        
        # Invoice number exists, try the next one
        seq += 1
        
        # Safety check to prevent infinite loop
        if seq > 999999:
            raise HTTPException(status_code=500, detail="Unable to generate unique invoice number")


@app.post("/invoices", response_model=InvoiceOut)
async def create_invoice(body: InvoiceCreate, db: Session = Depends(get_db), current_user: User = Depends(require_subscription_dependency)):
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

    subtotal, taxable_value, cgst, sgst, igst, total = compute_totals(invoice.items, seller_state, buyer_state)
    invoice.subtotal = subtotal
    invoice.taxable_value = taxable_value
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
async def add_payment(invoice_id: int, body: PaymentIn, db: Session = Depends(get_db), current_user: User = Depends(require_subscription_dependency)):
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

    subtotal, taxable_value, cgst, sgst, igst, total = compute_totals(inv.items, seller_state, buyer_state)
    inv.subtotal = subtotal
    inv.taxable_value = taxable_value
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
async def duplicate_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_subscription_dependency)):
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
    subtotal, taxable_value, cgst, sgst, igst, total = compute_totals(dup.items, src.seller_state_code, src.buyer.state_code)
    dup.subtotal, dup.taxable_value, dup.cgst, dup.sgst, dup.igst, dup.total = subtotal, taxable_value, cgst, sgst, igst, total
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


# ===== SUBSCRIPTION ENDPOINTS =====

@app.get("/subscription/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's subscription status"""
    
    # Give user free trial if they don't have any subscription
    subscription = get_user_subscription(current_user, db)
    if not subscription:
        subscription = give_user_free_trial(current_user, db)
    
    # Check if subscription is active
    is_active = check_subscription_access(current_user, db)
    
    # Calculate days remaining
    days_remaining = get_days_remaining(subscription)
    
    # Check if trial is expiring soon
    is_expiring_soon = is_trial_expiring_soon(subscription, 3)
    
    # Check if user should have read-only access
    is_read_only = check_read_only_access(current_user, db)
    
    return {
        "has_subscription": is_active,
        "plan_name": subscription.plan.display_name if subscription.plan else None,
        "status": subscription.status,
        "trial_start_date": subscription.trial_start_date.isoformat() if subscription.trial_start_date else None,
        "trial_end_date": subscription.trial_end_date.isoformat() if subscription.trial_end_date else None,
        "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
        "days_remaining": days_remaining,
        "is_expiring_soon": is_expiring_soon,
        "is_read_only": is_read_only,
        "upgrade_required": not is_active,
        "plan_price": 158
    }

@app.get("/subscription/plans")
async def get_subscription_plans(db: Session = Depends(get_db)):
    """Get available subscription plans"""
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    
    return [
        {
            "id": plan.id,
            "name": plan.name,
            "display_name": plan.display_name,
            "price_monthly": plan.price_monthly,
            "trial_days": plan.trial_days,
            "currency": "INR"
        }
        for plan in plans
    ]

@app.post("/subscription/select-plan")
async def select_subscription_plan(
    plan_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User selects a subscription plan during registration"""
    
    plan_name = plan_data.get("plan_name")
    if not plan_name:
        raise HTTPException(status_code=400, detail="Plan name is required")
    
    # Get the selected plan
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == plan_name,
        SubscriptionPlan.is_active == True
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Check if user already has subscription
    existing_sub = db.query(UserSubscription).filter(
        UserSubscription.user_id == current_user.id
    ).first()
    
    if existing_sub:
        return {"message": "User already has a subscription", "subscription": existing_sub.plan.display_name}
    
    # Create subscription based on plan
    if plan_name == "free_trial":
        # Give free trial (trial starts from plan selection)
        trial_start = datetime.utcnow()
        trial_end = trial_start + timedelta(days=plan.trial_days)
        subscription = UserSubscription(
            user_id=current_user.id,
            plan_id=plan.id,
            status="trial",
            trial_start_date=trial_start,
            trial_end_date=trial_end
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return {
            "message": "Free trial activated successfully",
            "plan": plan.display_name,
            "trial_start_date": trial_start.isoformat(),
            "trial_end_date": trial_end.isoformat(),
            "days_remaining": plan.trial_days
        }
    
    elif plan_name == "paid":
        # For paid plan, return payment info (we'll integrate payment gateway later)
        return {
            "message": "Payment integration coming soon",
            "plan": plan.display_name,
            "amount": plan.price_monthly,
            "currency": "INR",
            "payment_required": True
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid plan selected")

@app.get("/subscription/manage")
async def get_subscription_management(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get subscription management details"""
    
    subscription = get_user_subscription(current_user, db)
    if not subscription:
        subscription = give_user_free_trial(current_user, db)
    
    days_remaining = get_days_remaining(subscription)
    is_expiring_soon = is_trial_expiring_soon(subscription, 3)
    is_read_only = check_read_only_access(current_user, db)
    
    return {
        "subscription": {
            "plan_name": subscription.plan.display_name if subscription.plan else None,
            "status": subscription.status,
            "trial_start_date": subscription.trial_start_date.isoformat() if subscription.trial_start_date else None,
            "trial_end_date": subscription.trial_end_date.isoformat() if subscription.trial_end_date else None,
            "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
            "days_remaining": days_remaining,
            "is_expiring_soon": is_expiring_soon,
            "is_read_only": is_read_only
        },
        "upgrade_options": {
            "paid_plan_price": 158,
            "currency": "INR"
        },
        "actions": {
            "can_upgrade": subscription.plan.name != "paid",
            "can_cancel": subscription.plan.name == "paid",
            "upgrade_required": not check_subscription_access(current_user, db)
        }
    }

@app.post("/subscription/upgrade")
async def upgrade_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade user to paid plan (redirect to payment gateway)"""
    
    # Check if user already has paid subscription
    subscription = get_user_subscription(current_user, db)
    if subscription and subscription.plan.name == "paid":
        return {"message": "User already has paid subscription"}
    
    # Get paid plan
    paid_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == "paid"
    ).first()
    
    if not paid_plan:
        raise HTTPException(status_code=500, detail="Paid plan not found")
    
    # For now, redirect to dummy payment page (we'll integrate Razorpay later)
    return {
        "message": "Redirecting to payment gateway...",
        "redirect_url": "https://payment-gateway-dummy.com/checkout",  # Dummy URL
        "plan": paid_plan.display_name,
        "amount": paid_plan.price_monthly,
        "currency": "INR",
        "payment_required": True
    }

@app.post("/subscription/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel user's subscription"""
    
    subscription = get_user_subscription(current_user, db)
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    if subscription.plan.name == "free_trial":
        # For free trial, just mark as expired
        subscription.status = "expired"
        db.commit()
        return {"message": "Free trial cancelled"}
    
    elif subscription.plan.name == "paid":
        # For paid plan, mark as cancelled
        subscription.status = "cancelled"
        db.commit()
        return {"message": "Subscription cancelled successfully"}
    
    else:
        raise HTTPException(status_code=400, detail="Cannot cancel this subscription type")


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
        
        # Create service template with template_type field
        template_data = body.model_dump()
        template = ServiceTemplate(
            user_id=current_user.id,
            business_profile_id=bp.id,
            **template_data
        )
        
        print(f"DEBUG: Created template object: {template}")
        print(f"DEBUG: Template type: {template.template_type}")
        
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
                    template_name=service_data['name'],  # NEW: Generic name for template selection
                    description=service_data['description'],  # Specific description for invoice
                    sac_code=service_data['sac_code'],
                    gst_rate=service_data['gst_rate'],
                    unit='Nos',  # Default unit for services
                    base_rate=service_data['base_rate'],
                    template_type='service'  # Set template type for services
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
                    template_name=product.description,  # NEW: Generic name for template selection
                    description=product.description,  # Specific description for invoice (same for products)
                    sac_code=product.code,  # Use HSN code as SAC code for products
                    gst_rate=product.gst_rate,
                    hsn_code=product.code,  # Store the actual HSN code
                    unit='Nos',  # Default unit for products
                    base_rate=1000.0,  # Default base rate for products
                    template_type='product'  # Set template type for products
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


# ============================================================================
# CA SCHEDULING ENDPOINTS
# ============================================================================

@app.get("/ca-scheduling/check-first-invoice")
async def check_first_invoice(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if this is the user's first invoice creation"""
    invoice_count = db.query(Invoice).filter(Invoice.user_id == current_user.id).count()
    
    # Check if user has any CA booking requests
    ca_booking_count = db.query(CAScheduling).filter(CAScheduling.user_id == current_user.id).count()
    has_ca_booking = ca_booking_count > 0
    
    return {
        "is_first_invoice": invoice_count == 0,
        "total_invoices": invoice_count,
        "has_ca_booking": has_ca_booking
    }


@app.post("/ca-scheduling/schedule")
async def schedule_ca_call(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule a CA consultation call"""
    
    # Get user's business profile for pre-filling
    business_profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    
    # Create CA scheduling record
    ca_scheduling = CAScheduling(
        user_id=current_user.id,
        invoice_id=request.get("invoice_id"),
        full_name=request.get("full_name", current_user.full_name or ""),
        phone=request.get("phone", business_profile.phone if business_profile else ""),
        email=request.get("email", current_user.email or ""),
        business_name=request.get("business_name", business_profile.business_name if business_profile else ""),
        business_type=request.get("business_type", current_user.business_type or ""),
        preferred_date=request.get("preferred_date"),
        preferred_time=request.get("preferred_time"),
        user_notes=request.get("user_notes", ""),
        status="pending"
    )
    
    db.add(ca_scheduling)
    db.commit()
    db.refresh(ca_scheduling)
    
    return {
        "id": ca_scheduling.id,
        "status": "pending",
        "message": "CA consultation request submitted successfully! Our CA will contact you within 24 hours.",
        "ca_details": {
            "name": ca_scheduling.ca_name,
            "phone": ca_scheduling.ca_phone,
            "email": ca_scheduling.ca_email
        }
    }


@app.get("/ca-scheduling/my-requests")
async def get_my_ca_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's CA scheduling requests"""
    requests = db.query(CAScheduling).filter(CAScheduling.user_id == current_user.id).order_by(CAScheduling.created_at.desc()).all()
    
    return [
        {
            "id": req.id,
            "status": req.status,
            "preferred_date": req.preferred_date.isoformat() if req.preferred_date else None,
            "preferred_time": req.preferred_time,
            "ca_name": req.ca_name,
            "ca_phone": req.ca_phone,
            "ca_email": req.ca_email,
            "created_at": req.created_at.isoformat(),
            "scheduled_at": req.scheduled_at.isoformat() if req.scheduled_at else None,
            "user_notes": req.user_notes
        }
        for req in requests
    ]


@app.get("/ca-scheduling/available-slots")
async def get_available_slots():
    """Get available CA consultation time slots"""
    # This would typically come from a calendar system
    # For now, return some sample slots
    return {
        "slots": [
            {"date": "2025-09-06", "time": "morning", "available": True},
            {"date": "2025-09-06", "time": "afternoon", "available": True},
            {"date": "2025-09-07", "time": "morning", "available": True},
            {"date": "2025-09-07", "time": "afternoon", "available": True},
            {"date": "2025-09-08", "time": "morning", "available": True},
            {"date": "2025-09-08", "time": "evening", "available": True},
        ],
        "timezone": "IST",
        "ca_info": {
            "name": "CA Rajesh Kumar, ACA",
            "experience": "8+ Years",
            "specialization": "SME GST Compliance",
            "location": "Hyderabad",
            "rating": "4.9/5",
            "businesses_guided": "500+"
        }
    }


# ============================================================================
# CA ADMIN AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/admin/auth/login")
async def admin_login(request: dict):
    """Admin login endpoint"""
    password = request.get("password", "")
    
    if not verify_admin_credentials("admin", password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password"
        )
    
    session_token = create_admin_session()
    
    return {
        "access_token": session_token,
        "token_type": "bearer",
        "message": "Admin authentication successful"
    }

@app.post("/admin/auth/logout")
async def admin_logout(current_admin: str = Depends(get_current_admin)):
    """Admin logout endpoint"""
    # In a real implementation, you'd invalidate the session
    return {"message": "Admin logged out successfully"}

# ============================================================================
# ADMIN DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/admin/users")
async def get_all_users(
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users for admin dashboard"""
    users = db.query(User).all()
    return users

@app.get("/admin/invoices")
async def get_all_invoices(
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all invoices for admin dashboard"""
    invoices = db.query(Invoice).all()
    return invoices

@app.get("/admin/dashboard/stats")
async def get_admin_dashboard_stats(
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for admin panel"""
    now = datetime.utcnow()
    today = now.date()
    thirty_days_ago = now - timedelta(days=30)
    
    # User statistics
    total_users = db.query(User).count()
    active_users_30_days = db.query(User).filter(
        User.last_login >= thirty_days_ago
    ).count()
    new_users_today = db.query(User).filter(
        func.date(User.created_at) == today
    ).count()
    
    # Invoice statistics
    total_invoices = db.query(Invoice).count()
    total_revenue = db.query(func.sum(Invoice.total)).scalar() or 0
    invoices_today = db.query(Invoice).filter(
        func.date(Invoice.created_at) == today
    ).count()
    
    # CA consultation statistics
    total_ca_requests = db.query(CAScheduling).count()
    pending_ca_requests = db.query(CAScheduling).filter(
        CAScheduling.status == 'pending'
    ).count()
    
    # Business types statistics
    business_types = db.query(
        User.business_type,
        func.count(User.id).label('count')
    ).filter(
        User.business_type.isnot(None)
    ).group_by(User.business_type).all()
    
    business_types_list = [
        {"type": bt.business_type, "count": bt.count}
        for bt in business_types
    ]
    
    return {
        "users": {
            "total": total_users,
            "active_30_days": active_users_30_days,
            "new_today": new_users_today
        },
        "invoices": {
            "total": total_invoices,
            "total_revenue": float(total_revenue),
            "created_today": invoices_today
        },
        "ca_consultations": {
            "total_requests": total_ca_requests,
            "pending_requests": pending_ca_requests
        },
        "business_types": business_types_list
    }

# Public endpoints for testing (remove in production)
@app.get("/debug/users")
async def get_debug_users(db: Session = Depends(get_db)):
    """Debug endpoint to get all users (remove in production)"""
    users = db.query(User).all()
    return users

@app.get("/debug/invoices")
async def get_debug_invoices(db: Session = Depends(get_db)):
    """Debug endpoint to get all invoices (remove in production)"""
    invoices = db.query(Invoice).all()
    return invoices

# Admin User Management Endpoints
@app.put("/admin/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: dict,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update user information (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields
    if 'full_name' in user_data:
        user.full_name = user_data['full_name']
    if 'email' in user_data:
        user.email = user_data['email']
    if 'phone' in user_data:
        user.phone = user_data['phone']
    if 'business_type' in user_data:
        user.business_type = user_data['business_type']
    if 'onboarding_completed' in user_data:
        user.onboarding_completed = user_data['onboarding_completed']
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return {"message": "User updated successfully", "user": user}

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete user (Admin only) - Both Local DB and Cognito"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cognito_sub = user.cognito_sub
    user_name = user.full_name or user.email
    
    try:
        # 1. Delete from Cognito first (if cognito_sub exists)
        cognito_deleted = False
        if cognito_sub:
            try:
                cognito_deleted = cognito_admin.delete_user(cognito_sub)
                print(f"✅ Cognito deletion result for {user_name}: {cognito_deleted}")
            except Exception as e:
                print(f"⚠️ Cognito deletion failed for {user_name}: {e}")
                # Continue with local deletion even if Cognito fails
        
        # 2. Delete related data from local database
        db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).delete()
        db.query(Customer).filter(Customer.user_id == user_id).delete()
        db.query(Invoice).filter(Invoice.user_id == user_id).delete()
        
        # 3. Delete user from local database
        db.delete(user)
        db.commit()
        
        return {
            "message": "User deleted successfully",
            "local_db_deleted": True,
            "cognito_deleted": cognito_deleted,
            "user_name": user_name
        }
        
    except Exception as e:
        print(f"❌ Error deleting user {user_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@app.post("/admin/users/{user_id}/contact")
async def contact_user(
    user_id: int,
    contact_data: dict,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Send contact message to user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # In a real implementation, you would send email/SMS here
    # For now, we'll just log the contact attempt
    print(f"Admin contact to user {user.full_name} ({user.email}):")
    print(f"Method: {contact_data.get('method', 'email')}")
    print(f"Message: {contact_data.get('message', '')}")
    
    return {
        "message": "Contact message sent successfully",
        "user": user.full_name,
        "method": contact_data.get('method', 'email')
    }

@app.post("/admin/users/export")
async def export_users(
    export_data: dict,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Export user data (Admin only)"""
    users = db.query(User).all()
    
    # Get business profiles for users
    business_profiles = db.query(BusinessProfile).all()
    bp_dict = {bp.user_id: bp for bp in business_profiles}
    
    # Get invoice counts for users
    invoice_counts = db.query(
        Invoice.user_id,
        func.count(Invoice.id).label('count'),
        func.sum(Invoice.total).label('total_revenue')
    ).group_by(Invoice.user_id).all()
    
    invoice_dict = {ic.user_id: {'count': ic.count, 'revenue': ic.total_revenue or 0} for ic in invoice_counts}
    
    # Prepare export data
    export_users = []
    for user in users:
        user_data = {
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'business_type': user.business_type,
            'onboarding_completed': user.onboarding_completed,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'invoice_count': invoice_dict.get(user.id, {}).get('count', 0),
            'total_revenue': invoice_dict.get(user.id, {}).get('revenue', 0)
        }
        
        # Add business profile if exists
        if user.id in bp_dict:
            bp = bp_dict[user.id]
            user_data.update({
                'business_name': bp.business_name,
                'gstin': bp.gstin,
                'pan': bp.pan,
                'address': bp.address
            })
        
        export_users.append(user_data)
    
    return {
        "message": "Export data prepared successfully",
        "format": export_data.get('format', 'json'),
        "total_users": len(export_users),
        "data": export_users
    }


# New Export Endpoints with Multiple Options
@app.get("/invoices/export/{export_type}")
async def export_invoices_by_type(
    export_type: str,
    status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    customer_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export invoices by type: complete, hsn, or gst-slab"""
    from fastapi.responses import Response
    import csv
    from io import StringIO
    from sqlalchemy import func, case
    
    # Build base query
    qry = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    if status:
        qry = qry.filter(Invoice.status == status.upper())
    if date_from:
        qry = qry.filter(Invoice.date >= date_from)
    if date_to:
        qry = qry.filter(Invoice.date <= date_to)
    if customer_id:
        qry = qry.filter(Invoice.buyer_id == customer_id)
    
    if export_type == "complete":
        return await export_complete_invoices(qry, db)
    elif export_type == "hsn":
        return await export_hsn_wise_invoices(qry, db, current_user.id)
    elif export_type == "gst-slab":
        return await export_gst_slab_wise_invoices(qry, db, current_user.id)
    else:
        raise HTTPException(status_code=400, detail="Invalid export type. Use: complete, hsn, or gst-slab")


# Export functions moved to export_handlers.py module for better organization

# Additional Cognito Management Endpoints
@app.post("/admin/users/{user_id}/enable")
async def enable_user(
    user_id: int,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Enable user in Cognito (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.cognito_sub:
        raise HTTPException(status_code=400, detail="User has no Cognito account")
    
    try:
        success = cognito_admin.enable_user(user.cognito_sub)
        if success:
            return {"message": f"User {user.full_name} enabled successfully in Cognito"}
        else:
            return {"message": f"User {user.full_name} - Cognito operations not available (AWS credentials not configured)", "warning": True}
    except Exception as e:
        return {"message": f"User {user.full_name} - Cognito operations not available: {str(e)}", "warning": True}

@app.post("/admin/users/{user_id}/disable")
async def disable_user(
    user_id: int,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Disable user in Cognito (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.cognito_sub:
        raise HTTPException(status_code=400, detail="User has no Cognito account")
    
    try:
        success = cognito_admin.disable_user(user.cognito_sub)
        if success:
            return {"message": f"User {user.full_name} disabled successfully in Cognito"}
        else:
            return {"message": f"User {user.full_name} - Cognito operations not available (AWS credentials not configured)", "warning": True}
    except Exception as e:
        return {"message": f"User {user.full_name} - Cognito operations not available: {str(e)}", "warning": True}

@app.post("/admin/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reset user password in Cognito (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.cognito_sub:
        raise HTTPException(status_code=400, detail="User has no Cognito account")
    
    try:
        success = cognito_admin.reset_user_password(user.cognito_sub)
        if success:
            return {"message": f"Password reset initiated for user {user.full_name}. Check Cognito console for temporary password."}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset password in Cognito")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting password: {str(e)}")

@app.get("/admin/users/{user_id}/cognito-status")
async def get_user_cognito_status(
    user_id: int,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get user's Cognito account status (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.cognito_sub:
        return {"cognito_status": "No Cognito account", "cognito_sub": None}
    
    try:
        status = cognito_admin.get_user_status(user.cognito_sub)
        return {
            "cognito_status": status or "Unknown",
            "cognito_sub": user.cognito_sub,
            "user_name": user.full_name,
            "user_email": user.email
        }
    except Exception as e:
        return {
            "cognito_status": "Error checking status",
            "cognito_sub": user.cognito_sub,
            "error": str(e)
        }

# CA ADMIN MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/admin/ca-scheduling/requests")
async def get_all_ca_requests(
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all CA scheduling requests (Admin only)"""
    query = db.query(CAScheduling)
    
    if status:
        query = query.filter(CAScheduling.status == status)
    
    total = query.count()
    requests = query.order_by(CAScheduling.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "requests": [
            {
                "id": req.id,
                "user_id": req.user_id,
                "invoice_id": req.invoice_id,
                "full_name": req.full_name,
                "phone": req.phone,
                "email": req.email,
                "business_name": req.business_name,
                "business_type": req.business_type,
                "preferred_date": req.preferred_date.isoformat() if req.preferred_date else None,
                "preferred_time": req.preferred_time,
                "status": req.status,
                "user_notes": req.user_notes,
                "ca_notes": req.ca_notes,
                "created_at": req.created_at.isoformat(),
                "scheduled_at": req.scheduled_at.isoformat() if req.scheduled_at else None,
                "completed_at": req.completed_at.isoformat() if req.completed_at else None,
                "ca_name": req.ca_name,
                "ca_phone": req.ca_phone,
                "ca_email": req.ca_email
            }
            for req in requests
        ],
            "total": total,
        "limit": limit,
        "offset": offset
    }


@app.put("/admin/ca-scheduling/requests/{request_id}/status")
async def update_ca_request_status(
    request_id: int,
    request: dict,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update CA request status (Admin only)"""
    ca_request = db.query(CAScheduling).filter(CAScheduling.id == request_id).first()
    
    if not ca_request:
        return {"error": "CA request not found"}
    
    # Update status
    ca_request.status = request.get("status", ca_request.status)
    ca_request.ca_notes = request.get("ca_notes", ca_request.ca_notes)
    
    # Update timestamps based on status
    if request.get("status") == "scheduled":
        ca_request.scheduled_at = datetime.utcnow()
    elif request.get("status") == "completed":
        ca_request.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ca_request)
    
    return {
        "id": ca_request.id,
        "status": ca_request.status,
        "message": f"CA request status updated to {ca_request.status}",
        "updated_at": ca_request.updated_at.isoformat()
    }


@app.get("/admin/ca-scheduling/stats")
async def get_ca_scheduling_stats(
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get CA scheduling statistics (Admin only)"""
    total_requests = db.query(CAScheduling).count()
    pending_requests = db.query(CAScheduling).filter(CAScheduling.status == "pending").count()
    scheduled_requests = db.query(CAScheduling).filter(CAScheduling.status == "scheduled").count()
    completed_requests = db.query(CAScheduling).filter(CAScheduling.status == "completed").count()
    cancelled_requests = db.query(CAScheduling).filter(CAScheduling.status == "cancelled").count()
    
    # Recent requests (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_requests = db.query(CAScheduling).filter(CAScheduling.created_at >= week_ago).count()
    
    # Business type breakdown
    business_types = db.query(
        CAScheduling.business_type,
        func.count(CAScheduling.id).label('count')
    ).group_by(CAScheduling.business_type).all()
    
    return {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "scheduled_requests": scheduled_requests,
        "completed_requests": completed_requests,
        "cancelled_requests": cancelled_requests,
        "recent_requests": recent_requests,
        "business_type_breakdown": [
            {"type": bt[0] or "Not specified", "count": bt[1]} 
            for bt in business_types
        ]
    }


@app.post("/admin/ca-scheduling/requests/{request_id}/contact")
async def contact_ca_request_user(
    request_id: int,
    request: dict,
    current_admin: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Send contact message to CA request user (Admin only)"""
    ca_request = db.query(CAScheduling).filter(CAScheduling.id == request_id).first()
    
    if not ca_request:
        return {"error": "CA request not found"}
    
    # In a real implementation, this would send email/SMS
    # For now, we'll just log the contact attempt
    contact_message = request.get("message", "")
    contact_method = request.get("method", "email")  # email, sms, call
    
    # Update CA notes with contact attempt
    ca_request.ca_notes = f"{ca_request.ca_notes or ''}\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Contacted via {contact_method}: {contact_message}".strip()
    db.commit()
    
    return {
        "id": ca_request.id,
        "message": f"Contact message sent via {contact_method}",
        "user_phone": ca_request.phone,
        "user_email": ca_request.email,
        "contact_logged": True
    }
