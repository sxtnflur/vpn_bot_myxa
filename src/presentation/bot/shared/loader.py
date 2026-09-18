from presentation.bot.shared.errors import register_errors
from presentation.bot.shared.middlewares import register_middlewares
from typing_extensions import Literal

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import Settings

from presentation.bot import statistic, start, payments, my_sub


def create_bot(token: str):
    return Bot(token=token,
               default=DefaultBotProperties(
                   parse_mode=ParseMode.HTML,
                   link_preview_is_disabled=True
               ))


def create_dp(storage_type: Literal['memory', 'redis'], settings: Settings):
    if storage_type == 'redis':
        from aiogram.fsm.storage.redis import RedisStorage
        storage = RedisStorage.from_url(settings.redis_url)
    else:
        from aiogram.fsm.storage.memory import MemoryStorage
        storage = MemoryStorage()
    return Dispatcher(storage=storage)


def register_dp(dp: Dispatcher, settings: Settings):
    for router in (
        statistic.router,
        start.router,
        payments.router
        # my_sub.router
    ):
        dp.include_router(router)

    register_middlewares(dp, settings)
    register_errors(dp)
