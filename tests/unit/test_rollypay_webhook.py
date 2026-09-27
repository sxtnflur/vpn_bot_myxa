import hashlib
import hmac
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from infra.rollypay.client import RollyPay
from presentation.api.payment import create_router

SECRET = 'whsec_test'
PATH = '/payment/rollypay'


def sign(body: bytes, timestamp: str = '1700000000', secret: str = SECRET) -> dict:
    signature = hmac.new(secret.encode(), timestamp.encode() + b'.' + body, hashlib.sha256).hexdigest()
    return {'X-Timestamp': timestamp, 'X-Signature': signature, 'Content-Type': 'application/json'}


def paid_body(**overrides) -> bytes:
    payload = {
        'event_type': 'payment.paid',
        'status': 'paid',
        'payment_id': 'p1',
        'order_id': 'o1',
        'amount': 200.0,
        'currency': 'RUB',
        'test': False,
        'metadata': {'telegram_id': 100, 'full_name': 'Иван', 'username': 'ivan', 'rate_id': 1},
    }
    payload.update(overrides)
    return json.dumps(payload).encode()


@pytest.fixture
def rolly_pay():
    return RollyPay(api_key='k', base_url='https://rollypay.test', secret_webhook=SECRET, session=MagicMock())


@pytest.fixture
def payments_service():
    service = MagicMock()
    service.on_payment_webhook = AsyncMock()
    return service


@pytest.fixture
async def client(rolly_pay, payments_service):
    app = web.Application()
    app.add_routes(create_router(payments_service=payments_service, rolly_pay=rolly_pay))
    async with TestClient(TestServer(app)) as client:
        yield client


# ---------- RollyPay.validate_sign ----------

def test_validate_sign_ok(rolly_pay):
    body = paid_body()
    headers = sign(body)
    assert rolly_pay.validate_sign(body, headers['X-Timestamp'], headers['X-Signature']) is True
    assert rolly_pay.validate_sign(body.decode(), headers['X-Timestamp'], headers['X-Signature']) is True


def test_validate_sign_wrong_secret(rolly_pay):
    body = paid_body()
    headers = sign(body, secret='other')
    assert rolly_pay.validate_sign(body, headers['X-Timestamp'], headers['X-Signature']) is False


def test_validate_sign_tampered_body(rolly_pay):
    headers = sign(paid_body())
    assert rolly_pay.validate_sign(paid_body(amount=1.0), headers['X-Timestamp'], headers['X-Signature']) is False


@pytest.mark.parametrize('timestamp,signature', [(None, 'x'), ('1', None), ('', '')])
def test_validate_sign_missing_headers(rolly_pay, timestamp, signature):
    assert rolly_pay.validate_sign(b'{}', timestamp, signature) is False


# ---------- HTTP-хендлер вебхука ----------

async def test_paid_webhook_activates_subscription(client, payments_service):
    body = paid_body()
    resp = await client.post(PATH, data=body, headers=sign(body))

    assert resp.status == 200
    payments_service.on_payment_webhook.assert_awaited_once()
    kwargs = payments_service.on_payment_webhook.await_args.kwargs
    assert kwargs['payment_id'] == 'p1'
    assert kwargs['metadata']['rate_id'] == 1


async def test_paid_webhook_amount_as_string(client, payments_service):
    # В доке RollyPay amount приходит строкой: "1500.00"
    body = paid_body(amount='1500.00')
    resp = await client.post(PATH, data=body, headers=sign(body))

    assert resp.status == 200
    payments_service.on_payment_webhook.assert_awaited_once()


@pytest.mark.parametrize('event_type,status', [
    ('payment.created', 'created'), ('payment.canceled', 'canceled'), ('payment.expired', 'expired'),
])
async def test_not_paid_events_acknowledged_without_processing(client, payments_service, event_type, status):
    # Не-2xx заставит RollyPay ретраить событие до 8 раз
    body = paid_body(event_type=event_type, status=status)
    resp = await client.post(PATH, data=body, headers=sign(body))

    assert resp.status == 200
    payments_service.on_payment_webhook.assert_not_awaited()


async def test_signed_invalid_body_400(client, payments_service):
    body = b'{"foo": 1}'
    resp = await client.post(PATH, data=body, headers=sign(body))

    assert resp.status == 400
    payments_service.on_payment_webhook.assert_not_awaited()


async def test_webhook_bad_signature_403(client, payments_service):
    body = paid_body()
    resp = await client.post(PATH, data=body, headers=sign(body, secret='attacker'))

    assert resp.status == 403
    payments_service.on_payment_webhook.assert_not_awaited()


async def test_webhook_without_signature_headers_403(client, payments_service):
    resp = await client.post(PATH, data=paid_body(), headers={'Content-Type': 'application/json'})

    assert resp.status == 403
    payments_service.on_payment_webhook.assert_not_awaited()


async def test_webhook_unsigned_garbage_403(client, payments_service):
    resp = await client.post(PATH, data=b'{"foo": 1}', headers={'X-Timestamp': '1', 'X-Signature': 'x'})

    assert resp.status == 403


async def test_webhook_rejects_get(client):
    resp = await client.get(PATH)
    assert resp.status == 405
