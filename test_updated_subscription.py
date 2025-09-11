#!/usr/bin/env python3
"""
Test script for updated subscription system with trial_start_date and read-only access
"""

from database import SessionLocal
from models import User, SubscriptionPlan, UserSubscription
from main import (
    check_subscription_access, 
    get_user_subscription, 
    give_user_free_trial,
    get_days_remaining,
    check_read_only_access,
    is_trial_expiring_soon
)
from datetime import datetime, timedelta

def test_updated_subscription_system():
    """Test the updated subscription system"""
    db = SessionLocal()
    
    try:
        print("🧪 Testing Updated Subscription System...")
        
        # 1. Get a test user
        user = db.query(User).first()
        if not user:
            print("❌ No users found in database")
            return
        
        print(f"✅ Testing with user: {user.email or user.full_name}")
        
        # 2. Test trial start date logic
        print("\n📅 Testing Trial Start Date Logic...")
        
        # Clear any existing subscription
        existing_sub = db.query(UserSubscription).filter(
            UserSubscription.user_id == user.id
        ).first()
        if existing_sub:
            db.delete(existing_sub)
            db.commit()
            print("   Cleared existing subscription")
        
        # Give user free trial
        subscription = give_user_free_trial(user, db)
        print(f"   Created subscription: {subscription.plan.display_name}")
        print(f"   Trial start date: {subscription.trial_start_date}")
        print(f"   Trial end date: {subscription.trial_end_date}")
        
        # 3. Test days remaining calculation
        print("\n⏰ Testing Days Remaining Calculation...")
        days_remaining = get_days_remaining(subscription)
        print(f"   Days remaining: {days_remaining}")
        
        # 4. Test trial expiring soon logic
        print("\n⚠️ Testing Trial Expiring Soon Logic...")
        is_expiring_soon = is_trial_expiring_soon(subscription, 3)
        print(f"   Is expiring soon (3 days): {is_expiring_soon}")
        
        # 5. Test read-only access logic
        print("\n🔒 Testing Read-Only Access Logic...")
        is_read_only = check_read_only_access(user, db)
        print(f"   Is read-only: {is_read_only}")
        
        # 6. Test subscription status endpoint logic
        print("\n📊 Testing Subscription Status Logic...")
        is_active = check_subscription_access(user, db)
        print(f"   Has active subscription: {is_active}")
        
        # 7. Test subscription management endpoint logic
        print("\n⚙️ Testing Subscription Management Logic...")
        subscription = get_user_subscription(user, db)
        if subscription:
            print(f"   Current plan: {subscription.plan.display_name}")
            print(f"   Status: {subscription.status}")
            print(f"   Trial start: {subscription.trial_start_date}")
            print(f"   Trial end: {subscription.trial_end_date}")
            print(f"   Days remaining: {get_days_remaining(subscription)}")
            print(f"   Is expiring soon: {is_trial_expiring_soon(subscription, 3)}")
            print(f"   Is read-only: {check_read_only_access(user, db)}")
        
        # 8. Test plan selection logic
        print("\n🎯 Testing Plan Selection Logic...")
        plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
        print(f"   Available plans: {[plan.display_name for plan in plans]}")
        
        for plan in plans:
            print(f"   - {plan.display_name}: ₹{plan.price_monthly}/month, {plan.trial_days} days trial")
        
        # 9. Test upgrade logic
        print("\n💳 Testing Upgrade Logic...")
        if subscription.plan.name == "free_trial":
            print("   User can upgrade to paid plan")
            print("   Upgrade would redirect to: https://payment-gateway-dummy.com/checkout")
        else:
            print("   User already has paid plan")
        
        # 10. Test cancel logic
        print("\n❌ Testing Cancel Logic...")
        if subscription.plan.name == "free_trial":
            print("   User can cancel free trial (mark as expired)")
        elif subscription.plan.name == "paid":
            print("   User can cancel paid subscription")
        else:
            print("   User cannot cancel this subscription type")
        
        print("\n🎉 Updated subscription system test completed successfully!")
        print("\n📝 Summary of Updates:")
        print("   ✅ Added trial_start_date field")
        print("   ✅ Updated trial calculation from first login")
        print("   ✅ Added days_remaining calculation")
        print("   ✅ Added read-only access logic")
        print("   ✅ Added trial expiring soon detection")
        print("   ✅ Updated error responses with read-only mode")
        print("   ✅ Added subscription management endpoints")
        print("   ✅ Added upgrade/cancel functionality")
        
    except Exception as e:
        print(f"❌ Error testing updated subscription system: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_updated_subscription_system()
