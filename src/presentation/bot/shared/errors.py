import logging
from html import escape

from aiogram import Bot, Router, types
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


def register_errors(router: Router, admin_logs_id: int):
    @router.error(ExceptionTypeFilter(NoSubError))
    async def no_sub_error(event: ErrorEvent):
        message = _get_message_from_error_event(event)
        await message.answer(
            'Для этого действия у вас должна быть действующая подписка\n\n'
            f'Приобрести подписку — /{commands.RATES}'
        )
        logging.critical(event.exception, exc_info=True)

    @router.error()
    async def global_error(event: ErrorEvent, bot: Bot):
        # Сначала логируем: отправка сообщений ниже сама может упасть
        logging.critical(event.exception, exc_info=True)

        message = _get_message_from_error_event(event)
        if message is not None:
            await message.answer(DEFAULT_ERROR_MESSAGE)

        user: types.User | None = getattr(event.update.event, 'from_user', None)
        user_info = f'@{user.username} #{user.id}' if user else 'неизвестного пользователя'
        # repr исключения часто содержит <...>, а бот шлёт сообщения в HTML
        await bot.send_message(
            chat_id=admin_logs_id,
            text=f'Ошибка у {escape(user_info)}:\n\n'
                 f'{escape(repr(event.exception))}'
        )
