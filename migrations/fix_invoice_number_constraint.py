from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///invoicegen.db')

def fix_invoice_number_constraint():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("Fixing invoice number constraint...")
        
        # For SQLite, we need to recreate the table to modify constraints
        # First, check if the old unique constraint exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        # Get table info
        table_info = inspector.get_table_names()
        if 'invoices' in table_info:
            # Get existing indexes
            indexes = inspector.get_indexes('invoices')
            print(f"Existing indexes: {[idx['name'] for idx in indexes]}")
            
            # Check if there are any unique constraints on invoice_number
            unique_indexes = [idx for idx in indexes if idx.get('unique', False)]
            print(f"Unique indexes: {[idx['name'] for idx in unique_indexes]}")
            
            # For SQLite, we need to recreate the table
            # This is a complex operation, so we'll do it step by step
            
            # 1. Create a backup table
            print("Creating backup table...")
            db.execute(text("""
                CREATE TABLE invoices_backup AS 
                SELECT * FROM invoices
            """))
            
            # 2. Drop the original table
            print("Dropping original table...")
            db.execute(text("DROP TABLE invoices"))
            
            # 3. Recreate the table with the new constraint
            print("Recreating table with new constraint...")
            db.execute(text("""
                CREATE TABLE invoices (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    invoice_number VARCHAR NOT NULL,
                    financial_year VARCHAR NOT NULL,
                    date DATE DEFAULT (CURRENT_DATE),
                    due_date DATE,
                    seller_gstin VARCHAR,
                    seller_state_code VARCHAR,
                    seller_pan VARCHAR,
                    buyer_id INTEGER,
                    place_of_supply VARCHAR,
                    place_of_supply_code VARCHAR,
                    reverse_charge BOOLEAN DEFAULT 0,
                    ecommerce_gstin VARCHAR,
                    export_type VARCHAR,
                    template_id INTEGER,
                    signature_path VARCHAR,
                    subtotal FLOAT,
                    discount FLOAT,
                    taxable_value FLOAT,
                    cgst FLOAT,
                    sgst FLOAT,
                    igst FLOAT,
                    total FLOAT,
                    round_off FLOAT,
                    total_in_words VARCHAR,
                    status VARCHAR DEFAULT 'UNPAID',
                    paid_on DATE,
                    terms_and_conditions TEXT,
                    notes TEXT,
                    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
                    updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (buyer_id) REFERENCES customers (id),
                    FOREIGN KEY (template_id) REFERENCES invoice_templates (id),
                    UNIQUE (user_id, invoice_number)
                )
            """))
            
            # 4. Copy data back
            print("Copying data back...")
            db.execute(text("""
                INSERT INTO invoices 
                SELECT * FROM invoices_backup
            """))
            
            # 5. Drop backup table
            print("Dropping backup table...")
            db.execute(text("DROP TABLE invoices_backup"))
            
            # 6. Create indexes
            print("Creating indexes...")
            db.execute(text("CREATE INDEX ix_invoices_id ON invoices (id)"))
            db.execute(text("CREATE INDEX ix_invoices_user_id ON invoices (user_id)"))
            db.execute(text("CREATE INDEX ix_invoices_invoice_number ON invoices (invoice_number)"))
            
            db.commit()
            print("✅ Invoice number constraint fixed successfully!")
            print("✅ Now invoice numbers are unique per user, not globally unique.")
            
        else:
            print("❌ Invoices table not found!")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
        print("The database may be in an inconsistent state. Please check manually.")
    finally:
        db.close()

if __name__ == "__main__":
    fix_invoice_number_constraint()
