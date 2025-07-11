# from sqlalchemy import func, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from cache import cache
# from models import Game, Provider
# from schemas import SearchResult


# class SearchService:
#     def __init__(self):
#         self.cache = RedisCache()

#     async def search(self, query: str, db: AsyncSession) -> dict:
#         if query:
#             cache_key = f"{query.lower()}"
#             cached_data = await cache.get(cache_key)

#             if cached_data:
#                 print('ok')
#                 cached_dict = json.loads(cached_data)
        
#                 if isinstance(cached_dict, str):
#                     cached_dict = json.loads(cached_dict)
#                 cached_result = SearchResult(**cached_dict)
#                 cached_result.cache = True
#                 return cached_result
            
#             result = SearchResult()
#             like_pattern = f"%{query}%"

#             games_stmt = select(Game.id).where(func.lower(Game.title).ilike(func.lower(like_pattern)))
#             games_result = await db.execute(games_stmt)
#             result.games = [row[0] for row in games_result.fetchall()]

#             providers_stmt = select(Provider.id).where(func.lower(Provider.name).ilike(func.lower(like_pattern)))
#             providers_result = await db.execute(providers_stmt)
#             result.providers = [row[0] for row in providers_result.fetchall()]
#             await cache.set(cache_key, result.model_dump_json())

#             return result


import json
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from cache import cache
from models import Game, Provider
from schemas import SearchResult


class SearchService:
    def __init__(self):
        pass

    async def search(self, query: str, db: AsyncSession) -> SearchResult:
        cache_key = query.lower()
        cached_data = await cache.get(cache_key)

        if cached_data:
            cached_dict = json.loads(cached_data)
            if isinstance(cached_dict, str):
                cached_dict = json.loads(cached_dict)
            cached_result = SearchResult(**cached_dict)
            cached_result.cache = True
            return cached_result

        # Прямой поиск по БД
        result = SearchResult()
        like_pattern = f"%{query}%"

        games_stmt = select(Game.id).where(func.lower(Game.title).ilike(func.lower(like_pattern)))
        games_result = await db.execute(games_stmt)
        result.games = [row[0] for row in games_result.fetchall()]

        providers_stmt = select(Provider.id).where(func.lower(Provider.name).ilike(func.lower(like_pattern)))
        providers_result = await db.execute(providers_stmt)
        result.providers = [row[0] for row in providers_result.fetchall()]

        await cache.set(cache_key, result.model_dump_json())

        return result
