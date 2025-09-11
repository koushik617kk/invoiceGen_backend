#!/usr/bin/env python3
"""
CA Request Notification System
This script checks for new CA requests and sends notifications
Run this as a cron job every 15 minutes
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
from models import CAScheduling

def check_new_requests():
    """Check for new CA requests and send notifications"""
    db = next(get_db())
    
    try:
        # Get requests from last 15 minutes
        since = datetime.utcnow() - timedelta(minutes=15)
        new_requests = db.query(CAScheduling).filter(
            CAScheduling.created_at >= since,
            CAScheduling.status == 'pending'
        ).all()
        
        if not new_requests:
            print(f"[{datetime.now()}] No new CA requests found")
            return
        
        print(f"[{datetime.now()}] Found {len(new_requests)} new CA requests")
        
        for request in new_requests:
            send_notification(request)
            
    except Exception as e:
        print(f"[{datetime.now()}] Error checking CA requests: {e}")
    finally:
        db.close()

def send_notification(request):
    """Send notification for a CA request"""
    try:
        # In a real implementation, this would send:
        # - Email to CA
        # - SMS to CA
        # - Slack notification
        # - WhatsApp message
        
        print(f"[{datetime.now()}] NEW CA REQUEST:")
        print(f"  ID: {request.id}")
        print(f"  Name: {request.full_name}")
        print(f"  Phone: {request.phone}")
        print(f"  Email: {request.email}")
        print(f"  Business: {request.business_name}")
        print(f"  Type: {request.business_type}")
        print(f"  Preferred Date: {request.preferred_date}")
        print(f"  Preferred Time: {request.preferred_time}")
        print(f"  Notes: {request.user_notes}")
        print(f"  Created: {request.created_at}")
        print("  " + "="*50)
        
        # Here you would add actual notification sending:
        # send_email_notification(request)
        # send_sms_notification(request)
        # send_slack_notification(request)
        
    except Exception as e:
        print(f"[{datetime.now()}] Error sending notification for request {request.id}: {e}")

def send_email_notification(request):
    """Send email notification to CA"""
    # Implementation for email notification
    # Using services like SendGrid, AWS SES, etc.
    pass

def send_sms_notification(request):
    """Send SMS notification to CA"""
    # Implementation for SMS notification
    # Using services like Twilio, AWS SNS, etc.
    pass

def send_slack_notification(request):
    """Send Slack notification"""
    # Implementation for Slack webhook
    pass

if __name__ == "__main__":
    check_new_requests()
