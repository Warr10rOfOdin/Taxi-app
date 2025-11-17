"""
Vercel serverless function handler for FastAPI
"""
from mangum import Mangum
from main import app

# Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
