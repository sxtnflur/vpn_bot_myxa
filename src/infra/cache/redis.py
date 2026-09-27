from domain.cache.cache_service import CacheService
from redis.asyncio import Redis
from typing_extensions import Any


class RedisCacheService(CacheService):
    def __init__(self, redis_url: str):
        self._client = Redis.from_url(redis_url)

    async def set(self, key: str, value: Any) -> None:
        await self._client.set(key, value)

    async def get(self, key: str) -> Any:
        return await self._client.get(key)

    async def close(self) -> None:
        await self._client.aclose()
