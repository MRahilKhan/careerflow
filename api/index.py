from fastapi import FastAPI
from backend.app.main import app as backend_app

# Vercel forwards /api/* requests to this function. Keep the prefix explicit
# so the static frontend can own the root route.
app = FastAPI(title="CareerFlow API")
app.mount("/api", backend_app)

__all__ = ["app"]
