"""Shared SQLAlchemy declarative base, engine, and session factory."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import sessionmaker

_engine = None
_session_factory: sessionmaker | None = None


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy ORM models."""


def init_db(database_url: str) -> None:
    """Initialise the engine and session factory from a connection URL.

    :param database_url: SQLAlchemy-compatible database URL string.
    """
    global _engine, _session_factory
    _engine = create_engine(database_url, pool_pre_ping=True)
    _session_factory = sessionmaker(_engine, expire_on_commit=False)


def get_db_session() -> SASession:
    """Return a new database Session from the application session factory.

    :returns: SQLAlchemy ORM Session instance.
    :raises RuntimeError: If :func:`init_db` has not been called first.
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialised — call init_db() first.")
    return _session_factory()
