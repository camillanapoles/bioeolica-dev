"""
Authentication and authorization module.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..db.models import Simulation, Material  # Example models; we may have a User model later
from ..db.repository import SimulationRepository, MaterialRepository

# To be set via environment variables
SECRET_KEY = "your-secret-key-here"  # In production, load from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# TODO: In a real system, we would have a User table and credentials.
# For now, we'll simulate a simple admin/user distinction based on a header or a fake token.
# We'll create a fake user database for demonstration.
FAKE_USERS = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("adminpass"),
        "role": "admin",
        "disabled": False,
    },
    "researcher": {
        "username": "researcher",
        "full_name": "Researcher",
        "email": "researcher@example.com",
        "hashed_password": pwd_context.hash("researchpass"),
        "role": "researcher",
        "disabled": False,
    },
    "visitor": {
        "username": "visitor",
        "full_name": "Visitor",
        "email": "visitor@example.com",
        "hashed_password": pwd_context.hash("visitorpass"),
        "role": "visitor",
        "disabled": False,
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[dict]:
    if username in FAKE_USERS:
        user_dict = FAKE_USERS[username]
        return user_dict
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # We could also fetch the user from DB, but we use fake users for now.
        token_data = {"username": username}
    except JWTError:
        raise credentials_exception
    user = get_user(username if token_data.get("username") else "")
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(current_user: dict = Depends(get_current_active_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

def get_current_researcher_or_admin_user(current_user: dict = Depends(get_current_active_user)):
    if current_user.get("role") not in ["researcher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

# Example dependency for endpoints that require at least researcher
get_current_researcher_user = get_current_researcher_or_admin_user

# We'll also create a simple login endpoint in the main API router.
