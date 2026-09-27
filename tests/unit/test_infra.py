import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic.v1 import ValidationError

from application.errors import SessionError
from config.settings import Settings
from infra.xui_vpn.clients.get import GetClient

from .conftest import make_client_obj


# ---------- GetClient ----------

@pytest.fixture
def session():
    session = MagicMock()
    session.get = AsyncMock()
    return session


@pytest.fixture
def get_client(session):
    return GetClient('https://panel.test', 'key', session)


async def test_get_client_found(get_client, session):
    obj = make_client_obj(email='a@b.c')
    session.get.return_value = {'success': True, 'msg': '', 'obj': json.loads(obj.model_dump_json(by_alias=True))}

    result = await get_client('a@b.c')

    assert result.client.email == 'a@b.c'


async def test_get_client_not_found_returns_none(get_client, session):
    session.get.return_value = {'success': False, 'msg': 'record not found', 'obj': None}
    assert await get_client('nope@x.y') is None


async def test_get_client_404_returns_none(get_client, session):
    session.get.side_effect = SessionError(status=404)
    assert await get_client('nope@x.y') is None


async def test_get_client_other_http_error_raises(get_client, session):
    session.get.side_effect = SessionError(status=500)
    with pytest.raises(SessionError):
        await get_client('a@b.c')


async def test_get_client_escapes_email_in_url(get_client, session):
    session.get.return_value = {'success': False, 'msg': '', 'obj': None}

    await get_client('../inbounds/list x')

    url = session.get.await_args.args[0]
    assert url == 'https://panel.test/panel/api/clients/get/..%2Finbounds%2Flist%20x'


# ---------- RedisCacheService ----------

async def test_redis_cache_json_roundtrip():
    storage = {}
    redis = MagicMock()
    redis.set = AsyncMock(side_effect=lambda k, v: storage.__setitem__(k, v))
    redis.get = AsyncMock(side_effect=lambda k: storage.get(k))

    with patch('infra.cache.redis.Redis.from_url', return_value=redis):
        from infra.cache.redis import RedisCacheService
        cache = RedisCacheService('redis://test')

    await cache.set('payment:processed:p1', True)
    await cache.set('obj', {'a': [1, 2]})

    assert await cache.get('payment:processed:p1') is True
    assert await cache.get('obj') == {'a': [1, 2]}
    assert await cache.get('missing') is None


def test_cache_factory_picks_backend():
    from infra.cache.factory import create_cache_service
    from infra.cache.memory import MemoryCacheService

    assert isinstance(create_cache_service(MagicMock(redis_url=None)), MemoryCacheService)
    with patch('infra.cache.redis.Redis.from_url'):
        from infra.cache.redis import RedisCacheService
        assert isinstance(create_cache_service(MagicMock(redis_url='redis://x')), RedisCacheService)


# ---------- Settings ----------

REQUIRED = dict(
    xui_api_key='k', xui_api_url='u', xui_sub_base_url='s', bot_token='t',
    yookassa_shop_id='1', yookassa_secret_key='y', rollypay_api_key='r', rollypay_secret_webhook='w',
    bot_url='b', support_url='s', privacy_policy_url='p', user_agreement_url='a', admin_log_chat_id=1,
)


def test_test_payment_is_required(monkeypatch):
    monkeypatch.delenv('TEST_PAYMENT', raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **REQUIRED)


def test_test_payment_from_env(monkeypatch):
    monkeypatch.setenv('TEST_PAYMENT', 'false')
    assert Settings(_env_file=None, **REQUIRED).test_payment is False
