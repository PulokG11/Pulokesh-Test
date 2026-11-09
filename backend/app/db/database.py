from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from psycopg_pool import ConnectionPool

from app.config import get_settings

_pool: ConnectionPool | None = None
_memory_fallback = False


def init_pool() -> None:
    global _pool, _memory_fallback
    settings = get_settings()
    try:
        _pool = ConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=5,
            kwargs={"connect_timeout": 3},
            open=True,
        )
        # Probe
        with _pool.connection() as conn:
            conn.execute("select 1")
        _memory_fallback = False
    except Exception:
        _pool = None
        _memory_fallback = True


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def db_available() -> bool:
    return _pool is not None and not _memory_fallback


@contextmanager
def get_connection() -> Iterator:
    if _pool is None:
        raise RuntimeError("Database pool is not available")
    with _pool.connection() as conn:
        yield conn
