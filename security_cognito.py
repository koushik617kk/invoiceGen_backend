from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import httpx
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import os

from database import get_db
from models import User
from sqlalchemy.orm import Session
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Load environment variables from .env files if present
# 1) Project root .env
load_dotenv(find_dotenv(), override=False)
# 2) Backend-local .env (invoiceGen_backend/.env)
backend_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(backend_env_path, override=False)


COGNITO_REGION = os.getenv("COGNITO_REGION")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")
DEV_AUTH_BYPASS = os.getenv("DEV_AUTH_BYPASS", "").lower() in {"1", "true", "yes"}

if not (COGNITO_REGION and COGNITO_USER_POOL_ID and COGNITO_APP_CLIENT_ID) and not DEV_AUTH_BYPASS:
    raise RuntimeError("Missing Cognito env vars: COGNITO_REGION, COGNITO_USER_POOL_ID, COGNITO_APP_CLIENT_ID")

ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

_jwks_cache: Dict[str, Any] = {"keys": None, "ts": None}


async def get_jwks() -> Dict[str, Any]:
    now = datetime.utcnow()
    if _jwks_cache["keys"] and _jwks_cache["ts"] and now - _jwks_cache["ts"] < timedelta(hours=12):
        return _jwks_cache["keys"]
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(JWKS_URL)
        resp.raise_for_status()
        data = resp.json()
        _jwks_cache["keys"] = data
        _jwks_cache["ts"] = now
        return data


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    # Local/dev bypass to keep working when Cognito is unreachable
    if DEV_AUTH_BYPASS:
        user = db.query(User).filter(User.cognito_sub == "dev-sub").first()
        if not user:
            user = User(cognito_sub="dev-sub", email="dev@example.com", full_name="Dev User")
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    token = creds.credentials
    unverified = jwt.get_unverified_header(token)
    kid = unverified.get("kid")
    jwks = await get_jwks()
    key = None
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            key = k
            break
    if key is None:
        raise HTTPException(status_code=401, detail="Invalid token key")

    try:
        decoded = jwt.decode(
            token,
            key,
            audience=COGNITO_APP_CLIENT_ID,
            issuer=ISSUER,
            options={"verify_at_hash": False},
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token invalid: {str(e)}")

    # Ensure token_use is id or access
    token_use = decoded.get("token_use")
    if token_use not in {"id", "access"}:
        raise HTTPException(status_code=401, detail="Invalid token use")

    sub = decoded.get("sub")
    email = decoded.get("email")
    name = decoded.get("name") or decoded.get("cognito:username")

    user = db.query(User).filter(User.cognito_sub == sub).first()
    if not user:
        user = User(cognito_sub=sub, email=email, full_name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
