"""FastAPI database session dependency.

Yields a scoped async database session for request handlers.
"""

from .engine import AsyncSessionLocal


async def get_db():
    """Generator providing an async DB session and handling cleanup."""
    async with AsyncSessionLocal() as session:
        yield session
