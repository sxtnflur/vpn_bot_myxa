import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.rates import RatesService
from application.subscriptions.inbounds_service import InboundsService
from application.subscriptions.service import SubscriptionsTgBotService
from infra.cache.memory import MemoryCacheService
from infra.xui_vpn.clients.get.schemas import GetClientObject
from infra.xui_vpn.inbounds.options.schemas import InboundOption

UTC = datetime.timezone.utc


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(UTC)


def to_ms(dt: datetime.datetime) -> int:
    return round(dt.timestamp() * 1000)


def make_client_obj(
        email: str = '100',
        tg_id: int = 100,
        expiry: datetime.datetime | int | None = None,
        group: str | None = '1',
        comment: str | None = 'Иван @ivan',
        inbound_ids: list[int] | None = None,
        enable: bool = True,
        limit_ip: int = 3,
        total_gb: int = 0,
) -> GetClientObject:
    if expiry is None:
        expiry = utcnow() + datetime.timedelta(days=10)
    expiry_ms = expiry if isinstance(expiry, int) else to_ms(expiry)
    now_ms = to_ms(utcnow())
    return GetClientObject.model_validate({
        'client': {
            'id': 1,
            'email': email,
            'subId': f'sub-{email}',
            'uuid': '6a1b2c3d-0000-4000-8000-000000000001',
            'limitIp': limit_ip,
            'totalGB': total_gb,
            'expiryTime': expiry_ms,
            'enable': enable,
            'tgId': tg_id,
            'group': group,
            'comment': comment,
            'reset': 0,
            'resetDay': 0,
            'resetMax': 0,
            'createdAt': now_ms,
            'updatedAt': now_ms,
        },
        'inboundIds': inbound_ids if inbound_ids is not None else [1, 2],
        'usedTraffic': 0,
    })


def make_inbound(id: int, protocol: str, remark: str | None = None) -> InboundOption:
    return InboundOption.model_validate({
        'id': id,
        'remark': remark or f'{protocol}-{id}',
        'tag': f'inbound-{id}',
        'protocol': protocol,
        'port': 1000 + id,
        'enable': True,
        'tlsFlowCapable': False,
        'ssMethod': '',
    })


@pytest.fixture
def inbounds():
    return [make_inbound(1, 'vless'), make_inbound(2, 'trojan'), make_inbound(3, 'wireguard')]


@pytest.fixture
def vpn_client(inbounds):
    """Фейковый XUIVPN: у каждого метода AsyncMock, по умолчанию «клиентов нет»."""
    clients = SimpleNamespace(
        get=AsyncMock(return_value=None),
        get_by_tg_id=AsyncMock(return_value=[]),
        add=AsyncMock(return_value=None),
        update=AsyncMock(return_value=None),
        traffic=AsyncMock(return_value=SimpleNamespace(up=1, down=2, total=0)),
        onlines=AsyncMock(return_value=[]),
        bulk_attach=AsyncMock(),
        bulk_detach=AsyncMock(),
        sub_links=AsyncMock(return_value=[]),
    )
    return SimpleNamespace(
        clients=clients,
        inbounds=SimpleNamespace(options=AsyncMock(return_value=inbounds)),
        create_sub_link=MagicMock(side_effect=lambda sub_id: f'https://sub.example/{sub_id}'),
    )


@pytest.fixture
def rates():
    return RatesService()


@pytest.fixture
def inbounds_service(vpn_client):
    return InboundsService(vpn_client=vpn_client)


@pytest.fixture
def subs_service(vpn_client, rates, inbounds_service):
    return SubscriptionsTgBotService(vpn_client=vpn_client, rates=rates, inbounds_service=inbounds_service)


@pytest.fixture
def cache():
    return MemoryCacheService()
