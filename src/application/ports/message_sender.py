from abc import ABC, abstractmethod
import datetime


class PaymentMessageSender(ABC):
    @abstractmethod
    async def on_payment(self, telegram_id: int, email: str, expire_at: datetime.datetime | None) -> None:
        """
        :param email: email оплаченной (созданной или продлённой) подписки
        :param expire_at: None — бессрочная подписка
        """

    @abstractmethod
    async def on_error_payment(self, telegram_id: int, message: str) -> None: pass