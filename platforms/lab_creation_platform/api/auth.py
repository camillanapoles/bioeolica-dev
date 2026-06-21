"""
Authentication and authorization module for Lab Creation Platform.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

# To be set via environment variables
SECRET_KEY = "your-secret-key-here"  # In production, load from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake user database for demonstration
# In a real system, this would be backed by a proper User table in the database
FAKE_USERS = {
    "admin": {
        "username": "admin",
        "full_name": "Platform Administrator",
        "email": "admin@labplatform.example.com",
        "hashed_password": pwd_context.hash("adminpass"),
        "role": "admin",
        "disabled": False,
    },
    "designer": {
        "username": "designer",
        "full_name": "Lab Type Designer",
        "email": "designer@labplatform.example.com",
        "hashed_password": pwd_context.hash("designerpass"),
        "role": "designer",
        "disabled": False,
    },
    "researcher": {
        "username": "researcher",
        "full_name": "Lab Researcher",
        "email": "researcher@labplatform.example.com",
        "hashed_password": pwd_context.hash("researchpass"),
        "role": "researcher",
        "disabled": False,
    },
    "student": {
        "username": "student",
        "full_name": "Lab Student",
        "email": "student@labplatform.example.com",
        "hashed_password": pwd_context.hash("studentpass"),
        "role": "student",
        "disabled": False,
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[dict]:
    """Get user by username from fake user database."""
    if username in FAKE_USERS:
        return FAKE_USERS[username]
    return None


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user."""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get the current authenticated user."""
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
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get the current active user."""
    if current_user.get("disabled"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def get_current_designer_user(
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    """Get the current user if they are a designer or admin."""
    if current_user["role"] not in ["designer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_researcher_or_admin_user(
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    """Get the current user if they are researcher, designer, or admin."""
    if current_user["role"] not in ["researcher", "designer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
