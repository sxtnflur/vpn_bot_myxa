from abc import ABC, abstractmethod
from decimal import Decimal
import datetime

from domain.payments.values import PaymentResult


class PaymentService(ABC):
    @abstractmethod
    async def create_payment(self,
         amount: Decimal, description: str,
         metadata: dict | None = None,
         expired_date: datetime.date | None = None
    ) -> PaymentResult: pass
