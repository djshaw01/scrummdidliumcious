"""Unit test fixtures providing an in-memory SQLite database with the full SCRUM Poker schema."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session as SASession, sessionmaker

from app.db import Base

# Import all models so Base.metadata is fully populated before create_all.
import app.models.configuration  # noqa: F401
import app.models.participant  # noqa: F401
import app.models.session  # noqa: F401
import app.models.storage_issue  # noqa: F401
import app.models.team  # noqa: F401
import app.models.vote  # noqa: F401


@pytest.fixture(scope="session")
def db_engine():
    """Create an in-memory SQLite engine with the full SCRUM Poker schema.

    :yields: Configured SQLAlchemy engine.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    with engine.connect() as conn:
        # SQLite FK pragma — keep off so use_alter deferred FKs don't block DDL.
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        Base.metadata.create_all(conn)
        conn.commit()
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> SASession:
    """Transactional SQLAlchemy session that rolls back after each test.

    :param db_engine: Session-scoped engine fixture.
    :yields: SQLAlchemy Session within a savepoint-backed transaction.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    factory = sessionmaker(bind=connection, expire_on_commit=False)
    session = factory()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
