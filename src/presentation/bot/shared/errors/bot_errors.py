from aiogram.types import InlineKeyboardMarkup


class BotError(Exception):
    def __init__(self, base_exception: Exception, chat_id: int, text: str, reply_markup: InlineKeyboardMarkup | None = None):
        self.base_exception = base_exception
        self.chat_id = chat_id
        self.text = text
        self.reply_markup = reply_markup


class ExternalBotError(BotError):
    def __init__(self, base_exception: Exception, user_telegram_id: int, text: str):
        super().__init__(
            base_exception, user_telegram_id, text
        )


class PaymentError(ExternalBotError):
    pass
