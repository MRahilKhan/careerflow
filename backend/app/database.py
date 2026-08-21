import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def get_database_url() -> str:
    database_url = (
        os.getenv("CAREERFLOW_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("DATABASE_URL")
    )

    if not database_url:
        if os.getenv("VERCEL"):
            raise RuntimeError(
                "No database configured. Set CAREERFLOW_DATABASE_URL, "
                "POSTGRES_URL, or DATABASE_URL in the Vercel "
                "Environment Variables and redeploy."
            )

        return "sqlite:///./careerflow.db"

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    return database_url


DATABASE_URL = get_database_url()


connect_args = (
    {}
    if DATABASE_URL.startswith("postgresql+")
    else {
        "check_same_thread": False,
    }
)


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
