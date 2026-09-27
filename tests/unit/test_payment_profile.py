"""После успешной оплаты бот показывает профиль на странице с оплаченной подпиской"""
import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from presentation.bot.message_senders.payment import AiogramPaymentMessageSender
from presentation.bot.statistic.callback_datas import ProfilePageCallback

from .conftest import make_client_obj

MSK = datetime.timedelta(hours=3)
EXPIRE = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc)


def _clients(n: int):
    objs = [make_client_obj(email=f'u{i}@mail.ru') for i in range(1, n + 1)]
    for i, obj in enumerate(objs, start=1):
        obj.client.id = i
    return objs


@pytest.fixture
def bot():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot


def _sender(bot, subs_service, page_size=1):
    return AiogramPaymentMessageSender(bot, tz=MSK, subs_service=subs_service, profile_page_size=page_size)


# ---------- сервис ----------

@pytest.mark.parametrize('email,page_size,expected_page', [
    ('u1@mail.ru', 1, 0), ('u3@mail.ru', 1, 2), ('u4@mail.ru', 2, 1), ('U5@MAIL.RU', 2, 2),
])
async def test_page_with_subscription(subs_service, vpn_client, email, page_size, expected_page):
    vpn_client.clients.get_by_tg_id.return_value = _clients(5)

    page = await subs_service.get_page_with_subscription(100, email=email, page_size=page_size)

    assert page.page == expected_page
    assert email.lower() in [s.email for s in page.items]


async def test_page_with_foreign_subscription_is_none(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(2)
    assert await subs_service.get_page_with_subscription(100, email='other@mail.ru', page_size=1) is None


async def test_add_subscription_returns_created_email(subs_service):
    result = await subs_service.add_subscription(telegram_id=100, full_name='Иван', username=None, rate_id=1)
    assert result.email == '100_1'


# ---------- сообщение после оплаты ----------

async def test_payment_shows_profile_on_page_with_paid_sub(bot, subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(3)

    await _sender(bot, subs_service).on_payment(100, email='u3@mail.ru', expire_at=EXPIRE)

    kwargs = bot.send_message.await_args.kwargs
    assert kwargs['chat_id'] == 100
    assert kwargs['text'].lstrip().startswith('✅ <b>Оплата прошла успешно</b>')
    assert 'u3@mail.ru' in kwargs['text'] and 'u1@mail.ru' not in kwargs['text']
    assert '<b>Подписка #3</b>' in kwargs['text']
    pagination = kwargs['reply_markup'].inline_keyboard[0]
    assert [b.text for b in pagination] == ['◀️', '3 / 3', '·']
    assert pagination[0].callback_data == ProfilePageCallback(page=1).pack()


async def test_payment_for_foreign_sub_shows_plain_success(bot, subs_service, vpn_client):
    # Продлил по email чужую подписку — в его профиле её нет
    vpn_client.clients.get_by_tg_id.return_value = _clients(1)

    await _sender(bot, subs_service).on_payment(100, email='friend@mail.ru', expire_at=EXPIRE)

    text = bot.send_message.await_args.kwargs['text']
    assert 'Оплата прошла успешно' in text and 'Дата окончания' in text
    assert 'Подписка #' not in text


async def test_payment_profile_error_falls_back_to_plain_success(bot, subs_service, vpn_client):
    # Подписка уже выдана: падение 3x-ui при построении профиля не должно выглядеть как ошибка оплаты
    vpn_client.clients.get_by_tg_id.side_effect = RuntimeError('3x-ui down')

    await _sender(bot, subs_service).on_payment(100, email='u1@mail.ru', expire_at=EXPIRE)

    assert 'Оплата прошла успешно' in bot.send_message.await_args.kwargs['text']


async def test_payment_message_for_unlimited_subscription(bot, subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = [make_client_obj(email='u1@mail.ru', expiry=0)]

    await _sender(bot, subs_service).on_payment(100, email='u1@mail.ru', expire_at=None)

    assert 'Дата окончания: ♾ Бессрочно' in bot.send_message.await_args.kwargs['text']
