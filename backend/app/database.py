import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

database_url = (
    os.getenv("CAREERFLOW_DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or os.getenv("DATABASE_URL")
)
if not database_url:
    if os.getenv("VERCEL"):
        # Never silently fall back to /tmp SQLite in production: /tmp is private
        # to each serverless instance, so different concurrent requests would
        # see different, mostly-empty databases (users "randomly" 401ing).
        # Fail loudly instead so a missing env var is obvious, not mysterious.
        raise RuntimeError(
            "No database configured. Set CAREERFLOW_DATABASE_URL, POSTGRES_URL, "
            "or DATABASE_URL in the Vercel project's Environment Variables "
            "(Production) and redeploy."
        )
    database_url = "sqlite:///./careerflow.db"

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Log (without credentials) which database backend is actually in use, so this
# is visible in Vercel's runtime function logs rather than guessed at.
_scheme = database_url.split("://", 1)[0] if "://" in database_url else database_url
print(f"[CareerFlow] Database backend: {_scheme}")

connect_args = {} if database_url.startswith("postgresql+") else {"check_same_thread": False}
engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
