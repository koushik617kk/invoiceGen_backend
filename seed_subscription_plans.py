#!/usr/bin/env python3
"""
Script to seed subscription plans in the database
Run this after creating the new tables
"""

from database import SessionLocal, engine
from models import Base, SubscriptionPlan, UserSubscription, SubscriptionPayment
from datetime import datetime

def create_tables():
    """Create all tables including new subscription tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

def seed_subscription_plans():
    """Seed the 2 subscription plans"""
    db = SessionLocal()
    
    try:
        # Check if plans already exist
        existing_plans = db.query(SubscriptionPlan).count()
        if existing_plans > 0:
            print("ℹ️  Subscription plans already exist, skipping...")
            return
        
        # Create Free Trial plan
        free_trial = SubscriptionPlan(
            name="free_trial",
            display_name="Free Trial",
            price_monthly=0.0,
            trial_days=14,
            is_active=True
        )
        
        # Create Paid plan
        paid_plan = SubscriptionPlan(
            name="paid",
            display_name="Paid Plan",
            price_monthly=158.0,
            trial_days=0,
            is_active=True
        )
        
        db.add(free_trial)
        db.add(paid_plan)
        db.commit()
        
        print("✅ Subscription plans seeded successfully!")
        print(f"   - Free Trial: ₹{free_trial.price_monthly} for {free_trial.trial_days} days")
        print(f"   - Paid Plan: ₹{paid_plan.price_monthly}/month")
        
    except Exception as e:
        print(f"❌ Error seeding plans: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Setting up subscription system...")
    create_tables()
    seed_subscription_plans()
    print("🎉 Setup complete!")
