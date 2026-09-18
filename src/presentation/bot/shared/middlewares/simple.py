from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class SimpleMiddleware(BaseMiddleware):
    def __init__(self, **values):
        self.__data = values

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        data.update(**self.__data)
        return await handler(event, data)
