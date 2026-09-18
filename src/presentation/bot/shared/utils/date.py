import datetime

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

_DAYS = ('День', 'Дня', 'Дней')
_HOURS = ('Час', 'Часа', 'Часов')
_MINUTES = ('Минута', 'Минуты', 'Минут')


def bool_to_str(v: bool):
    return '✅ Да' if v else '❌ Нет'


def _plural(n: int, forms: tuple[str, str, str]) -> str:
    if 11 <= n % 100 <= 14:
        return forms[2]
    last = n % 10
    if last == 1:
        return forms[0]
    if 2 <= last <= 4:
        return forms[1]
    return forms[2]


def sub_end_to_string(date: datetime.datetime | None):
    if date is None or date < datetime.datetime.utcnow():
        return 'Истекла'
    return f'{date.strftime(TIME_FORMAT)} ({datetime_to_td_string(date)})'


def datetime_to_td_string(date: datetime.datetime):
    td = max(date.replace(tzinfo=None) - datetime.datetime.utcnow(), datetime.timedelta(0))
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes = remainder // 60

    parts = [
        f'{value} {_plural(value, forms)}'
        for value, forms in ((days, _DAYS), (hours, _HOURS), (minutes, _MINUTES))
        if value
    ]
    return ' '.join(parts) or f'0 {_MINUTES[2]}'


def date_to_local_tz(date: datetime.datetime, tz: datetime.timedelta):
    return date + tz
