from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine

DATABASE_URL_ASYNC = "sqlite+aiosqlite:///./comments.db"
DATABASE_URL_SYNC = "sqlite:///./comments.db"

# Async engine (used by app)
engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

# Sync engine (ONLY for table creation)
sync_engine = create_engine(
    DATABASE_URL_SYNC,
    echo=False,
    future=True,
)
