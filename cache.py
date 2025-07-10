# cache.py
import json
import os

from redis import asyncio as redis


class RedisCache:
    def __init__(self):
        self.redis = None

    async def init(self):
        self.redis = await redis.from_url(
            f"redis://redis:6379/0",
            decode_responses=True,
            max_connections=10,
        )

    async def get(self, key: str):
        return await self.redis.get(key)

    async def set(self, key: str, value, expire: int = 300):
        await self.redis.set(key, json.dumps(value), ex=expire)

cache = RedisCache()
