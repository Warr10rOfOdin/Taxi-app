"""
Main API entry point - FastAPI with authentication and database
Fault-tolerant version for debugging Vercel deployment
"""
import sys
import os
import traceback

# Add parent directory to path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60, file=sys.stderr)
print("Starting Voss Taxi API (Vercel Serverless)", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Working directory: {os.getcwd()}", file=sys.stderr)
print(f"sys.path: {sys.path[:3]}", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# Track what succeeded/failed
initialization_status = {
    "fastapi": None,
    "database": None,
    "database_tables": None
}
import_errors = []

# Import FastAPI basics
try:
    print("→ Importing FastAPI...", file=sys.stderr)
    from fastapi import FastAPI, Depends, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from mangum import Mangum
    print("✓ FastAPI imports successful", file=sys.stderr)
    initialization_status["fastapi"] = "success"
except Exception as e:
    error_msg = f"Failed to import FastAPI: {e}"
    print(f"✗ {error_msg}", file=sys.stderr)
    traceback.print_exc()
    initialization_status["fastapi"] = error_msg
    import_errors.append(error_msg)
    # Don't raise - try to continue

# Import database modules with error handling
database_available = False
try:
    print("→ Importing database modules...", file=sys.stderr)
    from sqlalchemy.orm import Session
    from datetime import timedelta
    from database import get_db, engine
    import models
    import schemas
    import auth
    print("✓ Database modules imported", file=sys.stderr)
    initialization_status["database"] = "success"
    database_available = True
except Exception as e:
    error_msg = f"Failed to import database modules: {e}"
    print(f"⚠ {error_msg}", file=sys.stderr)
    traceback.print_exc()
    initialization_status["database"] = error_msg
    import_errors.append(error_msg)
    # Don't raise - continue without database

# Create FastAPI app
app = FastAPI(
    title="Voss Taxi Web App API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - be permissive for now
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in ALLOWED_ORIGINS else ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"✓ CORS configured: {ALLOWED_ORIGINS}", file=sys.stderr)

# Database initialization - non-blocking
if database_available:
    try:
        print("→ Initializing database tables...", file=sys.stderr)
        models.Base.metadata.create_all(bind=engine)
        print("✓ Database tables ready", file=sys.stderr)
        initialization_status["database_tables"] = "success"
    except Exception as e:
        error_msg = f"Database initialization failed: {e}"
        print(f"⚠ {error_msg}", file=sys.stderr)
        initialization_status["database_tables"] = error_msg
else:
    initialization_status["database_tables"] = "skipped (database unavailable)"

print("=" * 60, file=sys.stderr)
print("API initialization complete!", file=sys.stderr)
print(f"Status: {initialization_status}", file=sys.stderr)
print("=" * 60, file=sys.stderr)


@app.get("/")
def read_root():
    """Root endpoint - health check with diagnostic info"""
    return {
        "status": "ok",
        "message": "Voss Taxi Web App API",
        "version": "1.0.0",
        "deployment": "vercel-serverless",
        "initialization": initialization_status,
        "errors": import_errors if import_errors else None,
        "database_available": database_available,
        "endpoints": {
            "docs": "GET /docs",
            "health": "GET /health",
            "debug": "GET /debug",
            "register": "POST /api/auth/register" if database_available else "unavailable",
            "login": "POST /api/auth/login" if database_available else "unavailable",
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy" if database_available else "degraded",
        "database": "not_available",
        "version": "1.0.0"
    }

    if database_available:
        try:
            # Test database connection
            from database import SessionLocal
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            status["database"] = "connected"
        except Exception as e:
            status["database"] = f"error: {str(e)}"

    return status


@app.get("/debug")
def debug_info():
    """Debug endpoint with detailed system information"""
    import sys
    return {
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "sys_path": sys.path[:5],
        "env_vars": {
            "VERCEL": os.getenv("VERCEL"),
            "DATABASE_URL": "***" if os.getenv("DATABASE_URL") else None,
            "POSTGRES_URL": "***" if os.getenv("POSTGRES_URL") else None,
        },
        "initialization_status": initialization_status,
        "import_errors": import_errors,
        "database_available": database_available
    }


# Handle OPTIONS for CORS preflight
@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}


# ========== Authentication Endpoints (only if database available) ==========
if database_available:
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
