import os

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from config import DATABASE_URL


# Создание асинхронного движка
engine = create_async_engine(
    DATABASE_URL,
    echo=True  
)

# Создание асинхронной сессии
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Зависимость для FastAPI (получение сессии)
async def get_db():
    async with async_session() as session:
        yield session
