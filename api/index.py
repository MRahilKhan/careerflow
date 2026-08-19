from fastapi import FastAPI
from backend.app.main import app as backend_app

# Vercel forwards /api/* requests to this function. Mount the existing
# FastAPI application under that prefix while keeping local development intact.
app = FastAPI(title="CareerFlow API")
app.mount("/api", backend_app)

__all__ = ["app"]
