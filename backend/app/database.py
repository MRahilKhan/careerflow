import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = (
    os.getenv("CAREERFLOW_DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or os.getenv("DATABASE_URL")
)

if not DATABASE_URL:
    if os.getenv("VERCEL"):
        raise RuntimeError(
            "No database configured. Set CAREERFLOW_DATABASE_URL, POSTGRES_URL, "
            "or DATABASE_URL in the Vercel project's Environment Variables "
            "(Production) and redeploy."
        )

    DATABASE_URL = "sqlite:///./careerflow.db"


if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1,
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )


_scheme = (
    DATABASE_URL.split("://", 1)[0]
    if "://" in DATABASE_URL
    else DATABASE_URL
)

print(f"[CareerFlow] Database backend: {_scheme}")


connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite://")
    else {}
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
