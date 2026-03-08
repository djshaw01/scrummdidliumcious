"""Pytest fixtures for SCRUM Poker integration tests.

Provides an in-memory SQLite database with a static connection pool so all
sessions within a test share the same database instance, enabling end-to-end
HTTP → service → repository → DB flow without a running PostgreSQL server.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session as SASession, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base

# Import all models so metadata is fully populated before create_all.
import app.models.configuration  # noqa: F401
import app.models.participant  # noqa: F401
import app.models.session  # noqa: F401
import app.models.storage_issue  # noqa: F401
import app.models.team  # noqa: F401
import app.models.vote  # noqa: F401


@pytest.fixture(scope="module")
def integration_engine():
    """In-memory SQLite engine with a static pool for shared cross-session state.

    :yields: Configured SQLAlchemy engine.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        Base.metadata.create_all(conn)
        conn.commit()
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(integration_engine) -> SASession:
    """Provide a fresh session and truncate all tables after each test.

    :param integration_engine: Module-scoped SQLite engine.
    :yields: SQLAlchemy ORM session.
    """
    factory = sessionmaker(integration_engine, expire_on_commit=False)
    session = factory()
    yield session
    session.close()
    # Truncate all tables in reverse dependency order between tests.
    with integration_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()


@pytest.fixture()
def api_db_factory(integration_engine):
    """Return a callable that creates fresh ORM sessions for route handlers.

    Routes call ``get_db_session()`` per request; this factory is injected via
    ``patch`` so each call gets a new session backed by the same in-memory DB.

    :param integration_engine: Module-scoped SQLite engine.
    :returns: Callable that produces new SASession instances.
    """
    return sessionmaker(integration_engine, expire_on_commit=False)
