from fastapi import FastAPI
from backend.app.main import app as backend_app

# Vercel forwards /api/* requests to this function. Mount the existing
# FastAPI application under that prefix while keeping local development intact.
app = FastAPI(title="CareerFlow API")
# Depending on Vercel's rewrite handling, the function can receive either the
# full /api/... path or a path with the /api prefix already stripped.
app.mount("/api", backend_app)
app.mount("/", backend_app)

__all__ = ["app"]
