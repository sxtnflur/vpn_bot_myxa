import asyncio
import datetime
import logging
from decimal import Decimal

from application.errors import IncreaseSubByEmailError, SubscriptionAlreadyExistsError
from application.ports.message_sender import PaymentMessageSender
from application.rates import RatesService
from domain.cache.cache_service import CacheService
from domain.payments.registry import PaymentsRegistry
from application.subscriptions.service import SubscriptionsTgBotService
from presentation.bot.shared.errors.bot_errors import PaymentError


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
        self._webhook_lock = asyncio.Lock()

    async def create_payment(
            self,
            *,
            email: str,
            telegram_id: int,
            full_name: str,
            username: str | None,
            amount: Decimal | int | float,
            description: str,
            rate_id: int | None = None
    ) -> str:
        """
        rate_id + email — добавление новой подписки (клиента) с этим email по тарифу.
        Только email — продление существующей подписки.

        :param email: email нового клиента (с rate_id) или продлеваемой подписки (без rate_id)
        :param rate_id: тариф новой подписки
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
            'email': email
        }

        if rate_id is not None:
            metadata['rate_id'] = rate_id

        if self._fake:
            payment_id = f'test-payment-{telegram_id}-{datetime.datetime.now().timestamp()}'
            await self.on_payment_webhook(
                payment_id, metadata,
                is_succeed=True
            )
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
            metadata: dict,
            is_succeed: bool
    ) -> None:
        telegram_id = metadata['telegram_id']

        try:
            if not is_succeed:
                await self._sender.on_error_payment(
                    telegram_id,
                    'Оплата была отклонена. Обратитесь в поддержку: /support'
                )
                return

            # Лок: два одновременных вебхука с одним payment_id не должны выдать подписку дважды
            async with self._webhook_lock:
                if await self._is_processed(payment_id):
                    return

                full_name = metadata['full_name']
                username = metadata['username']
                email = metadata['email']
                rate_id = metadata.get('rate_id')

                if rate_id is not None:
                    # Покупка тарифа — всегда новый клиент. email может отсутствовать у старых платежей
                    try:
                        added_sub = await self._subs_service.add_subscription(
                            telegram_id=telegram_id,
                            full_name=full_name,
                            username=username,
                            rate_id=rate_id,
                            email=email
                        )
                    except SubscriptionAlreadyExistsError:
                        # Почту заняли между оплатой и вебхуком — ретраи не помогут, нужен человек
                        logging.error('Оплата %s: email %s уже занят, подписка не создана', payment_id, email)
                        await self._mark_processed(payment_id)
                        await self._sender.on_error_payment(
                            telegram_id,
                            message=f'Оплата получена, но подписка с почтой {email} уже существует. '
                                    f'Обратитесь в поддержку: /support'
                        )
                        return
                    expire_at = added_sub.expire_at
                    paid_email = added_sub.email or email
                elif email is not None:
                    try:
                        expire_at = await self._subs_service.increase_subscription_by_email(
                            email=email, expire_in=datetime.timedelta(days=30)
                        )
                        paid_email = email
                    except IncreaseSubByEmailError:
                        # Клиента удалили между оплатой и вебхуком — ретраи не помогут, нужен человек
                        logging.error('Оплата %s: подписка по email %s не найдена', payment_id, email)
                        await self._mark_processed(payment_id)
                        await self._sender.on_error_payment(
                            telegram_id,
                            message=f'Оплата получена, но подписка {email} не найдена. '
                                    f'Обратитесь в поддержку: /support'
                        )
                        return
                else:
                    await self._mark_processed(payment_id)
                    await self._sender.on_error_payment(
                        telegram_id,
                        message='Произошла ошибка во время оплаты. Обратитесь в поддержку: /support'
                    )
                    return

                # Помечаем только после выдачи подписки: если 3x-ui упал, ретрай RollyPay обработается заново
                await self._mark_processed(payment_id)

            await self._sender.on_payment(telegram_id, email=paid_email, expire_at=expire_at)

        except Exception:
            logging.exception('Ошибка во время оплаты')
            await self._sender.on_error_payment(
                telegram_id,
                message='Произошла ошибка во время оплаты. Обратитесь в поддержку: /support'
            )
            return

    @staticmethod
    def _processed_key(payment_id: str) -> str:
        return f'payment:processed:{payment_id}'

    async def _is_processed(self, payment_id: str) -> bool:
        return await self._cache.get(self._processed_key(payment_id)) is not None

    async def _mark_processed(self, payment_id: str) -> None:
        await self._cache.set(self._processed_key(payment_id), True)
