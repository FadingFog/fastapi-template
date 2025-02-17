from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
