from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taxi_app.db")

# Configure engine based on database type
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
elif "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
    # PostgreSQL configuration for serverless (Supabase)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=300,    # Recycle connections after 5 minutes
        pool_size=5,         # Connection pool size
        max_overflow=10      # Max overflow connections
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
