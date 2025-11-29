import pytest

from app.db import SessionLocal, init_db
from app import models


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Ensure tables exist before any tests run.
    In production you'd use Alembic; here we reuse init_db().
    """
    init_db()
    yield


@pytest.fixture(scope="function")
def db_session():
    """
    Provides a clean DB session per test.

    We truncate all tables between tests to keep them isolated while still
    using the same Postgres database the app uses.
    """
    db = SessionLocal()

    # Clean existing data
    # We use sorted_tables in reverse FK order so deletes don't violate constraints.
    for table in reversed(models.Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()

    try:
        yield db
    finally:
        db.close()
