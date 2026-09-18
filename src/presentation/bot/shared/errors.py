import logging

from aiogram import Router
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import Message, CallbackQuery, ErrorEvent

from application.errors import NoSubError
from presentation.bot import commands


def _get_message(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        return event.message
    elif isinstance(event, Message):
        return event


def _get_message_from_error_event(event: ErrorEvent):
    return _get_message(event.update.event)


DEFAULT_ERROR_MESSAGE = 'Произошла непредвиденная ошибка.\n' \
                         'Попробуйте совершить это действие позже или обратитесь ' \
                         f'в поддержку: /{commands.SUPPORT}'


def register_errors(router: Router):
    @router.error(ExceptionTypeFilter(NoSubError))
    async def no_sub_error(event: ErrorEvent):
        message = _get_message_from_error_event(event)
        await message.answer(
            'Для этого действия у вас должна быть действующая подписка\n\n'
            f'Приобрести подписку — /{commands.RATES}'
        )
        logging.critical(event.exception, exc_info=True)

    @router.error()
    async def global_error(event: ErrorEvent):
        message = _get_message_from_error_event(event)
        await message.answer(DEFAULT_ERROR_MESSAGE)
        logging.critical(event.exception, exc_info=True)
