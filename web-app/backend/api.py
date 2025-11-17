"""
Vercel serverless function handler for FastAPI
"""
import sys
import traceback

print("=" * 60, file=sys.stderr)
print("Starting Vercel serverless function", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# Test basic imports first
try:
    print("→ Importing Mangum...", file=sys.stderr)
    from mangum import Mangum
    print("✓ Mangum imported successfully", file=sys.stderr)
except Exception as e:
    print(f"✗ FAILED to import Mangum: {e}", file=sys.stderr)
    traceback.print_exc()
    raise

# Import main app with detailed error handling
try:
    print("→ Importing main app...", file=sys.stderr)
    from main import app
    print("✓ Main app imported successfully", file=sys.stderr)
except ImportError as e:
    print(f"✗ IMPORT ERROR in main: {e}", file=sys.stderr)
    traceback.print_exc()
    raise
except Exception as e:
    print(f"✗ FAILED to import main app: {e}", file=sys.stderr)
    traceback.print_exc()
    raise

# Create Mangum handler
try:
    print("→ Creating Mangum handler...", file=sys.stderr)
    handler = Mangum(app, lifespan="off")
    print("✓ Handler created successfully", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("Serverless function ready!", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
except Exception as e:
    print(f"✗ FAILED to create handler: {e}", file=sys.stderr)
    traceback.print_exc()
    raise

