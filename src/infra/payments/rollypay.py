import uuid
from decimal import Decimal
import datetime

import aiohttp
from domain.payments.payment_service import PaymentService
from domain.payments.values import PaymentResult

from infra.rollypay.client import RollyPay


class RollyPayStrategy(PaymentService):
    def __init__(self, rollypay: RollyPay, test: bool = False):
        self._rollypay = rollypay
        self._test = test

    async def create_payment(self,
                             amount: Decimal, description: str,
                             metadata: dict | None = None,
                             expired_date: datetime.date | None = None
                             ) -> PaymentResult:
        result = await self._rollypay.create_payment(
            amount=float(amount),
            description=description,
            metadata=metadata,
            test=self._test
        )
        return PaymentResult(
            id=result.payment_id,
            url=result.pay_url
        )
