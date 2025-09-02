from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    
    # Onboarding Status
    onboarding_completed: bool
    business_type: Optional[str] = None
    onboarding_step: str
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class BusinessProfileIn(BaseModel):
    business_name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    state_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    
    # Business Category
    turnover_category: Optional[str] = None  # '5cr_plus' or 'below_5cr'
    
    # Invoice Management
    current_financial_year: Optional[str] = None  # e.g., "2024-25"
    invoice_prefix: Optional[str] = None  # Custom prefix for invoice numbers
    
    # Branding
    logo_path: Optional[str] = None
    signature_path: Optional[str] = None
    primary_color: Optional[str] = None  # Hex color code
    
    # Payment details
    bank_account_name: Optional[str] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc: Optional[str] = None
    upi_id: Optional[str] = None
    default_terms: Optional[str] = None
    accepts_cash: Optional[str] = None
    cash_note: Optional[str] = None


class BusinessProfileOut(BusinessProfileIn):
    id: int

    class Config:
        from_attributes = True


class CustomerIn(BaseModel):
    name: str
    gstin: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    state_code: Optional[str] = None


class CustomerOut(CustomerIn):
    id: int

    class Config:
        from_attributes = True


class InvoiceItemIn(BaseModel):
    description: str
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None  # SAC code for services
    quantity: float
    unit: Optional[str] = None  # e.g., Nos, Kg, Meters
    rate: float
    
    # Discounts
    discount_percent: Optional[float] = 0.0
    discount_amount: Optional[float] = 0.0
    
    # Tax
    gst_rate: float


class InvoiceCreate(BaseModel):
    buyer_id: int
    date: Optional[str] = None        # Accept date strings like "2025-08-14"
    due_date: Optional[str] = None    # Accept date strings like "2025-08-23"
    items: List[InvoiceItemIn]
    
    # GST Details
    reverse_charge: Optional[bool] = False
    ecommerce_gstin: Optional[str] = None
    export_type: Optional[str] = None  # 'WITH_PAYMENT' or 'WITHOUT_PAYMENT'
    
    # Additional fields
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    template_id: Optional[int] = None  # ID of the template to use (optional)


class InvoiceItemOut(InvoiceItemIn):
    id: int
    
    # Calculated amounts
    amount: float  # Before tax
    tax_amount: float  # Total tax
    total_amount: float  # Including tax
    
    # Tax breakdown
    taxable_value: float  # After discount, before tax
    cgst_rate: float
    cgst_amount: float
    sgst_rate: float
    sgst_amount: float
    igst_rate: float
    igst_amount: float
    
    # Additional fields
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    financial_year: str
    date: date
    due_date: Optional[date]
    
    # Buyer and Supply Details
    buyer: CustomerOut
    place_of_supply: Optional[str] = None
    place_of_supply_code: Optional[str] = None
    
    # GST Details
    reverse_charge: bool
    ecommerce_gstin: Optional[str] = None
    export_type: Optional[str] = None
    
    # Items and Amounts
    items: List[InvoiceItemOut]
    subtotal: float
    discount: float
    taxable_value: float  # After discount, before tax
    cgst: float
    sgst: float
    igst: float
    total: float
    round_off: float
    total_in_words: Optional[str] = None
    
    # Status and Payment
    status: str
    paid_on: Optional[date]
    
    # Template and Additional Info
    template_id: Optional[int] = None
    template_name: Optional[str] = None
    signature_path: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentIn(BaseModel):
    amount: float
    method: str
    # Accept date as an optional ISO string (YYYY-MM-DD) to avoid client parsing issues
    date: Optional[str] = None
    ref: Optional[str] = None
    note: Optional[str] = None


class PaymentOut(BaseModel):
    id: int
    amount: float
    method: str
    date: date
    ref: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None


class InvoiceTemplateCreate(InvoiceTemplateBase):
    pass


class InvoiceTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None


class InvoiceTemplateOut(InvoiceTemplateBase):
    id: int
    user_id: int
    template_file_path: Optional[str] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LibraryItemIn(BaseModel):
    description: str
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None
    gst_rate: float = 0.0
    unit: Optional[str] = "Nos"
    category: Optional[str] = None
    is_active: bool = True


class LibraryItemOut(BaseModel):
    id: int
    description: str
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None
    gst_rate: float
    unit: Optional[str] = None
    category: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceTemplateIn(BaseModel):
    description: str
    sac_code: str
    gst_rate: float
    hsn_code: Optional[str] = None
    unit: str = "Nos"
    base_rate: float
    currency: str = "INR"
    payment_terms: str = "Net 30 days"
    min_quantity: float = 1.0
    max_quantity: Optional[float] = None
    is_active: bool = True
    is_default: bool = False


class ServiceTemplateOut(BaseModel):
    id: int
    user_id: int
    business_profile_id: int
    description: str
    sac_code: str
    gst_rate: float
    hsn_code: Optional[str] = None
    unit: str
    base_rate: float
    currency: str
    payment_terms: str
    min_quantity: float
    max_quantity: Optional[float] = None
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceTemplateUpdate(BaseModel):
    description: Optional[str] = None
    sac_code: Optional[str] = None
    gst_rate: Optional[float] = None
    hsn_code: Optional[str] = None
    unit: Optional[str] = None
    base_rate: Optional[float] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None
    min_quantity: Optional[float] = None
    max_quantity: Optional[float] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


# Master Services Schemas
class MasterServiceOut(BaseModel):
    id: int
    name: str
    description: str
    sac_code: str
    gst_rate: float
    hsn_code: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    business_type: Optional[str] = None
    keywords: Optional[str] = None
    tags: Optional[str] = None
    unit: str
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MasterServiceSearch(BaseModel):
    query: str
    category: Optional[str] = None
    business_type: Optional[str] = None
    limit: int = 10


class BusinessProfileCreate(BaseModel):
    business_name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    state_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    turnover_category: Optional[str] = None
    employee_count: Optional[str] = None
    current_financial_year: Optional[str] = None
    invoice_prefix: Optional[str] = None
    logo_path: Optional[str] = None
    signature_path: Optional[str] = None
    primary_color: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc: Optional[str] = None
    upi_id: Optional[str] = None
    default_terms: Optional[str] = None
    accepts_cash: Optional[str] = None
    cash_note: Optional[str] = None


class UserOnboardingUpdate(BaseModel):
    business_type: Optional[str] = None
    onboarding_step: Optional[str] = None
    onboarding_completed: Optional[bool] = None
