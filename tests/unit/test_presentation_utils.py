import datetime

import pytest

from application.subscriptions.dto import ExpandedSubscription, SubscriptionLinks, Subscription
from presentation.bot.shared.utils.date import _plural, _DAYS, datetime_to_td_string, sub_end_to_string
from presentation.bot.shared.utils.traffic import bytes_to_string, total_gb_to_string, gb_to_bytes, GB
from presentation.bot.start import screens as start_screens
from presentation.bot.statistic.screens import client_statistic

MSK = datetime.timedelta(hours=3)


@pytest.mark.parametrize('n,form', [
    (1, 'День'), (2, 'Дня'), (4, 'Дня'), (5, 'Дней'), (11, 'Дней'),
    (12, 'Дней'), (21, 'День'), (22, 'Дня'), (111, 'Дней'), (0, 'Дней'),
])
def test_plural(n, form):
    assert _plural(n, _DAYS) == form


def test_td_string():
    date = datetime.datetime.utcnow() + datetime.timedelta(days=2, hours=3, minutes=5, seconds=30)
    assert datetime_to_td_string(date) == '2 Дня 3 Часа 5 Минут'


def test_td_string_past_is_zero():
    assert datetime_to_td_string(datetime.datetime.utcnow() - datetime.timedelta(days=1)) == '0 Минут'


def test_sub_end_expired_and_unlimited():
    assert sub_end_to_string(None) == '♾ Бессрочно'
    assert sub_end_to_string(datetime.datetime.utcnow() - datetime.timedelta(seconds=1)) == 'Истекла'


def test_sub_end_accepts_aware():
    date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1, seconds=30)
    assert sub_end_to_string(date).endswith('(1 День)')


@pytest.mark.parametrize('value,expected', [
    (0, '0Б'), (512, '512Б'), (GB, '1ГБ'), (int(1.5 * GB), '1.5ГБ'), (gb_to_bytes(2.25), '2.25ГБ'),
])
def test_bytes_to_string(value, expected):
    assert bytes_to_string(value) == expected


def test_total_gb_unlimited():
    assert total_gb_to_string(0) == '♾ Безлимит'
    assert total_gb_to_string(10 * GB) == '10ГБ'


def test_subscription_dto_normalizes_to_naive_utc():
    aware = datetime.datetime(2030, 1, 1, 12, tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
    sub = Subscription.from_client(email='e', telegram_id=1, expire_at=aware, sub_id='s',
                                   enable=True, inbound_ids=[], group='2')
    assert sub.expire_at == datetime.datetime(2030, 1, 1, 9)
    assert sub.rate_id == 2


def _expanded(expire_at: datetime.datetime, email: str = '100') -> ExpandedSubscription:
    return ExpandedSubscription(
        email=email, expire_at=expire_at, sub_id='s', active=True, load_up=0, load_down=0, total_gb=0,
        inbounds=[], is_online=False, links=SubscriptionLinks(sub_url='https://sub/s', happ_url='happ://x'),
    )


@pytest.mark.xfail(strict=True, reason='BUG: дата сдвигается на tz ДО sub_end_to_string, '
                                       'а та сравнивает с utcnow — остаток завышен на 3 часа, '
                                       'подписка показывается активной 3 часа после окончания')
def test_statistic_remaining_time_not_shifted_by_tz():
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(days=10, seconds=30)
    text = client_statistic([_expanded(expire_at)], tz=MSK).text
    assert '(10 Дней)' in text


def test_start_screen_escapes_name():
    text = start_screens.start('Вася <3', privacy_policy_link='https://p', user_agreement_link='https://u').text
    assert 'Вася &lt;3' in text
