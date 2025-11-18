"""
Minimal test handler - verifies Vercel Python + Mangum works
"""
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Minimal test works!"}

@app.get("/test")
def test():
    return {"test": "success", "vercel": "working"}

handler = Mangum(app, lifespan="off")
