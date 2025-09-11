from sqlalchemy import create_engine, text
import os

# Define the database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///invoicegen.db")

def fix_template_name_nulls():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Check if there are any NULL template_name values
            result = conn.execute(text("SELECT COUNT(*) FROM service_templates WHERE template_name IS NULL"))
            null_count = result.scalar()
            
            if null_count > 0:
                print(f"Found {null_count} templates with NULL template_name. Fixing...")
                
                # Update NULL template_name values to use description
                conn.execute(text("UPDATE service_templates SET template_name = description WHERE template_name IS NULL"))
                conn.commit()
                
                print(f"✅ Fixed {null_count} templates. template_name now populated.")
            else:
                print("✅ No NULL template_name values found. Database is clean.")
                
        except Exception as e:
            print(f"❌ Error fixing template_name NULLs: {e}")
            conn.rollback()

if __name__ == "__main__":
    fix_template_name_nulls()
