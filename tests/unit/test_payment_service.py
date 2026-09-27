import asyncio
import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.payments import PaymentsService
from application.subscriptions.dto import AddSubscriptionResponse
from domain.payments.registry import PaymentsRegistry
from domain.payments.values import PaymentResult

EXPIRE = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc)
METADATA = {'telegram_id': 100, 'full_name': 'Иван', 'username': 'ivan', 'rate_id': 1}


@pytest.fixture
def provider():
    provider = MagicMock()
    provider.create_payment = AsyncMock(return_value=PaymentResult(id='p1', url='https://pay.example/p1'))
    return provider


@pytest.fixture
def subs():
    subs = MagicMock()
    subs.add_subscription = AsyncMock(return_value=AddSubscriptionResponse(created=True, expire_at=EXPIRE))
    subs.increase_subscription_by_email = AsyncMock(return_value=EXPIRE)
    return subs


@pytest.fixture
def sender():
    sender = MagicMock()
    sender.on_payment = AsyncMock()
    sender.on_error_payment = AsyncMock()
    return sender


def make_service(provider, subs, sender, cache, rates, fake=False):
    return PaymentsService(
        registry=PaymentsRegistry().add('rollypay', provider),
        subscriptions_service=subs,
        sender=sender,
        rates=rates,
        payment_key='rollypay',
        cache=cache,
        fake=fake,
    )


@pytest.fixture
def service(provider, subs, sender, cache, rates):
    return make_service(provider, subs, sender, cache, rates)


# ---------- create_payment ----------

async def test_create_payment_requires_rate_or_email(service):
    with pytest.raises(ValueError):
        await service.create_payment(telegram_id=1, full_name='x', username=None, amount=1, description='d')


async def test_create_payment_rejects_rate_and_email(service):
    with pytest.raises(ValueError):
        await service.create_payment(telegram_id=1, full_name='x', username=None, amount=1,
                                     description='d', rate_id=1, email='a@b.c')


async def test_create_payment_by_rate(service, provider):
    url = await service.create_payment(telegram_id=100, full_name='Иван', username='ivan',
                                       amount=200, description='d', rate_id=1)

    assert url == 'https://pay.example/p1'
    kwargs = provider.create_payment.await_args.kwargs
    assert kwargs['amount'] == Decimal(200) and isinstance(kwargs['amount'], Decimal)
    assert kwargs['metadata'] == METADATA


async def test_create_payment_by_email_metadata(service, provider):
    await service.create_payment(telegram_id=100, full_name='Иван', username=None,
                                 amount=500, description='d', email='a@b.c')

    metadata = provider.create_payment.await_args.kwargs['metadata']
    assert metadata['email'] == 'a@b.c'
    assert 'rate_id' not in metadata


async def test_fake_payment_activates_immediately(provider, subs, sender, cache, rates):
    service = make_service(provider, subs, sender, cache, rates, fake=True)

    url = await service.create_payment(telegram_id=100, full_name='Иван', username='ivan',
                                       amount=200, description='d', rate_id=1)

    assert url == 'https://example.com'
    provider.create_payment.assert_not_awaited()
    subs.add_subscription.assert_awaited_once()
    sender.on_payment.assert_awaited_once_with(100, expire_at=EXPIRE)


# ---------- on_payment_webhook ----------

async def test_webhook_by_rate(service, subs, sender):
    await service.on_payment_webhook('p1', dict(METADATA))

    subs.add_subscription.assert_awaited_once_with(telegram_id=100, full_name='Иван', username='ivan', rate_id=1)
    sender.on_payment.assert_awaited_once_with(100, expire_at=EXPIRE)


async def test_webhook_by_email(service, subs, sender):
    metadata = {'telegram_id': 100, 'full_name': 'Иван', 'username': None, 'email': 'a@b.c'}

    await service.on_payment_webhook('p1', metadata)

    subs.increase_subscription_by_email.assert_awaited_once()
    assert subs.increase_subscription_by_email.await_args.kwargs['email'] == 'a@b.c'
    subs.add_subscription.assert_not_awaited()
    sender.on_payment.assert_awaited_once_with(100, expire_at=EXPIRE)


async def test_webhook_without_rate_and_email_reports_error(service, subs, sender):
    await service.on_payment_webhook('p1', {'telegram_id': 100, 'full_name': 'Иван', 'username': None})

    sender.on_error_payment.assert_awaited_once()
    sender.on_payment.assert_not_awaited()


async def test_webhook_is_idempotent(service, subs, sender):
    await service.on_payment_webhook('p1', dict(METADATA))
    await service.on_payment_webhook('p1', dict(METADATA))
    await service.on_payment_webhook('p2', dict(METADATA))

    assert subs.add_subscription.await_count == 2
    assert sender.on_payment.await_count == 2


async def test_webhook_retry_after_failure_is_processed(service, subs, sender):
    subs.add_subscription.side_effect = [RuntimeError('3x-ui down'),
                                         AddSubscriptionResponse(created=True, expire_at=EXPIRE)]

    with pytest.raises(RuntimeError):
        await service.on_payment_webhook('p1', dict(METADATA))
    await service.on_payment_webhook('p1', dict(METADATA))

    assert subs.add_subscription.await_count == 2
    sender.on_payment.assert_awaited_once()


class SlowCache:
    """Кэш с задержкой на чтении — как Redis/сеть: между get и set проходит await."""

    def __init__(self):
        self._data = {}

    async def get(self, key):
        value = self._data.get(key)
        await asyncio.sleep(0.01)
        return list(value) if value is not None else None

    async def set(self, key, value):
        self._data[key] = list(value)


async def test_concurrent_duplicate_webhooks(provider, subs, sender, rates):
    service = make_service(provider, subs, sender, SlowCache(), rates)

    await asyncio.gather(
        service.on_payment_webhook('p1', dict(METADATA)),
        service.on_payment_webhook('p1', dict(METADATA)),
    )

    assert subs.add_subscription.await_count == 1
