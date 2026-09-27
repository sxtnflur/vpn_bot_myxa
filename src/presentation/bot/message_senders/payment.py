import datetime
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from application.ports.message_sender import PaymentMessageSender
from application.subscriptions.service import SubscriptionsTgBotService
from presentation.bot.shared.utils.date import sub_end_to_string, date_to_local_tz

PAYMENT_SUCCESS_HEADER = '✅ <b>Оплата прошла успешно</b>\n'


class AiogramPaymentMessageSender(PaymentMessageSender):
    def __init__(
            self,
            bot: Bot,
            tz: datetime.timedelta,
            subs_service: SubscriptionsTgBotService,
            profile_page_size: int
    ):
        self._bot = bot
        self._tz = tz
        self._subs_service = subs_service
        self._profile_page_size = profile_page_size

    async def on_payment(self, telegram_id: int, email: str, expire_at: datetime.datetime | None) -> None:
        # Показываем профиль сразу на странице с оплаченной подпиской
        try:
            page = await self._subs_service.get_page_with_subscription(
                telegram_id, email=email, page_size=self._profile_page_size
            )
        except Exception:
            # Подписка уже выдана — ошибка отображения профиля не должна выглядеть как ошибка оплаты
            logging.exception('Не удалось получить профиль после оплаты подписки %s', email)
            page = None

        if page is not None:
            # Импорт здесь: пакет statistic тянет handlers -> bootstrap, а bootstrap импортирует этот модуль
            from presentation.bot.statistic.screens import client_statistic
            try:
                screen = client_statistic(page, tz=self._tz, header=PAYMENT_SUCCESS_HEADER)
                await screen.send_by_id(telegram_id, self._bot)
                return
            except Exception:
                logging.exception('Не удалось отправить профиль после оплаты подписки %s', email)

        # Оплачена чужая подписка (продление по email) или профиль недоступен
        await self._bot.send_message(
            chat_id=telegram_id,
            text=f'''
{PAYMENT_SUCCESS_HEADER}
📅 Дата окончания: {sub_end_to_string(date_to_local_tz(expire_at, tz=self._tz))}
''',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text='В меню', callback_data='menu'
                )]
            ])
        )

    async def on_error_payment(self, telegram_id: int, message: str) -> None:
        await self._bot.send_message(
            chat_id=telegram_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text='Помощь', callback_data='support'
                )],
                [InlineKeyboardButton(
                    text='В меню', callback_data='menu'
                )]
            ])
        )
