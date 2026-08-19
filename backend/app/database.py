import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

database_url = os.getenv("CAREERFLOW_DATABASE_URL")
if not database_url:
    # Vercel's deployment filesystem is read-only; /tmp is writable for the
    # lifetime of a serverless instance. Use a configured database in production.
    database_url = "sqlite:////tmp/careerflow.db" if os.getenv("VERCEL") else "sqlite:///./careerflow.db"

engine = create_engine(database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
