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
    print(f"🔥 Failed to create database engine: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    print(f"⚠️  App will start without database support", file=sys.stderr)
    # Don't raise - allow app to start without DB
    engine = None

# Only create SessionLocal if engine exists
if engine is not None:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"✓ SessionLocal created", file=sys.stderr)
else:
    SessionLocal = None
    print(f"⚠️  SessionLocal not created (no engine)", file=sys.stderr)

Base = declarative_base()

print(f"✓ Database module initialized", file=sys.stderr)


def get_db():
    """Dependency for getting database session"""
    if engine is None:
        # Fail fast when endpoints actually need DB
        raise RuntimeError("Database engine is not available. Check logs for initialization errors.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    if engine is None:
        print(f"⚠️  Cannot initialize tables (no engine)", file=sys.stderr)
        return
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✓ Database tables initialized", file=sys.stderr)
    except Exception as e:
        print(f"⚠ Warning: Could not initialize tables: {e}", file=sys.stderr)
