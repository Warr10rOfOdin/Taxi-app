"""
Main API entry point - FastAPI with authentication and database
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, engine
import models
import schemas
import auth

# Create FastAPI app
app = FastAPI(title="Voss Taxi Web App API", version="1.0.0")

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"✓ Main API initialized with CORS: {ALLOWED_ORIGINS}", file=sys.stderr)

# Initialize database tables
try:
    models.Base.metadata.create_all(bind=engine)
    print(f"✓ Database tables ensured", file=sys.stderr)
except Exception as e:
    print(f"⚠ Database init warning: {e}", file=sys.stderr)


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Voss Taxi Web App API",
        "version": "1.0.0",
        "endpoints": {
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "me": "GET /api/auth/me",
            "health": "GET /health"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


# ========== Authentication Endpoints ==========
@app.post("/api/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    db_user = auth.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return auth.create_user(db=db, user=user)


@app.post("/api/auth/login", response_model=schemas.Token)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = auth.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=schemas.User)
async def get_current_user_info(current_user: models.User = Depends(auth.get_current_active_user)):
    """Get current logged-in user information"""
    return current_user


@app.post("/api/auth/logout")
async def logout():
    """Logout (client should delete token)"""
    return {"message": "Successfully logged out"}


# Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
