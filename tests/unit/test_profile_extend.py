"""Кнопка «Продлить подписку» в профиле — платёж на конкретную подписку без ввода email"""
import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from presentation.bot.statistic.callback_datas import ExtendSubCallback, ProfilePageCallback
from presentation.bot.statistic.screens import client_statistic

from .conftest import make_client_obj

MSK = datetime.timedelta(hours=3)


def _clients(n: int):
    objs = [make_client_obj(email=f'u{i}@mail.ru') for i in range(1, n + 1)]
    for i, obj in enumerate(objs, start=1):
        obj.client.id = i
    return objs


def _extend_buttons(screen):
    return [
        button for row in screen.reply_markup.inline_keyboard for button in row
        if button.callback_data and button.callback_data.startswith('ext:')
    ]


# ---------- сервис ----------

async def test_get_user_subscription_by_sub_id(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(2)

    sub = await subs_service.get_user_subscription_by_sub_id(100, 'sub-u2@mail.ru')

    assert sub.email == 'u2@mail.ru'
    vpn_client.clients.get_by_tg_id.assert_awaited_once_with(100)


async def test_get_user_subscription_by_sub_id_foreign_or_missing(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(1)
    assert await subs_service.get_user_subscription_by_sub_id(100, 'sub-someone-else') is None


# ---------- экран ----------

async def test_profile_has_extend_button_for_sub(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(3)
    page = await subs_service.get_user_subscriptions_page(100, page=1, page_size=1)

    buttons = _extend_buttons(client_statistic(page, tz=MSK))

    assert len(buttons) == 1
    assert buttons[0].text == '💳 Продлить подписку'
    assert ExtendSubCallback.unpack(buttons[0].callback_data) == ExtendSubCallback(sub_id='sub-u2@mail.ru', page=1)


async def test_profile_extend_buttons_numbered_when_many_on_page(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(3)
    page = await subs_service.get_user_subscriptions_page(100, page=0, page_size=2)

    buttons = _extend_buttons(client_statistic(page, tz=MSK))

    assert [b.text for b in buttons] == ['💳 Продлить подписку #1', '💳 Продлить подписку #2']


async def test_profile_skips_button_if_sub_id_does_not_fit_callback(subs_service, vpn_client):
    obj = make_client_obj(email='long@mail.ru')
    obj.client.sub_id = 'x' * 80  # callback_data ограничен 64 байтами
    vpn_client.clients.get_by_tg_id.return_value = [obj]
    page = await subs_service.get_user_subscriptions_page(100, page=0, page_size=1)

    screen = client_statistic(page, tz=MSK)  # профиль не должен падать

    assert _extend_buttons(screen) == []


async def test_empty_profile_has_no_extend_button(subs_service):
    page = await subs_service.get_user_subscriptions_page(100, page=0, page_size=1)
    assert _extend_buttons(client_statistic(page, tz=MSK)) == []


# ---------- хендлер ----------

def _call():
    call = MagicMock()
    call.from_user = SimpleNamespace(id=100, username='ivan', full_name='Иван')
    call.answer = AsyncMock()
    return call


def _state():
    state = MagicMock()
    state.clear = AsyncMock()
    return state


async def test_extend_handler_creates_payment_for_sub(subs_service, vpn_client):
    from presentation.bot.payments.handlers import extend_sub_from_profile
    vpn_client.clients.get_by_tg_id.return_value = _clients(2)
    subs_by_email = MagicMock(get_subscription_amount_by_sub=AsyncMock(return_value=200))
    payments = MagicMock(create_payment=AsyncMock(return_value='https://pay.example/1'))

    with patch('presentation.bot.shared.screen.ScreenDef.answer', new=AsyncMock()) as answer:
        await extend_sub_from_profile(
            _call(), ExtendSubCallback(sub_id='sub-u2@mail.ru', page=1), _state(),
            subs_service=subs_service, subs_by_email_service=subs_by_email, payment_service=payments
        )

    kwargs = payments.create_payment.await_args.kwargs
    assert kwargs['email'] == 'u2@mail.ru'
    assert kwargs['amount'] == 200
    assert 'rate_id' not in kwargs  # продление, не новая подписка
    answer.assert_awaited_once()


async def test_extend_handler_back_returns_to_profile_page(subs_service, vpn_client):
    from presentation.bot.payments import screens
    vpn_client.clients.get_by_tg_id.return_value = _clients(1)
    sub = await subs_service.get_user_subscription_by_sub_id(100, 'sub-u1@mail.ru')

    screen = screens.pay_link_by_email(sub, 'https://pay.example/1',
                                       back_callback=ProfilePageCallback(page=3).pack())

    callbacks = [b.callback_data for row in screen.reply_markup.inline_keyboard for b in row]
    assert ProfilePageCallback(page=3).pack() in callbacks


async def test_extend_handler_missing_sub_alerts(subs_service, vpn_client):
    from presentation.bot.payments.handlers import extend_sub_from_profile
    payments = MagicMock(create_payment=AsyncMock())
    call = _call()

    await extend_sub_from_profile(
        call, ExtendSubCallback(sub_id='sub-deleted', page=0), _state(),
        subs_service=subs_service, subs_by_email_service=MagicMock(), payment_service=payments
    )

    payments.create_payment.assert_not_awaited()
    call.answer.assert_awaited_once()
    assert call.answer.await_args.kwargs.get('show_alert') is True
