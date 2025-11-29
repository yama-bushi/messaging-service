# app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Engine with hardened pool options inspired by your db_pg.py patterns:
# - pool_pre_ping: test connections before use, auto-dispose broken ones
# - pool_size / max_overflow: small but non-trivial concurrency
# - pool_recycle: recycle connections periodically to avoid stale TCP
engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,  # seconds
    connect_args={"connect_timeout": 10},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db():
    """
    FastAPI dependency that yields a DB session.
    If you ever want a retry layer like _db_retry, the best place
    is around your service methods rather than here.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables on startup.

    For a real production system you'd use Alembic, but for this
    take-home, auto-creating the schema is a pragmatic choice.
    """
    from app import models

    models.Base.metadata.create_all(bind=engine)
