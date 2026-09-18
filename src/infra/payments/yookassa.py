from decimal import Decimal
from async_yookassa import YooKassaClient

from domain.payments.payment_service import PaymentService
from domain.payments.values import PaymentResult


class YookassaService(PaymentService):
    def __init__(
            self,
            shop_id: str,
            secret_key: str,
            return_url: str
    ):
        self._client = YooKassaClient(
            account_id=shop_id,
            secret_key=secret_key
        )
        self._return_url = return_url

    async def create_payment(self, amount: Decimal,
                             description: str, test: bool = False,
                             metadata: dict | None = None, **kwargs) -> PaymentResult:
        metadata = metadata or {}
        data = {
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": self._return_url
            },
            "description": description,
            "metadata": metadata,
            "receipt": {
                "customer": {
                    "full_name": "Иванов Иван Иванович",
                    "phone": "79000000000"
                },
                "items": [
                    {
                        "description": description,
                        "quantity": "1.00",
                        "amount": {
                            "value": amount,
                            "currency": "RUB"
                        },
                        "vat_code": "2",
                        "payment_mode": "full_prepayment",
                        "payment_subject": "commodity"
                    }
                ]
            },
            "test": test
        }
        payment = await self._client.payment.create(data)
        return PaymentResult(
            id=payment.id,
            url=payment.confirmation.confirmation_url
        )
