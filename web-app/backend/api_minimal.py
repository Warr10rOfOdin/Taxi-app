"""
Minimal Vercel handler to test if basic deployment works
"""
from fastapi import FastAPI
from mangum import Mangum

# Create a minimal FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Voss Taxi Web App API - Minimal Version"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
