import datetime
from decimal import Decimal

from application.ports.message_sender import PaymentMessageSender
from application.rates import RatesService
from domain.cache.cache_service import CacheService
from domain.payments.registry import PaymentsRegistry
from application.subscriptions.service import SubscriptionsTgBotService


class PaymentsService:
    def __init__(
            self,
            registry: PaymentsRegistry,
            subscriptions_service: SubscriptionsTgBotService,
            sender: PaymentMessageSender,
            rates: RatesService,
            payment_key: str,
            cache: CacheService,
            fake: bool = False
    ):
        self._registry = registry
        self._subs_service = subscriptions_service
        self._sender = sender
        self._rates = rates
        self._payment_key = payment_key
        self._cache = cache
        self._fake = fake

    async def create_payment(
            self,
            *,
            telegram_id: int,
            full_name: str,
            username: str | None,
            amount: Decimal | int | float,
            description: str,
            rate_id: int | None = None,
            email: str | None = None
    ) -> str:
        """
        :param email: Для продления подписки по email (если не указан email)
        :param rate_id: Для покупки или продления подписки по rate_id (если не указан rate_id)
        :param full_name:
        :param username:
        :param telegram_id:
        :param amount:
        :param description:
        :return: Payment URL
        """

        if rate_id is None and email is None:
            raise ValueError('Нужно указать rate_id или email')

        if rate_id is not None and email is not None:
            raise ValueError('Нужно указать или rate_id, или email, но не оба')

        metadata = {
            'telegram_id': telegram_id,
            'full_name': full_name,
            'username': username
        }

        if rate_id is not None:
            metadata['rate_id'] = rate_id

        if email is not None:
            metadata['email'] = email

        if self._fake:
            payment_id = f'test-payment-{telegram_id}-{datetime.datetime.now().timestamp()}'
            await self.on_payment_webhook(payment_id, metadata)
            url = 'https://example.com'
            return url
        else:
            if not isinstance(amount, Decimal):
                amount = Decimal(amount)

            result = await self._registry.get(self._payment_key).create_payment(
                amount=amount,
                description=description,
                metadata=metadata
            )
            return result.url

    async def on_payment_webhook(
            self,
            payment_id: str,
            metadata: dict
    ) -> None:

        if not await self._is_idempotent_callback(
            payment_id
        ):
            return

        telegram_id = metadata['telegram_id']
        full_name = metadata['full_name']
        username = metadata['username']

        rate_id = metadata.get('rate_id')
        email = metadata.get('email')

        if email is not None:
            expire_at = await self._subs_service.increase_subscription_by_email(
                email=email, expire_in=datetime.timedelta(days=30)
            )
        elif rate_id is not None:
            added_sub = await self._subs_service.add_subscription(
                telegram_id=telegram_id,
                full_name=full_name,
                username=username,
                rate_id=rate_id
            )
            expire_at = added_sub.expire_at
        else:
            await self._sender.on_error_payment(
                telegram_id,
                message='Произошла ошибка во время оплаты. Обратитесь в поддержку: /support'
            )
            return

        await self._sender.on_payment(telegram_id, expire_at=expire_at)

    async def _is_idempotent_callback(self, payment_id: str) -> bool:
        payment_ids = await self._cache.get('payment_ids')

        if payment_ids is None:
            payment_ids = []

        if payment_id in payment_ids:
            return False

        payment_ids.append(payment_id)
        await self._cache.set('payment_ids', payment_ids)
        return True
