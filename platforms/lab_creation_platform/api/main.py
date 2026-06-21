from __future__ import annotations

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from shared.database import init_db, get_db

from api.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_designer_user,
    get_current_researcher_or_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from ssot.api import router as ssot_router
from lab_type.api import router as lab_type_router
# TODO: Add routers for other services as they are implemented
# from logging.api import router as logging_router
# from workflow.api import router as workflow_router
# from instances.api import router as instances_router

# Import models to ensure tables are created
from ssot import models as ssot_models
from lab_type import models as lab_type_models
# TODO: Import other service models as they are created

app = FastAPI(
    title="Lab Creation Platform API",
    description="API for managing computational laboratories following Ciclo de Produção",
    version="0.1.0",
)

# Initialize database tables
@app.on_event("startup")
async def startup_event():
    init_db()

# Include API routers
app.include_router(ssot_router)
app.include_router(lab_type_router)
# TODO: Include other routers as services are implemented
# app.include_router(logging_router)
# app.include_router(workflow_router)
# app.include_router(instances_router)

# Authentication endpoints
@app.post("/token", response_model=dict)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# User information endpoint
@app.get("/users/me/", response_model=dict)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user information."""
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "lab-creation-platform"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Lab Creation Platform API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
"""
Main FastAPI application for the Lab Creation Platform.
"""
from __future__ import annotations

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from shared.database import init_db, get_db
from api.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_designer_user,
    get_current_researcher_or_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from ssot.api import router as ssot_router
from lab_type.api import router as lab_type_router
# TODO: Add routers for other services as they are implemented
# from logging.api import router as logging_router
# from workflow.api import router as workflow_router
# from instances.api import router as instances_router

# Import models to ensure tables are created
from ssot import models as ssot_models
from lab_type import models as lab_type_models
# TODO: Import other service models as they are created

app = FastAPI(
    title="Lab Creation Platform API",
    description="API for managing computational laboratories following Ciclo de Produção",
    version="0.1.0",
)

# Initialize database tables
@app.on_event("startup")
async def startup_event():
    init_db()

# Include API routers
app.include_router(ssot_router)
app.include_router(lab_type_router)
# TODO: Include other routers as services are implemented
# app.include_router(logging_router)
# app.include_router(workflow_router)
# app.include_router(instances_router)

# Authentication endpoints
@app.post("/token", response_model=dict)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# User information endpoint
@app.get("/users/me/", response_model=dict)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user information."""
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "lab-creation-platform"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Lab Creation Platform API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
