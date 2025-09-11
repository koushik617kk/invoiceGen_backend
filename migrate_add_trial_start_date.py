#!/usr/bin/env python3
"""
Migration script to add trial_start_date column to user_subscriptions table
"""

from database import SessionLocal, engine
from models import UserSubscription
from sqlalchemy import text
from datetime import datetime, timedelta

def migrate_add_trial_start_date():
    """Add trial_start_date column to user_subscriptions table"""
    db = SessionLocal()
    
    try:
        print("🔄 Starting migration: Add trial_start_date column...")
        
        # Check if column already exists (PostgreSQL)
        result = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.columns 
            WHERE table_name = 'user_subscriptions' 
            AND column_name = 'trial_start_date'
        """)).fetchone()
        
        if result[0] > 0:
            print("✅ Column trial_start_date already exists, skipping migration")
            return
        
        # Add the new column (PostgreSQL)
        db.execute(text("""
            ALTER TABLE user_subscriptions 
            ADD COLUMN trial_start_date TIMESTAMP
        """))
        
        db.commit()
        print("✅ Added trial_start_date column successfully")
        
        # Update existing records to set trial_start_date based on created_at
        print("🔄 Updating existing records...")
        existing_subscriptions = db.query(UserSubscription).filter(
            UserSubscription.trial_start_date.is_(None)
        ).all()
        
        for subscription in existing_subscriptions:
            if subscription.status == "trial":
                # Set trial_start_date to created_at for existing trial subscriptions
                subscription.trial_start_date = subscription.created_at
                print(f"   Updated subscription {subscription.id}: trial_start_date = {subscription.created_at}")
        
        db.commit()
        print(f"✅ Updated {len(existing_subscriptions)} existing subscriptions")
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_add_trial_start_date()
