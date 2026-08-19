import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

database_url = (
    os.getenv("CAREERFLOW_DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or os.getenv("DATABASE_URL")
)
if not database_url:
    # Vercel's deployment filesystem is read-only; /tmp is writable for the
    # lifetime of a serverless instance. Use a configured database in production.
    database_url = "sqlite:////tmp/careerflow.db" if os.getenv("VERCEL") else "sqlite:///./careerflow.db"

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

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
