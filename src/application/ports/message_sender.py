from abc import ABC, abstractmethod
import datetime


class PaymentMessageSender(ABC):
    @abstractmethod
    async def on_payment(self, telegram_id: int, expire_at: datetime.datetime) -> None: pass
