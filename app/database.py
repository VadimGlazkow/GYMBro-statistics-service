from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

Base = declarative_base()


def normalize_database_url(url: str) -> str:
    """
    Render часто отдаёт postgres:// — приводим к формату SQLAlchemy.
    postgresql+psycopg2:// явно указывает драйвер (psycopg2-binary).
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def get_connect_args(url: str) -> dict:
    """
    Локальный Postgres — без SSL.
    Render Postgres (облако) — sslmode=require.
    Можно переопределить через DATABASE_SSL_MODE в .env.
    """
    if settings.DATABASE_SSL_MODE is not None:
        if settings.DATABASE_SSL_MODE == "":
            return {}
        return {"sslmode": settings.DATABASE_SSL_MODE}

    if "sslmode=" in url:
        return {}

    if "localhost" in url or "127.0.0.1" in url or "@db:" in url:
        return {}

    return {"sslmode": "require"}


def create_db_engine(url: str | None = None, **engine_kwargs):
    database_url = normalize_database_url(url or settings.DATABASE_URL)
    defaults = {
        "connect_args": get_connect_args(database_url),
        "pool_pre_ping": True,
    }
    defaults.update(engine_kwargs)
    return create_engine(database_url, **defaults)


engine = create_db_engine(pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
