from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from app.config import config

engine: AsyncEngine = create_async_engine(
    config.db.db_url, pool_size=config.db.pool_size, max_overflow=config.db.max_overflow
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Ideally for tests
AsyncScopedSession = async_scoped_session(AsyncSessionLocal, scopefunc=current_task)
