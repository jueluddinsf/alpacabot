import asyncpg
from contextlib import asynccontextmanager


class Database:
    """Async wrapper around a PostgreSQL connection pool."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Create the connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self.dsn)

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def connection(self):
        """Acquire a database connection from the pool."""
        if self._pool is None:
            await self.connect()
        assert self._pool is not None
        conn = await self._pool.acquire()
        try:
            yield conn
        finally:
            await self._pool.release(conn)
