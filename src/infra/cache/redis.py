import json

from domain.cache.cache_service import CacheService
from redis.asyncio import Redis
from typing_extensions import Any


class RedisCacheService(CacheService):
    """Значения хранятся в JSON, чтобы get возвращал те же типы, что и MemoryCacheService."""

    def __init__(self, redis_url: str):
        self._client = Redis.from_url(redis_url)

    async def set(self, key: str, value: Any) -> None:
        await self._client.set(key, json.dumps(value))

    async def get(self, key: str) -> Any:
        value = await self._client.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def close(self) -> None:
        await self._client.aclose()
