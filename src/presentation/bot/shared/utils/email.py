import re

MAX_EMAIL_LENGTH = 64

# Без пробелов и слэшей: email попадает в URL запросов к 3x-ui
_EMAIL_RE = re.compile(r'^[^@\s/\\]+@[^@\s/\\]+\.[^@\s/\\]+$')


def normalize_email(text: str) -> str | None:
    """
    :return: email в нижнем регистре или None, если текст не похож на почту
    """
    email = text.strip().lower()
    if len(email) > MAX_EMAIL_LENGTH or not _EMAIL_RE.match(email):
        return None
    return email
