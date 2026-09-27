import datetime

import pytest

from application.errors import IncreaseSubByEmailError
from application.subscriptions.service import SubscriptionsTgBotService
from infra.xui_vpn.shared.schemas import ClientPayload

from .conftest import make_client_obj, utcnow, to_ms

DAY = datetime.timedelta(days=1)
MINUTE_MS = 60_000


def _last_update_payload(vpn_client) -> tuple[str, ClientPayload]:
    call = vpn_client.clients.update.await_args
    email = call.kwargs.get('email', call.args[0] if call.args else None)
    payload = call.kwargs.get('client', call.args[1] if len(call.args) > 1 else None)
    return email, payload


# ---------- InboundsService ----------

async def test_inbounds_ids_without_filter(inbounds_service):
    assert await inbounds_service.get_inbounds_ids() == [1, 2, 3]


async def test_inbounds_ids_positive_filter(inbounds_service):
    assert await inbounds_service.get_inbounds_ids('wireguard') == [3]


async def test_inbounds_ids_negative_filter(inbounds_service):
    assert await inbounds_service.get_inbounds_ids('!wireguard') == [1, 2]


# ---------- комментарий клиента ----------

def test_create_comment_contains_username():
    assert SubscriptionsTgBotService._create_comment('Иван', 'ivan') == 'Иван @ivan'


def test_create_comment_without_username():
    assert SubscriptionsTgBotService._create_comment('Иван', None) == 'Иван'


# ---------- check_if_user_has_sub ----------

async def test_has_sub_true_for_active(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(expiry=utcnow() + 10 * DAY)]
    assert await subs_service.check_if_user_has_sub(100) is True


async def test_has_sub_false_for_expired(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(expiry=utcnow() - 10 * DAY)]
    assert await subs_service.check_if_user_has_sub(100) is False


# ---------- add_subscription ----------

async def test_add_subscription_creates_new_client(subs_service, vpn_client):
    result = await subs_service.add_subscription(
        telegram_id=100, full_name='Иван', username='ivan', rate_id=1
    )

    assert result.created is True
    vpn_client.clients.add.assert_awaited_once()
    payload: ClientPayload = vpn_client.clients.add.await_args.args[0]
    assert vpn_client.clients.add.await_args.kwargs['inbound_ids'] == [1, 2]  # rate 1 = !wireguard
    assert payload.tg_id == 100
    assert payload.group == '1'
    expected = to_ms(utcnow() + 30 * DAY)
    assert abs(payload.expiry_time - expected) < MINUTE_MS
    assert payload.expiry_time == to_ms(result.expire_at)


async def test_add_subscription_wifi_rate_uses_wireguard_inbounds(subs_service, vpn_client):
    await subs_service.add_subscription(telegram_id=100, full_name='Иван', username=None, rate_id=2)
    assert vpn_client.clients.add.await_args.kwargs['inbound_ids'] == [3]


async def test_add_subscription_extends_active(subs_service, vpn_client):
    old_expiry = utcnow() + 10 * DAY
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(expiry=old_expiry, group='1')]

    result = await subs_service.add_subscription(telegram_id=100, full_name='Иван', username='ivan', rate_id=1)

    assert result.created is False
    vpn_client.clients.add.assert_not_awaited()
    email, payload = _last_update_payload(vpn_client)
    assert email == '100'
    assert abs(payload.expiry_time - to_ms(old_expiry + 30 * DAY)) < 1000
    assert payload.enable is True


async def test_add_subscription_expired_counts_from_now(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(expiry=utcnow() - 100 * DAY, group='1')]

    await subs_service.add_subscription(telegram_id=100, full_name='Иван', username='ivan', rate_id=1)

    _, payload = _last_update_payload(vpn_client)
    assert abs(payload.expiry_time - to_ms(utcnow() + 30 * DAY)) < MINUTE_MS


@pytest.mark.parametrize('rate_id', [1, 2])
async def test_new_client_email_is_tg_id_and_rate(subs_service, vpn_client, rate_id):
    await subs_service.add_subscription(telegram_id=100, full_name='Иван', username='ivan', rate_id=rate_id)

    payload: ClientPayload = vpn_client.clients.add.await_args.args[0]
    assert payload.email == f'100_{rate_id}'


async def test_second_rate_creates_separate_client(subs_service, vpn_client):
    # старый клиент первого тарифа (email = tg_id) — второй тариф не должен с ним конфликтовать
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(email='100', group='1')]

    result = await subs_service.add_subscription(telegram_id=100, full_name='Иван', username='ivan', rate_id=2)

    assert result.created is True
    vpn_client.clients.update.assert_not_awaited()
    payload: ClientPayload = vpn_client.clients.add.await_args.args[0]
    assert payload.email == '100_2'
    assert payload.group == '2'


async def test_legacy_client_of_same_rate_is_extended_not_duplicated(subs_service, vpn_client):
    # клиенты, созданные до смены формата (email = tg_id), продлеваются как раньше
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(email='100', group='1')]

    await subs_service.add_subscription(telegram_id=100, full_name='Иван', username='ivan', rate_id=1)

    vpn_client.clients.add.assert_not_awaited()
    email, _ = _last_update_payload(vpn_client)
    assert email == '100'


async def test_extend_keeps_client_limits(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(group='1', limit_ip=3, total_gb=50 * 1024 ** 3)]

    await subs_service.add_subscription(telegram_id=100, full_name='Иван', username='ivan', rate_id=1)

    _, payload = _last_update_payload(vpn_client)
    assert payload.limit_ip == 3
    assert payload.total_gb == 50 * 1024 ** 3


# ---------- increase_subscription_by_email ----------

async def test_increase_by_email_extends(subs_service, vpn_client):
    old_expiry = utcnow() + 5 * DAY
    vpn_client.clients.get.return_value = make_client_obj(email='a@b.c', expiry=old_expiry)

    new_expire = await subs_service.increase_subscription_by_email('a@b.c', expire_in=30 * DAY)

    email, payload = _last_update_payload(vpn_client)
    assert email == 'a@b.c'
    assert abs(payload.expiry_time - to_ms(old_expiry + 30 * DAY)) < 1000
    assert payload.expiry_time == to_ms(new_expire)
    assert payload.group == '1'


async def test_increase_by_email_keeps_comment(subs_service, vpn_client):
    vpn_client.clients.get.return_value = make_client_obj(email='a@b.c', comment='Иван @ivan')

    await subs_service.increase_subscription_by_email('a@b.c', expire_in=30 * DAY)

    _, payload = _last_update_payload(vpn_client)
    assert payload.comment == 'Иван @ivan'


async def test_increase_by_email_unknown_email(subs_service, vpn_client):
    vpn_client.clients.get.return_value = None
    with pytest.raises(IncreaseSubByEmailError):
        await subs_service.increase_subscription_by_email('nope@x.y', expire_in=30 * DAY)


# ---------- чтение подписок ----------

async def test_get_user_subscriptions_expands(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(email='100', inbound_ids=[1, 3, 99])]
    vpn_client.clients.onlines.return_value = ['100']

    subs = await subs_service.get_user_subscriptions(100)

    assert len(subs) == 1
    sub = subs[0]
    assert [i.id for i in sub.inbounds] == [1, 3]  # несуществующий inbound 99 отброшен
    assert sub.is_online is True
    assert sub.load_up == 1 and sub.load_down == 2
    assert sub.links.sub_url == 'https://sub.example/sub-100'
    assert sub.links.happ_url == 'happ://import?url=https://sub.example/sub-100'
    assert sub.expire_at.tzinfo is None  # храним naive UTC


@pytest.mark.xfail(strict=True, raises=AttributeError,
                   reason='BUG: get_subscription передаёт None в _expand_sub, если подписки нет')
async def test_get_subscription_missing_returns_none(subs_service):
    assert await subs_service.get_subscription(100, rate_id=1) is None


@pytest.mark.xfail(strict=True, raises=IndexError,
                   reason='BUG: get_subscription_links берёт users[0] без проверки')
async def test_get_subscription_links_without_clients(subs_service):
    assert await subs_service.get_subscription_links(100) == []


# ---------- set_existing_client_rate / Client.to_client_payload ----------

def test_to_client_payload_expiry_in_ms():
    expiry = utcnow() + 10 * DAY
    client = make_client_obj(expiry=expiry).client
    assert abs(client.to_client_payload().expiry_time - to_ms(expiry)) < 1000


def test_to_client_payload_keeps_limit_ip():
    client = make_client_obj(limit_ip=3).client
    assert client.to_client_payload().limit_ip == 3


async def test_set_existing_client_rate_moves_inbounds(subs_service, vpn_client):
    client = make_client_obj(email='100', group=None).client

    await subs_service.set_existing_client_rate(client, rate_id=2)

    vpn_client.clients.bulk_attach.assert_awaited_once_with(emails=['100'], inbound_ids=[3])
    vpn_client.clients.bulk_detach.assert_awaited_once_with(emails=['100'], inbound_ids=[1, 2])
    _, payload = _last_update_payload(vpn_client)
    assert payload.group == '2'


async def test_extend_keeps_uuid_sub_id_and_reenables(subs_service, vpn_client):
    client_obj = make_client_obj(email='100', group='1', enable=False, expiry=utcnow() - DAY)
    vpn_client.clients.get_by_tg_id.return_value = [client_obj]

    await subs_service.add_subscription(telegram_id=100, full_name='Иван', username='ivan', rate_id=1)

    _, payload = _last_update_payload(vpn_client)
    assert payload.uuid == str(client_obj.client.uuid)
    assert payload.sub_id == client_obj.client.sub_id
    assert payload.enable is True


async def test_increase_by_email_keeps_limits(subs_service, vpn_client):
    vpn_client.clients.get.return_value = make_client_obj(email='a@b.c', limit_ip=2, total_gb=10 * 1024 ** 3)

    await subs_service.increase_subscription_by_email('a@b.c', expire_in=30 * DAY)

    _, payload = _last_update_payload(vpn_client)
    assert payload.limit_ip == 2
    assert payload.total_gb == 10 * 1024 ** 3


# ---------- бессрочные клиенты и отложенный старт ----------

def test_client_expire_at_variants():
    assert make_client_obj(expiry=0).client.expire_at is None
    delayed = make_client_obj(expiry=-30 * 86_400_000).client.expire_at
    assert abs((delayed - utcnow()) - 30 * DAY) < datetime.timedelta(seconds=5)
    fixed = utcnow() + 3 * DAY
    assert abs(make_client_obj(expiry=fixed).client.expire_at - fixed) < datetime.timedelta(milliseconds=1)


async def test_has_sub_true_for_unlimited(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(expiry=0)]
    assert await subs_service.check_if_user_has_sub(100) is True


async def test_unlimited_client_stays_unlimited_on_payment(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(group='1', expiry=0)]

    result = await subs_service.add_subscription(telegram_id=100, full_name='Иван', username='ivan', rate_id=1)

    assert result.created is False
    assert result.expire_at is None
    _, payload = _last_update_payload(vpn_client)
    assert payload.expiry_time == 0


async def test_unlimited_client_by_email_stays_unlimited(subs_service, vpn_client):
    vpn_client.clients.get.return_value = make_client_obj(email='a@b.c', expiry=0)

    assert await subs_service.increase_subscription_by_email('a@b.c', expire_in=30 * DAY) is None
    _, payload = _last_update_payload(vpn_client)
    assert payload.expiry_time == 0


async def test_delayed_start_client_gets_longer_duration(subs_service, vpn_client):
    ten_days_ms = 10 * 86_400_000
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(group='1', expiry=-ten_days_ms)]

    result = await subs_service.add_subscription(telegram_id=100, full_name='Иван', username='ivan', rate_id=1)

    _, payload = _last_update_payload(vpn_client)
    assert payload.expiry_time == -(ten_days_ms + 30 * 86_400_000)  # отсчёт всё ещё с первого подключения
    assert abs((result.expire_at - utcnow()) - 40 * DAY) < datetime.timedelta(seconds=5)


async def test_profile_shows_unlimited(subs_service, vpn_client):
    from presentation.bot.statistic.screens import client_statistic
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(expiry=0)]

    subs = await subs_service.get_user_subscriptions(100)

    assert subs[0].expire_at is None
    assert 'Дата окончания: ♾ Бессрочно' in client_statistic(subs, tz=datetime.timedelta(hours=3)).text
