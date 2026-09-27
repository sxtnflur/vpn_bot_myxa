from typing_extensions import Any
from abc import ABC, abstractmethod


class CacheService(ABC):
    @abstractmethod
    async def set(self, key: str, value: Any) -> None: pass
    @abstractmethod
    async def get(self, key: str) -> Any: pass

    async def close(self) -> None: pass
