import pytest

from presentation.bot.shared.utils.email import normalize_email


@pytest.mark.parametrize('text,expected', [
    ('user@mail.ru', 'user@mail.ru'),
    ('  User.Name+vpn@Gmail.COM \n', 'user.name+vpn@gmail.com'),
])
def test_valid_emails(text, expected):
    assert normalize_email(text) == expected


@pytest.mark.parametrize('text', [
    '', 'AAZZHH', 'user@', '@mail.ru', 'user@mail', 'us er@mail.ru', 'a@b@c.ru',
    '../x@mail.ru', 'a\\b@mail.ru', 'a' * 60 + '@mail.ru',
])
def test_invalid_emails(text):
    assert normalize_email(text) is None
