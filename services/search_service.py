from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import Game, Provider
from schemas import SearchResult
from cache import RedisCache

class SearchService:
    def __init__(self):
        self.cache = RedisCache()

    async def search(self, query: str, db: AsyncSession) -> dict:
        cache_key = f"search_query_{query.lower()}"
        cached_data = self.cache.get(cache_key)

        if cached_data:
            return {
                "message": "Search result from cache",
                "data": cached_data,
                "cache": True
            }

        like_pattern = f"%{query}%"
        result = SearchResult()

        games_stmt = select(Game.id).where(func.lower(Game.title).ilike(func.lower(like_pattern)))
        games_result = await db.execute(games_stmt)
        result.games = [row[0] for row in games_result.fetchall()]

        providers_stmt = select(Provider.id).where(func.lower(Provider.name).ilike(func.lower(like_pattern)))
        providers_result = await db.execute(providers_stmt)
        result.providers = [row[0] for row in providers_result.fetchall()]

        # Кладем результат в кеш
        self.cache.set(cache_key, result.model_dump())

        return {
            "message": "Search result from DB",
            "data": result.model_dump(),
            "cache": False
        }
