import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import USE_SEARCH_SERVICE
from database import get_db
from models import Game, Provider
from schemas import SearchResult
from services.search_service import SearchService

app = FastAPI()

# Сервис поиска
search_service = SearchService()


USE_SERVICE = USE_SEARCH_SERVICE

@app.get("/search/", response_model=SearchResult)
async def search(
    query: Optional[str] = Query(
        default=None,
        min_length=2,
        max_length=100,
        description="Поисковый запрос (от 2 до 100 символов)"
    ),
    db: AsyncSession = Depends(get_db)
):
    if not query:
        return {
            "message": "Поисковый запрос не указан",
            "data": SearchResult().model_dump(),
            "cache": False
        }

    # Поиск через сервис
    if USE_SERVICE:
        return await search_service.search(query, db)

    # Прямой поиск по базе данных
    result = SearchResult()
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

@app.get("/")
def read_root():
    return {"message": "FastAPI + Docker + PostgreSQL"}


