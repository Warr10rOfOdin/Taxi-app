from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

# Don't load .env in production (Vercel injects env vars directly)
if os.getenv("VERCEL") != "1":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not installed, that's ok

# Use /tmp for SQLite in serverless environments (Vercel)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/taxi_app.db")

# CRITICAL: Normalize postgres:// to postgresql:// (SQLAlchemy requirement)
if DATABASE_URL.startswith("postgres://") and not DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"✓ Normalized DATABASE_URL to use postgresql://", file=sys.stderr)

# Configure engine based on database type
engine = None
try:
    if "sqlite" in DATABASE_URL.lower():
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        print(f"✓ SQLite engine created", file=sys.stderr)
    elif "postgresql" in DATABASE_URL.lower():
        # PostgreSQL configuration for serverless (Supabase)
        # Keep it simple - no connect_args that might fail
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10
        )
        print(f"✓ PostgreSQL engine created", file=sys.stderr)
    else:
        engine = create_engine(DATABASE_URL)
        print(f"✓ Generic database engine created", file=sys.stderr)

except Exception as e:
    print(f"⚠ Warning: Could not create database engine: {e}", file=sys.stderr)
    print(f"⚠ Using in-memory SQLite as fallback", file=sys.stderr)
    # Fallback to in-memory SQLite
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

print(f"✓ Database module initialized", file=sys.stderr)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✓ Database tables initialized", file=sys.stderr)
    except Exception as e:
        print(f"⚠ Warning: Could not initialize tables: {e}", file=sys.stderr)
