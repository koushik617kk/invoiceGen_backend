from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Date, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

try:
    from database import Base
except ImportError:
    from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    cognito_sub = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    
    # Onboarding Status
    onboarding_completed = Column(Boolean, default=False)
    business_type = Column(String, nullable=True)  # 'service', 'product', 'mixed'
    onboarding_step = Column(String, default='business_type')  # Current step
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    business_profile = relationship("BusinessProfile", uselist=False, back_populates="owner")
    invoice_templates = relationship("InvoiceTemplate", back_populates="user", cascade="all, delete-orphan")
    library_items = relationship("LibraryItem", back_populates="user", cascade="all, delete-orphan")
    service_templates = relationship("ServiceTemplate", back_populates="user", cascade="all, delete-orphan")


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String, nullable=True)
    gstin = Column(String, index=True, nullable=True)
    pan = Column(String, nullable=True)  # PAN number
    address = Column(Text, nullable=True)
    state_code = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Business Category (for HSN/SAC code digits)
    turnover_category = Column(String, nullable=True)  # '5cr_plus' or 'below_5cr'
    
    # Invoice Sequence Management
    current_financial_year = Column(String, nullable=True)  # e.g., "2024-25"
    next_invoice_seq = Column(Integer, default=1)
    invoice_prefix = Column(String, nullable=True)  # Custom prefix for invoice numbers
    
    # Branding
    logo_path = Column(String, nullable=True)
    signature_path = Column(String, nullable=True)
    primary_color = Column(String, nullable=True)  # Hex color code
    
    # Payment details (optional)
    bank_account_name = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    bank_branch = Column(String, nullable=True)
    bank_account_number = Column(String, nullable=True)
    bank_ifsc = Column(String, nullable=True)
    upi_id = Column(String, nullable=True)
    default_terms = Column(Text, nullable=True)
    accepts_cash = Column(String, nullable=True)  # 'YES' or 'NO'
    cash_note = Column(Text, nullable=True)

    owner = relationship("User", back_populates="business_profile")
    service_templates = relationship("ServiceTemplate", back_populates="business_profile", cascade="all, delete-orphan")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    gstin = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    state_code = Column(String, nullable=True)

    invoices = relationship("Invoice", back_populates="buyer")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Invoice Identification
    invoice_number = Column(String, index=True, nullable=False)
    financial_year = Column(String, nullable=False)  # e.g., "2024-25"
    date = Column(Date, default=date.today)
    due_date = Column(Date, nullable=True)

    # Seller Details
    seller_gstin = Column(String, nullable=True)
    seller_state_code = Column(String, nullable=True)
    seller_pan = Column(String, nullable=True)

    # Buyer Details
    buyer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    place_of_supply = Column(String, nullable=True)  # State name for place of supply
    place_of_supply_code = Column(String, nullable=True)  # State code for place of supply

    # GST Details
    reverse_charge = Column(Boolean, default=False)
    ecommerce_gstin = Column(String, nullable=True)  # For e-commerce supplies
    export_type = Column(String, nullable=True)  # 'WITH_PAYMENT' or 'WITHOUT_PAYMENT'

    # Template & Signature
    template_id = Column(Integer, ForeignKey("invoice_templates.id"), nullable=True)
    signature_path = Column(String, nullable=True)  # Specific signature for this invoice
    
    # Amounts
    subtotal = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    taxable_value = Column(Float, default=0.0)  # After discount, before tax
    cgst = Column(Float, default=0.0)
    sgst = Column(Float, default=0.0)
    igst = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    round_off = Column(Float, default=0.0)  # Rounding adjustment
    total_in_words = Column(String, nullable=True)  # Total amount in words
    
    # Status
    status = Column(String, default="UNPAID")
    paid_on = Column(Date, nullable=True)
    
    # Notes
    terms_and_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)  # Additional notes/remarks
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    buyer = relationship("Customer", back_populates="invoices")
    template = relationship("InvoiceTemplate")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    
    # Composite unique constraint: invoice_number must be unique per user
    __table_args__ = (
        UniqueConstraint('user_id', 'invoice_number', name='uq_user_invoice_number'),
    )


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    
    # Item Details
    description = Column(String, nullable=False)
    hsn_code = Column(String, nullable=True)  # HSN code for goods
    sac_code = Column(String, nullable=True)  # SAC code for services
    
    # Quantity & Unit
    quantity = Column(Float, default=1.0)
    unit = Column(String, nullable=True)  # e.g., Nos, Kg, Meters
    rate = Column(Float, default=0.0)  # Rate per unit
    
    # Discounts
    discount_percent = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    
    # Tax Details
    taxable_value = Column(Float, default=0.0)  # After discount, before tax
    gst_rate = Column(Float, default=0.0)  # GST percentage
    cgst_rate = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_rate = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_rate = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    
    # Totals
    amount = Column(Float, default=0.0)  # Before tax
    tax_amount = Column(Float, default=0.0)  # Total tax
    total_amount = Column(Float, default=0.0)  # Including tax
    
    # Additional Info
    notes = Column(Text, nullable=True)  # Item-specific notes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, nullable=False)  # CASH | BANK | UPI | OTHER
    date = Column(Date, default=date.today, nullable=False)
    ref = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="payments")


class InvoiceTemplate(Base):
    __tablename__ = "invoice_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "Default", "Electrical", "Construction"
    template_file_path = Column(String, nullable=True)  # Path to uploaded PDF template (optional initially)
    is_default = Column(Boolean, default=False)  # Default template for user
    description = Column(Text, nullable=True)  # Optional description
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="invoice_templates")
    
    def __repr__(self):
        return f"<InvoiceTemplate(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class LibraryItem(Base):
    __tablename__ = "library_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Item Details
    description = Column(String, nullable=False)
    hsn_code = Column(String, nullable=True)  # HSN code for goods
    sac_code = Column(String, nullable=True)  # SAC code for services
    gst_rate = Column(Float, default=0.0)  # GST percentage
    unit = Column(String, nullable=True)  # e.g., Nos, Kg, Meters, Hours, Days, Pieces
    category = Column(String, nullable=True)  # e.g., Electronics, Furniture, Services
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="library_items")
    
    def __repr__(self):
        return f"<LibraryItem(id={self.id}, description='{self.description}', user_id={self.user_id})>"


class ServiceTemplate(Base):
    __tablename__ = "service_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=False)
    
    # Service Details - Aligned with InvoiceItem
    template_name = Column(String, nullable=False)  # NEW: Generic name for template selection
    description = Column(String, nullable=False)  # Specific description for invoice
    sac_code = Column(String, nullable=False)
    gst_rate = Column(Float, nullable=False)
    hsn_code = Column(String, nullable=True)  # Added for goods later
    unit = Column(String, default="Nos")  # Added default unit
    
    # Template Type - NEW FIELD
    template_type = Column(String, default="service")  # "service" or "product"
    
    # Pricing
    base_rate = Column(Float, nullable=False)  # This will be the default rate
    currency = Column(String, default="INR")
    
    # Business Rules
    payment_terms = Column(String, default="Net 30 days")
    min_quantity = Column(Float, default=1.0)
    max_quantity = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="service_templates")
    business_profile = relationship("BusinessProfile", back_populates="service_templates")
    
    def __repr__(self):
        return f"<ServiceTemplate(id={self.id}, description='{self.description}', user_id={self.user_id})>"


class MasterService(Base):
    __tablename__ = "master_services"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Service Details
    name = Column(String, nullable=False)  # Display name for selection
    description = Column(String, nullable=False)  # Full description for invoices
    sac_code = Column(String, nullable=False)  # Service Accounting Code
    gst_rate = Column(Float, nullable=False)  # GST percentage
    hsn_code = Column(String, nullable=True)  # For hybrid service-goods
    
    # Classification
    category = Column(String, nullable=False)  # IT, Professional, Creative, etc.
    subcategory = Column(String, nullable=True)  # Web Development, Design, etc.
    business_type = Column(String, nullable=True)  # service, product, both
    
    # Search & Discovery
    keywords = Column(Text, nullable=True)  # Comma-separated search keywords
    tags = Column(Text, nullable=True)  # Additional tags for filtering
    
    # Metadata
    unit = Column(String, default="Nos")  # Default unit
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)  # Track popularity
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<MasterService(id={self.id}, name='{self.name}', category='{self.category}')>"


class HSNCode(Base):
    __tablename__ = "hsn_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Code Details
    code = Column(String, nullable=False, unique=True, index=True)  # HSN/SAC code
    description = Column(String, nullable=False)  # User-friendly description
    gst_rate = Column(Float, nullable=False)  # GST percentage
    type = Column(String, nullable=False)  # "HSN" or "SAC"
    
    # Category Classification
    category = Column(String, nullable=True)  # Electronics, Clothing, Food, etc.
    subcategory = Column(String, nullable=True)  # Computers, Smartphones, etc.
    
    # Search & Discovery
    keywords = Column(Text, nullable=True)  # Comma-separated search keywords
    tags = Column(Text, nullable=True)  # Additional tags
    
    # Business Context
    unit = Column(String, default="Nos")  # Default unit
    business_type = Column(String, nullable=True)  # B2B, B2C, both
    
    # Metadata
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)  # Track popularity
    source = Column(String, nullable=True)  # Source of data (manual, scraped, etc.)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<HSNCode(code='{self.code}', description='{self.description}', gst={self.gst_rate}%)>"
