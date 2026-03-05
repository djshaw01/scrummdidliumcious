"""SQLAlchemy repository adapters for PostgreSQL-backed persistence.

Scaffolded in Phase 2 (Foundational).  Repository methods raise
:class:`NotImplementedError` until Phase 6+ when ``DATA_BACKEND=postgres``
is activated.  ORM models in :mod:`app.infra.repository_sqlalchemy.models`
already define the full PostgreSQL schema.
"""

from app.infra.repository_sqlalchemy.repos import create_repositories

__all__ = ["create_repositories"]

