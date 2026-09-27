import datetime

import pytest

from presentation.bot.statistic.callback_datas import ProfilePageCallback, UpdateProfileCallback
from presentation.bot.statistic.screens import client_statistic, NOOP

from .conftest import make_client_obj

MSK = datetime.timedelta(hours=3)


def _clients(n: int):
    objs = [make_client_obj(email=f'u{i}@mail.ru') for i in range(1, n + 1)]
    for i, obj in enumerate(objs, start=1):
        obj.client.id = i
    return objs


def _buttons(screen):
    return [button for row in screen.reply_markup.inline_keyboard for button in row]


def _callbacks(screen):
    return [button.callback_data for button in _buttons(screen)]


# ---------- сервис ----------

async def test_page_slices_and_expands_only_page(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(5)

    page = await subs_service.get_user_subscriptions_page(100, page=1, page_size=2)

    assert [s.email for s in page.items] == ['u3@mail.ru', 'u4@mail.ru']
    assert (page.page, page.pages, page.total, page.offset) == (1, 3, 5, 2)
    assert page.has_prev and page.has_next
    # трафик запрашивается только для подписок текущей страницы
    assert [c.kwargs['email'] for c in vpn_client.clients.traffic.await_args_list] == ['u3@mail.ru', 'u4@mail.ru']


async def test_page_order_is_stable_by_client_id(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = list(reversed(_clients(3)))

    page = await subs_service.get_user_subscriptions_page(100, page=0, page_size=1)

    assert page.items[0].email == 'u1@mail.ru'


async def test_last_page_partial(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(5)

    page = await subs_service.get_user_subscriptions_page(100, page=2, page_size=2)

    assert [s.email for s in page.items] == ['u5@mail.ru']
    assert page.has_prev and not page.has_next


@pytest.mark.parametrize('requested,expected', [(-3, 0), (99, 2)])
async def test_out_of_range_page_is_clamped(subs_service, vpn_client, requested, expected):
    # Например, подписку удалили, а у пользователя открыта последняя страница
    vpn_client.clients.get_by_tg_id.return_value = _clients(3)

    page = await subs_service.get_user_subscriptions_page(100, page=requested, page_size=1)

    assert page.page == expected
    assert len(page.items) == 1


async def test_no_subscriptions(subs_service, vpn_client):
    page = await subs_service.get_user_subscriptions_page(100, page=0, page_size=1)

    assert page.items == [] and page.total == 0 and page.pages == 1
    assert not page.has_prev and not page.has_next


async def test_invalid_page_size(subs_service):
    with pytest.raises(ValueError):
        await subs_service.get_user_subscriptions_page(100, page=0, page_size=0)


# ---------- экран ----------

async def test_screen_single_page_has_no_pagination(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(1)
    page = await subs_service.get_user_subscriptions_page(100, page=0, page_size=1)

    screen = client_statistic(page, tz=MSK)

    assert NOOP not in _callbacks(screen)
    assert UpdateProfileCallback(page=0).pack() in _callbacks(screen)
    assert '<b>Подписка #1</b>' in screen.text


async def test_screen_middle_page(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(3)
    page = await subs_service.get_user_subscriptions_page(100, page=1, page_size=1)

    screen = client_statistic(page, tz=MSK)

    first_row = screen.reply_markup.inline_keyboard[0]
    assert [b.text for b in first_row] == ['◀️', '2 / 3', '▶️']
    assert first_row[0].callback_data == ProfilePageCallback(page=0).pack()
    assert first_row[2].callback_data == ProfilePageCallback(page=2).pack()
    assert UpdateProfileCallback(page=1).pack() in _callbacks(screen)
    assert '<b>Подписка #2</b>' in screen.text  # сквозная нумерация
    assert 'u2@mail.ru' in screen.text and 'u1@mail.ru' not in screen.text


async def test_screen_first_page_disables_prev(subs_service, vpn_client):
    vpn_client.clients.get_by_tg_id.return_value = _clients(2)
    page = await subs_service.get_user_subscriptions_page(100, page=0, page_size=1)

    first_row = client_statistic(page, tz=MSK).reply_markup.inline_keyboard[0]

    assert first_row[0].callback_data == NOOP
    assert first_row[2].callback_data == ProfilePageCallback(page=1).pack()
    assert all(b.text.strip() for b in first_row)  # Telegram не принимает пустой текст кнопки


async def test_screen_empty_offers_to_buy(subs_service, vpn_client):
    page = await subs_service.get_user_subscriptions_page(100, page=0, page_size=1)

    screen = client_statistic(page, tz=MSK)

    assert 'нет подписок' in screen.text
    assert 'rates' in _callbacks(screen)
    assert 'increase_sub_by_email' not in _callbacks(screen)  # продление только кнопкой у подписки
