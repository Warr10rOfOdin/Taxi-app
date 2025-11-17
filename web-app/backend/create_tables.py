"""
Database table creation script
Run this script to initialize the database tables in Supabase
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError

# Load environment variables
load_dotenv()

# Import models after loading env vars
from database import engine, Base
import models  # This imports all model classes

def create_tables():
    """Create all database tables"""
    try:
        print(f"Creating tables...")
        print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")

        # Test connection first
        with engine.connect() as conn:
            print("✓ Database connection successful")

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully!")

        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\nCreated tables ({len(tables)}):")
        for table in sorted(tables):
            print(f"  - {table}")

        return True

    except OperationalError as e:
        print(f"✗ Database connection error: {e}")
        print("\nTroubleshooting:")
        print("1. Check DATABASE_URL is set correctly")
        print("2. Verify Supabase project is active")
        print("3. Check database credentials")
        return False

    except ProgrammingError as e:
        print(f"✗ Database programming error: {e}")
        print("\nThis might mean tables already exist or there's a schema issue")
        return False

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Voss Taxi Database Initialization")
    print("=" * 60)
    print()

    success = create_tables()

    print()
    print("=" * 60)
    if success:
        print("✓ Database initialization completed successfully!")
    else:
        print("✗ Database initialization failed")
        print("\nYou can also run the SQL script directly in Supabase:")
        print("  1. Go to Supabase Dashboard → SQL Editor")
        print("  2. Run the init_database.sql file")
    print("=" * 60)
