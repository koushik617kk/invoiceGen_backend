from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# Smart environment detection
def get_environment():
    """Detect current environment and load appropriate config"""
    # Check if we're in production based on common indicators
    if os.getenv("ENVIRONMENT") == "production":
        return "production"
    elif "postgresql" in os.getenv("DATABASE_URL", ""):
        return "production"
    elif os.getenv("ENVIRONMENT") == "development":
        return "development"
    else:
        return "development"

# Load environment variables based on detected environment
ENVIRONMENT = get_environment()

if ENVIRONMENT == "production":
    # Load production config
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env.production'))
else:
    # Load development config
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env.development'))

# Fallback to .env if specific environment file doesn't exist
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./invoicegen.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _sqlite_column_exists(conn, table_name: str, column_name: str) -> bool:
    rows = conn.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = {row[1] for row in rows}  # (cid, name, type, notnull, dflt_value, pk)
    return column_name in existing_columns


def _sqlite_table_exists(conn, table_name: str) -> bool:
    rows = conn.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
    return len(rows) > 0


def run_startup_migrations():
    """Minimal, safe, in-place migrations for SQLite during development."""
    if ENVIRONMENT != "development" or not DATABASE_URL.startswith("sqlite"):
        return
    with engine.connect() as conn:
        # invoices.paid_on
        if not _sqlite_column_exists(conn, "invoices", "paid_on"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN paid_on DATE")
        # invoices.status
        if not _sqlite_column_exists(conn, "invoices", "status"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN status VARCHAR DEFAULT 'UNPAID'")
        # invoices.template_id
        if not _sqlite_column_exists(conn, "invoices", "template_id"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN template_id INTEGER")
        # business_profiles new fields
        if not _sqlite_column_exists(conn, "business_profiles", "bank_account_name"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN bank_account_name VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "bank_name"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN bank_name VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "bank_branch"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN bank_branch VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "bank_account_number"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN bank_account_number VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "bank_ifsc"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN bank_ifsc VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "upi_id"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN upi_id VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "default_terms"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN default_terms TEXT")
        if not _sqlite_column_exists(conn, "business_profiles", "accepts_cash"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN accepts_cash VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "cash_note"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN cash_note TEXT")
        
        # Create invoice_templates table if it doesn't exist
        if not _sqlite_table_exists(conn, "invoice_templates"):
            conn.exec_driver_sql("""
                CREATE TABLE invoice_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR NOT NULL,
                    template_file_path VARCHAR,
                    is_default BOOLEAN DEFAULT 0,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
        else:
            # Force recreate invoice_templates table with correct schema
            try:
                # Drop existing table and recreate with correct schema
                conn.exec_driver_sql("DROP TABLE IF EXISTS invoice_templates")
                conn.exec_driver_sql("""
                    CREATE TABLE invoice_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name VARCHAR NOT NULL,
                        template_file_path VARCHAR,
                        is_default BOOLEAN DEFAULT 0,
                        description TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
            except Exception:
                # If anything goes wrong, just continue
                pass
        
        # ===== GST COMPLIANCE MIGRATIONS =====
        
        # BusinessProfile new fields
        if not _sqlite_column_exists(conn, "business_profiles", "pan"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN pan VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "turnover_category"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN turnover_category VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "current_financial_year"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN current_financial_year VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "invoice_prefix"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN invoice_prefix VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "logo_path"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN logo_path VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "signature_path"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN signature_path VARCHAR")
        if not _sqlite_column_exists(conn, "business_profiles", "primary_color"):
            conn.exec_driver_sql("ALTER TABLE business_profiles ADD COLUMN primary_color VARCHAR")
        
        # Invoice new fields
        if not _sqlite_column_exists(conn, "invoices", "financial_year"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN financial_year VARCHAR NOT NULL DEFAULT '2024-25'")
        if not _sqlite_column_exists(conn, "invoices", "seller_pan"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN seller_pan VARCHAR")
        if not _sqlite_column_exists(conn, "invoices", "place_of_supply"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN place_of_supply VARCHAR")
        if not _sqlite_column_exists(conn, "invoices", "place_of_supply_code"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN place_of_supply_code VARCHAR")
        if not _sqlite_column_exists(conn, "invoices", "reverse_charge"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN reverse_charge BOOLEAN DEFAULT 0")
        if not _sqlite_column_exists(conn, "invoices", "ecommerce_gstin"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN ecommerce_gstin VARCHAR")
        if not _sqlite_column_exists(conn, "invoices", "export_type"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN export_type VARCHAR")
        if not _sqlite_column_exists(conn, "invoices", "signature_path"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN signature_path VARCHAR")
        if not _sqlite_column_exists(conn, "invoices", "discount"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN discount FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoices", "taxable_value"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN taxable_value FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoices", "round_off"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN round_off FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoices", "total_in_words"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN total_in_words VARCHAR")
        if not _sqlite_column_exists(conn, "invoices", "terms_and_conditions"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN terms_and_conditions TEXT")
        if not _sqlite_column_exists(conn, "invoices", "notes"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN notes TEXT")
        if not _sqlite_column_exists(conn, "invoices", "updated_at"):
            conn.exec_driver_sql("ALTER TABLE invoices ADD COLUMN updated_at DATETIME")
        
        # InvoiceItem new fields
        if not _sqlite_column_exists(conn, "invoice_items", "sac_code"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN sac_code VARCHAR")
        if not _sqlite_column_exists(conn, "invoice_items", "unit"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN unit VARCHAR")
        if not _sqlite_column_exists(conn, "invoice_items", "discount_percent"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN discount_percent FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "discount_amount"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN discount_amount FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "taxable_value"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN taxable_value FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "cgst_rate"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN cgst_rate FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "cgst_amount"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN cgst_amount FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "sgst_rate"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN sgst_rate FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "sgst_amount"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN sgst_amount FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "igst_rate"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN igst_rate FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "igst_amount"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN igst_amount FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "total_amount"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN total_amount FLOAT DEFAULT 0.0")
        if not _sqlite_column_exists(conn, "invoice_items", "notes"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN notes TEXT")
        if not _sqlite_column_exists(conn, "invoice_items", "created_at"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN created_at DATETIME")
        if not _sqlite_column_exists(conn, "invoice_items", "updated_at"):
            conn.exec_driver_sql("ALTER TABLE invoice_items ADD COLUMN updated_at DATETIME")
        
        # Update existing invoices to have financial year
        conn.exec_driver_sql("""
            UPDATE invoices 
            SET financial_year = '2024-25' 
            WHERE financial_year IS NULL
        """)
        
        # Update existing business profiles to have current financial year
        conn.exec_driver_sql("""
            UPDATE business_profiles 
            SET current_financial_year = '2024-25' 
            WHERE current_financial_year IS NULL
        """)
        
        # Set timestamp values for existing records - only if columns exist
        if _sqlite_column_exists(conn, "invoices", "updated_at"):
            conn.exec_driver_sql("""
                UPDATE invoices 
                SET updated_at = created_at 
                WHERE updated_at IS NULL
            """)
        
        if _sqlite_column_exists(conn, "invoice_items", "created_at"):
            conn.exec_driver_sql("""
                UPDATE invoice_items 
                SET created_at = datetime('now'), updated_at = datetime('now') 
                WHERE created_at IS NULL
            """)
        
        # Create library_items table if it doesn't exist
        if not _sqlite_table_exists(conn, "library_items"):
            conn.exec_driver_sql("""
                CREATE TABLE library_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    description VARCHAR NOT NULL,
                    hsn_code VARCHAR,
                    sac_code VARCHAR,
                    gst_rate FLOAT DEFAULT 0.0,
                    unit VARCHAR DEFAULT 'Nos',
                    category VARCHAR,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
        
        # Add new user fields for onboarding
        if not _sqlite_column_exists(conn, "users", "phone"):
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN phone VARCHAR")
        if not _sqlite_column_exists(conn, "users", "profile_picture"):
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN profile_picture VARCHAR")
        if not _sqlite_column_exists(conn, "users", "onboarding_completed"):
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT 0")
        if not _sqlite_column_exists(conn, "users", "business_type"):
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN business_type VARCHAR")
        if not _sqlite_column_exists(conn, "users", "onboarding_step"):
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN onboarding_step VARCHAR DEFAULT 'business_type'")
        if not _sqlite_column_exists(conn, "users", "updated_at"):
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN updated_at DATETIME")
        if not _sqlite_column_exists(conn, "users", "last_login"):
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN last_login DATETIME")
        
        # Note: New business profile fields are handled in the model but not added to existing tables
        # to maintain backward compatibility. New users will get the full schema.
        
        # Create service_templates table if it doesn't exist
        if not _sqlite_table_exists(conn, "service_templates"):
            conn.exec_driver_sql("""
                CREATE TABLE service_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    business_profile_id INTEGER NOT NULL,
                    description VARCHAR NOT NULL,
                    sac_code VARCHAR NOT NULL,
                    gst_rate FLOAT NOT NULL,
                    hsn_code VARCHAR,
                    unit VARCHAR DEFAULT 'Nos',
                    base_rate FLOAT NOT NULL,
                    currency VARCHAR DEFAULT 'INR',
                    payment_terms VARCHAR DEFAULT 'Net 30 days',
                    min_quantity FLOAT DEFAULT 1.0,
                    max_quantity FLOAT,
                    is_active BOOLEAN DEFAULT 1,
                    is_default BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (business_profile_id) REFERENCES business_profiles (id)
                )
            """)
        
        # Set timestamp values for existing records - only if columns exist
        if _sqlite_column_exists(conn, "users", "updated_at"):
            conn.exec_driver_sql("""
                UPDATE users 
                SET updated_at = created_at 
                WHERE updated_at IS NULL
            """)
        
        # Create master_services table if it doesn't exist
        if not _sqlite_table_exists(conn, "master_services"):
            conn.exec_driver_sql("""
                CREATE TABLE master_services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR NOT NULL,
                    description VARCHAR NOT NULL,
                    sac_code VARCHAR,
                    gst_rate FLOAT DEFAULT 0.0,
                    hsn_code VARCHAR,
                    category VARCHAR,
                    subcategory VARCHAR,
                    business_type VARCHAR,
                    keywords TEXT,
                    tags TEXT,
                    unit VARCHAR DEFAULT 'Nos',
                    is_active BOOLEAN DEFAULT 1,
                    usage_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            # Add missing columns to existing master_services table
            if not _sqlite_column_exists(conn, "master_services", "subcategory"):
                conn.exec_driver_sql("ALTER TABLE master_services ADD COLUMN subcategory VARCHAR")
            if not _sqlite_column_exists(conn, "master_services", "business_type"):
                conn.exec_driver_sql("ALTER TABLE master_services ADD COLUMN business_type VARCHAR")
            if not _sqlite_column_exists(conn, "master_services", "keywords"):
                conn.exec_driver_sql("ALTER TABLE master_services ADD COLUMN keywords TEXT")
            if not _sqlite_column_exists(conn, "master_services", "tags"):
                conn.exec_driver_sql("ALTER TABLE master_services ADD COLUMN tags TEXT")
            if not _sqlite_column_exists(conn, "master_services", "usage_count"):
                conn.exec_driver_sql("ALTER TABLE master_services ADD COLUMN usage_count INTEGER DEFAULT 0")
            if not _sqlite_column_exists(conn, "master_services", "created_at"):
                conn.exec_driver_sql("ALTER TABLE master_services ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            if not _sqlite_column_exists(conn, "master_services", "updated_at"):
                conn.exec_driver_sql("ALTER TABLE master_services ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")

        if _sqlite_column_exists(conn, "business_profiles", "updated_at"):
            conn.exec_driver_sql("""
                UPDATE business_profiles 
                SET updated_at = datetime('now') 
                WHERE updated_at IS NULL
            """)
        
        conn.commit()