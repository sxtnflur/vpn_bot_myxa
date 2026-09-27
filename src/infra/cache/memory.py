from domain.cache.cache_service import CacheService
from typing_extensions import Any


class MemoryCacheService(CacheService):
    def __init__(self):
        self._data = {}

    async def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    async def get(self, key: str) -> Any:
        return self._data.get(key)
