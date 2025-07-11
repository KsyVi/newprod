
import json
from typing import Optional

from fastapi import Depends, FastAPI, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import SearchResult
from cache import cache
from services.search_service import SearchService

app = FastAPI()
search_service = SearchService()

@app.on_event("startup")
async def startup_event():
    try:
        await cache.init()
    except HTTPException as e:
        print(f"Failed to initialize Redis: {e}")

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

    return await search_service.search(query, db)

@app.get("/")
def read_root():
    return {"message": "FastAPI + Docker + PostgreSQL"}

