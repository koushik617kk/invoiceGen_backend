#!/usr/bin/env python3
"""
Test script for subscription functionality
"""

from database import SessionLocal
from models import User, SubscriptionPlan, UserSubscription
from main import check_subscription_access, get_user_subscription, give_user_free_trial
from datetime import datetime, timedelta

def test_subscription_system():
    """Test the subscription system"""
    db = SessionLocal()
    
    try:
        print("🧪 Testing Subscription System...")
        
        # 1. Check if subscription plans exist
        plans = db.query(SubscriptionPlan).all()
        print(f"✅ Found {len(plans)} subscription plans:")
        for plan in plans:
            print(f"   - {plan.display_name}: ₹{plan.price_monthly}/month")
        
        # 2. Check if we have any users
        users = db.query(User).limit(3).all()
        print(f"✅ Found {len(users)} users in database")
        
        if users:
            # 3. Test subscription functions with first user
            test_user = users[0]
            print(f"   Testing with user: {test_user.email or test_user.full_name}")
            
            # Check current subscription
            subscription = get_user_subscription(test_user, db)
            if subscription:
                print(f"   Current subscription: {subscription.plan.display_name} ({subscription.status})")
            else:
                print("   No subscription found, giving free trial...")
                subscription = give_user_free_trial(test_user, db)
                print(f"   Created subscription: {subscription.plan.display_name} ({subscription.status})")
            
            # Check access
            has_access = check_subscription_access(test_user, db)
            print(f"   Has access: {has_access}")
            
            # Test subscription status endpoint logic
            is_active = check_subscription_access(test_user, db)
            days_remaining = None
            if subscription.trial_end_date and subscription.status == "trial":
                days_remaining = (subscription.trial_end_date - datetime.now()).days
            
            print(f"   Subscription Status:")
            print(f"     - Active: {is_active}")
            print(f"     - Plan: {subscription.plan.display_name if subscription.plan else None}")
            print(f"     - Status: {subscription.status}")
            print(f"     - Trial End: {subscription.trial_end_date}")
            print(f"     - Days Remaining: {days_remaining}")
        
        print("🎉 Subscription system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing subscription system: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_subscription_system()
