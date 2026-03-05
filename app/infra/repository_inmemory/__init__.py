"""In-memory repository adapters with seed fixture data.

Public API surface:

- :func:`create_repositories` — create a fresh :class:`~app.domain.repositories.RepositoryContext`
- :func:`seed_repositories` — populate it with development fixture data
"""

from app.infra.repository_inmemory.repos import create_repositories
from app.infra.repository_inmemory.seed import seed_repositories

__all__ = ["create_repositories", "seed_repositories"]

