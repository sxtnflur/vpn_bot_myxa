import datetime
from decimal import Decimal

from application.ports.message_sender import PaymentMessageSender
from application.rates import RatesService
from domain.payments.registry import PaymentsRegistry
from application.subscriptions.service import SubscriptionsTgBotService


class PaymentsService:
    def __init__(
            self,
            registry: PaymentsRegistry,
            subscriptions_service: SubscriptionsTgBotService,
            sender: PaymentMessageSender,
            rates: RatesService,
            fake: bool = False
    ):
        self._registry = registry
        self._subs_service = subscriptions_service
        self._sender = sender
        self._rates = rates
        self._fake = fake

    async def create_payment(
            self,
            *,
            sub_td: datetime.timedelta,
            telegram_id: int,
            full_name: str,
            username: str | None,
            amount: Decimal,
            description: str
    ) -> str:
        """
        :param sub_td:
        :param full_name:
        :param username:
        :param telegram_id:
        :param amount:
        :param description:
        :return: Payment URL
        """

        metadata = {
            'telegram_id': telegram_id,
            'full_name': full_name,
            'username': username,
            'expire_in_seconds': round(sub_td.total_seconds())
        }

        if self._fake:
            await self.on_payment_webhook(metadata)
            return 'https://example.com'
        else:
            result = await self._registry.get('yookassa').create_payment(
                amount=amount,
                description=description,
                metadata=metadata
            )
            return result.url

    async def on_payment_webhook(
            self,
            metadata: dict
    ) -> None:

        telegram_id = metadata['telegram_id']
        full_name = metadata['full_name']
        username = metadata['username']
        expire_in_seconds = metadata['expire_in_seconds']
        expire_in = datetime.timedelta(seconds=expire_in_seconds)

        added_sub = await self._subs_service.add_subscription(
            telegram_id=telegram_id,
            full_name=full_name,
            username=username,
            expire_in=expire_in
        )

        await self._sender.on_payment(telegram_id, expire_at=added_sub.expire_at)
