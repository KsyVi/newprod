# cache.py
import json
import os

import redis


class RedisCache:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.client = redis.from_url(redis_url)

    def get(self, key: str):
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value, expire: int = 300):
        self.client.set(key, json.dumps(value), ex=expire)
