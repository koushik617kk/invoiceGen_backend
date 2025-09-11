"""
Simple Admin Authentication System
Internal admin authentication (not using Cognito)
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

# Admin credentials (in production, store these in environment variables)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "sha256$" + hashlib.sha256("AdminPass2025!".encode()).hexdigest()
ADMIN_SESSION_DURATION = timedelta(hours=8)  # 8 hours session

# Simple in-memory session storage (use Redis in production)
admin_sessions = {}

security = HTTPBearer()

def verify_admin_credentials(username: str, password: str) -> bool:
    """Verify admin username and password"""
    if username != ADMIN_USERNAME:
        return False
    
    password_hash = "sha256$" + hashlib.sha256(password.encode()).hexdigest()
    return password_hash == ADMIN_PASSWORD_HASH

def create_admin_session() -> str:
    """Create a new admin session"""
    session_token = secrets.token_urlsafe(32)
    admin_sessions[session_token] = {
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + ADMIN_SESSION_DURATION,
        "username": ADMIN_USERNAME
    }
    return session_token

def verify_admin_session(session_token: str) -> bool:
    """Verify admin session is valid"""
    if session_token not in admin_sessions:
        return False
    
    session = admin_sessions[session_token]
    if datetime.utcnow() > session["expires_at"]:
        # Session expired, remove it
        del admin_sessions[session_token]
        return False
    
    return True

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current authenticated admin"""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    
    if not verify_admin_session(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin session"
        )
    
    return credentials.credentials

def cleanup_expired_sessions():
    """Clean up expired sessions (call this periodically)"""
    now = datetime.utcnow()
    expired_sessions = [
        token for token, session in admin_sessions.items()
        if now > session["expires_at"]
    ]
    for token in expired_sessions:
        del admin_sessions[token]
