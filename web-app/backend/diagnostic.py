"""
Diagnostic handler to check Vercel environment
"""
import sys
import os
import json

def handler(event, context):
    """Show environment information"""

    info = {
        "status": "ok",
        "python_version": sys.version,
        "python_path": sys.path,
        "environment_variables": {
            "VERCEL": os.getenv("VERCEL"),
            "VERCEL_ENV": os.getenv("VERCEL_ENV"),
            "VERCEL_REGION": os.getenv("VERCEL_REGION"),
            "DATABASE_URL_SET": "Yes" if os.getenv("DATABASE_URL") else "No",
            "ALLOWED_ORIGINS_SET": "Yes" if os.getenv("ALLOWED_ORIGINS") else "No",
            "SECRET_KEY_SET": "Yes" if os.getenv("SECRET_KEY") else "No",
        },
        "current_directory": os.getcwd(),
        "files_in_directory": os.listdir(os.getcwd())[:20],  # First 20 files
    }

    try:
        # Try importing key modules
        info["imports"] = {}

        try:
            import fastapi
            info["imports"]["fastapi"] = f"OK - {fastapi.__version__}"
        except Exception as e:
            info["imports"]["fastapi"] = f"FAILED - {str(e)}"

        try:
            import mangum
            info["imports"]["mangum"] = f"OK - {mangum.__version__}"
        except Exception as e:
            info["imports"]["mangum"] = f"FAILED - {str(e)}"

        try:
            import sqlalchemy
            info["imports"]["sqlalchemy"] = f"OK - {sqlalchemy.__version__}"
        except Exception as e:
            info["imports"]["sqlalchemy"] = f"FAILED - {str(e)}"

        try:
            import psycopg2
            info["imports"]["psycopg2"] = f"OK"
        except Exception as e:
            info["imports"]["psycopg2"] = f"FAILED - {str(e)}"

        try:
            import pandas
            info["imports"]["pandas"] = f"OK - {pandas.__version__}"
        except Exception as e:
            info["imports"]["pandas"] = f"FAILED - {str(e)}"

    except Exception as e:
        info["import_check_error"] = str(e)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(info, indent=2)
    }
