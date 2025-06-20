from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional, List
from pydantic import BaseModel

from models import Game, Provider
from database import get_db  

from schemas import SearchResult

from dotenv import load_dotenv
import os
app = FastAPI()

load_dotenv() 
database_url = os.getenv("DATABASE_URL")
print(database_url)


# Роут для поиска по играм и провайдерам
@app.get("/search/", response_model=SearchResult)
async def search(
    query: Optional[str] = Query(
        default=None,
        min_length=2,
        max_length=100,
        description="Search term (2-100 chars)"
    ),
    db: AsyncSession = Depends(get_db)
):
    result = SearchResult()

    if query:
        like_pattern = f"%{query}%"

        # Поиск по играм
        games_stmt = select(Game.id).where(func.lower(Game.title).ilike(func.lower(like_pattern)))
        games_result = await db.execute(games_stmt)
        result.games = [row[0] for row in games_result.fetchall()]

        # Поиск по провайдерам
        providers_stmt = select(Provider.id).where(func.lower(Provider.name).ilike(func.lower(like_pattern)))
        providers_result = await db.execute(providers_stmt)
        result.providers = [row[0] for row in providers_result.fetchall()]

    return result

# Простой тестовый маршрут
@app.get("/")
def read_root():
    return {"message": "FastAPI + Docker + PostgreSQL"}
