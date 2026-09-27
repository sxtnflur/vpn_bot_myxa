from config.settings import Settings


def create_cache_service(settings: Settings):
    if not settings.redis_url:
        from infra.cache.memory import MemoryCacheService
        return MemoryCacheService()

    from infra.cache.redis import RedisCacheService
    return RedisCacheService(redis_url=settings.redis_url)
