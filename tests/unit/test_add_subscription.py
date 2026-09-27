"""Покупка тарифа — всегда новый клиент с email, который ввёл пользователь"""
import datetime
from decimal import Decimal

import pytest

from application.errors import SubscriptionAlreadyExistsError
from infra.xui_vpn.shared.exceptions import ClientAlreadyExistsError
from infra.xui_vpn.shared.schemas import ClientPayload

from .conftest import make_client_obj, utcnow
from .test_payment_service import (  # noqa: F401 — фикстуры
    provider, subs, sender, service, make_service, METADATA, EXPIRE
)
from .test_subscriptions_service import _last_update_payload

DAY = datetime.timedelta(days=1)
NEW_SUB_METADATA = dict(METADATA, email='new@mail.ru')


# ---------- SubscriptionsTgBotService.add_subscription ----------

async def test_add_subscription_uses_given_email(subs_service, vpn_client):
    result = await subs_service.add_subscription(
        telegram_id=100, full_name='Иван', username='ivan', rate_id=2, email='new@mail.ru'
    )

    assert result.created is True
    payload: ClientPayload = vpn_client.clients.add.await_args.args[0]
    assert payload.email == 'new@mail.ru'
    assert payload.group == '2'
    assert payload.comment == 'Иван @ivan'
    vpn_client.clients.update.assert_not_awaited()


async def test_add_subscription_never_extends_existing_rate(subs_service, vpn_client):
    # У пользователя уже есть подписка на этот тариф — всё равно создаётся новый клиент
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(email='old@mail.ru', group='1')]

    result = await subs_service.add_subscription(
        telegram_id=100, full_name='Иван', username='ivan', rate_id=1, email='second@mail.ru'
    )

    assert result.created is True
    vpn_client.clients.update.assert_not_awaited()
    assert vpn_client.clients.add.await_args.args[0].email == 'second@mail.ru'


async def test_add_subscription_without_email_falls_back_to_tg_and_rate(subs_service, vpn_client):
    # Платежи, созданные до ввода email, содержат только rate_id
    await subs_service.add_subscription(telegram_id=100, full_name='Иван', username=None, rate_id=1)
    assert vpn_client.clients.add.await_args.args[0].email == '100_1'


async def test_add_subscription_existing_email_raises(subs_service, vpn_client):
    vpn_client.clients.get.return_value = make_client_obj(email='taken@mail.ru')

    with pytest.raises(SubscriptionAlreadyExistsError):
        await subs_service.add_subscription(
            telegram_id=100, full_name='Иван', username=None, rate_id=1, email='taken@mail.ru'
        )
    vpn_client.clients.add.assert_not_awaited()


async def test_add_subscription_panel_duplicate_raises(subs_service, vpn_client):
    # Почту заняли между проверкой и добавлением — 3x-ui ответит ошибкой
    vpn_client.clients.add.side_effect = ClientAlreadyExistsError('email already in use')

    with pytest.raises(SubscriptionAlreadyExistsError):
        await subs_service.add_subscription(
            telegram_id=100, full_name='Иван', username=None, rate_id=1, email='race@mail.ru'
        )


async def test_is_email_taken(subs_service, vpn_client):
    assert await subs_service.is_email_taken('free@mail.ru') is False
    vpn_client.clients.get.return_value = make_client_obj(email='taken@mail.ru')
    assert await subs_service.is_email_taken('taken@mail.ru') is True


# ---------- продление по email сохраняет клиента ----------

async def test_increase_by_email_keeps_uuid_sub_id_and_reenables(subs_service, vpn_client):
    client_obj = make_client_obj(email='a@b.c', enable=False, expiry=utcnow() - DAY)
    vpn_client.clients.get.return_value = client_obj

    new_expire = await subs_service.increase_subscription_by_email('a@b.c', expire_in=30 * DAY)

    _, payload = _last_update_payload(vpn_client)
    assert payload.uuid == str(client_obj.client.uuid)
    assert payload.sub_id == client_obj.client.sub_id
    assert payload.enable is True
    assert abs(new_expire - (utcnow() + 30 * DAY)) < datetime.timedelta(seconds=5)  # истекшая — от сейчас


async def test_increase_by_email_delayed_start_gets_longer_duration(subs_service, vpn_client):
    ten_days_ms = 10 * 86_400_000
    vpn_client.clients.get.return_value = make_client_obj(email='a@b.c', expiry=-ten_days_ms)

    await subs_service.increase_subscription_by_email('a@b.c', expire_in=30 * DAY)

    _, payload = _last_update_payload(vpn_client)
    assert payload.expiry_time == -(ten_days_ms + 30 * 86_400_000)


# ---------- PaymentsService ----------

async def test_create_payment_requires_email(service):
    with pytest.raises(ValueError):
        await service.create_payment(telegram_id=1, full_name='x', username=None, amount=1,
                                     description='d', rate_id=1)


async def test_create_payment_new_subscription(service, provider):
    url = await service.create_payment(telegram_id=100, full_name='Иван', username='ivan',
                                       amount=200, description='d', rate_id=1, email='new@mail.ru')

    assert url == 'https://pay.example/p1'
    kwargs = provider.create_payment.await_args.kwargs
    assert kwargs['amount'] == Decimal(200) and isinstance(kwargs['amount'], Decimal)
    assert kwargs['metadata'] == NEW_SUB_METADATA


async def test_fake_payment_activates_immediately(provider, subs, sender, cache, rates):
    service = make_service(provider, subs, sender, cache, rates, fake=True)

    url = await service.create_payment(telegram_id=100, full_name='Иван', username='ivan',
                                       amount=200, description='d', rate_id=1, email='new@mail.ru')

    assert url == 'https://example.com'
    provider.create_payment.assert_not_awaited()
    subs.add_subscription.assert_awaited_once()
    sender.on_payment.assert_awaited_once_with(100, email='new@mail.ru', expire_at=EXPIRE)


async def test_webhook_new_subscription_creates_client(service, subs, sender):
    await service.on_payment_webhook('p1', dict(NEW_SUB_METADATA))

    subs.add_subscription.assert_awaited_once_with(
        telegram_id=100, full_name='Иван', username='ivan', rate_id=1, email='new@mail.ru'
    )
    subs.increase_subscription_by_email.assert_not_awaited()  # rate_id + email — не продление
    sender.on_payment.assert_awaited_once_with(100, email='new@mail.ru', expire_at=EXPIRE)


async def test_webhook_legacy_rate_only_payment(service, subs, sender):
    await service.on_payment_webhook('p1', dict(METADATA))

    subs.add_subscription.assert_awaited_once_with(
        telegram_id=100, full_name='Иван', username='ivan', rate_id=1, email=None
    )


async def test_webhook_email_taken_notifies_and_stops_retries(service, subs, sender):
    subs.add_subscription.side_effect = SubscriptionAlreadyExistsError('exists')

    await service.on_payment_webhook('p1', dict(NEW_SUB_METADATA))
    await service.on_payment_webhook('p1', dict(NEW_SUB_METADATA))  # ретрай RollyPay

    assert subs.add_subscription.await_count == 1
    sender.on_error_payment.assert_awaited_once()
    assert 'new@mail.ru' in sender.on_error_payment.await_args.kwargs['message']
    sender.on_payment.assert_not_awaited()
