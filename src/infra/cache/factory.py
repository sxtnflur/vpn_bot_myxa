from config.settings import Settings
from typing_extensions import Literal


def create_cache_service(strategy: Literal['memory', 'redis'], settings: Settings):
    if strategy == 'memory':
        from infra.cache.memory import MemoryCacheService
        return MemoryCacheService()

    from infra.cache.redis import RedisCacheService
    return RedisCacheService(redis_url=settings.redis_url)
