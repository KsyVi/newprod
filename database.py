import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from base import Base

# Адрес подключения к базе данных
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@db:5432/fastapi_db"  
)

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
