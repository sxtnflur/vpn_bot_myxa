import datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from application.ports.message_sender import PaymentMessageSender
from presentation.bot.shared.utils.date import sub_end_to_string, date_to_local_tz


class AiogramPaymentMessageSender(PaymentMessageSender):
    def __init__(self, bot: Bot, tz: datetime.timedelta):
        self._bot = bot
        self._tz = tz

    async def on_payment(self, telegram_id: int, expire_at: datetime.datetime) -> None:
        await self._bot.send_message(
            chat_id=telegram_id,
            text=f'''
✅ <b>Оплата прошла успешно</b>

📅 Дата окончания: {sub_end_to_string(date_to_local_tz(expire_at, tz=self._tz))}
''',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text='В меню', callback_data='menu'
                )]
            ])
        )
