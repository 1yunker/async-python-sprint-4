from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import app_settings


# Функция понадобится при внедрении зависимостей Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

engine = create_async_engine(
    str(app_settings.database_dsn),
    echo=True,
    future=True
)
async_session = sessionmaker(
    engine, class_=AsyncSession,
    expire_on_commit=False
)