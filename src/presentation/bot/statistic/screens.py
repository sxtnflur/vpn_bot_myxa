import datetime
import logging
from html import escape

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from application.subscriptions.dto import ExpandedSubscription, SubscriptionsPage
from presentation.bot.shared.screen import ScreenDef
from presentation.bot.shared.utils.date import bool_to_str, TIME_FORMAT, sub_end_to_string, date_to_local_tz
from presentation.bot.shared.utils.online import online_to_str
from presentation.bot.shared.utils.traffic import bytes_to_string, total_gb_to_string
from presentation.bot.statistic.callback_datas import ProfilePageCallback, UpdateProfileCallback, ExtendSubCallback

NOOP = 'noop'


def _sub_text(number: int, sub: ExpandedSubscription, tz: datetime.timedelta) -> str:
    inbounds = "\n".join([escape(inbound.name) for inbound in sub.inbounds])
    if inbounds:
        inbounds = '<blockquote>' + inbounds + '</blockquote>'
    else:
        inbounds = '-'

    exp_at = date_to_local_tz(sub.expire_at, tz=tz)

    return f'''
<b>Подписка #{number}</b>
EMAIL: <code>{escape(sub.email)}</code>
Ccылка: <code>{escape(sub.links.sub_url)}</code>

{inbounds}

🚨 Активен: {bool_to_str(sub.active)}
🌐 Статус соединения: {online_to_str(sub.is_online)}
📅 Дата окончания: {sub_end_to_string(exp_at)}
🔼 Загрузка: ↑{bytes_to_string(sub.load_up)}
🔽 Загрузка: ↓{bytes_to_string(sub.load_down)}
📊 Всего: ↑↓{bytes_to_string(sub.load_up + sub.load_down)} / {total_gb_to_string(sub.total_gb)}
'''


def _pagination_row(page: SubscriptionsPage) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            text='◀️' if page.has_prev else '·',
            callback_data=ProfilePageCallback(page=page.page - 1).pack() if page.has_prev else NOOP
        ),
        InlineKeyboardButton(
            text=f'{page.page + 1} / {page.pages}',
            callback_data=NOOP
        ),
        InlineKeyboardButton(
            text='▶️' if page.has_next else '·',
            callback_data=ProfilePageCallback(page=page.page + 1).pack() if page.has_next else NOOP
        ),
    ]


def _extend_button(
        number: int, sub: ExpandedSubscription, page: SubscriptionsPage, single: bool
) -> InlineKeyboardButton | None:
    try:
        callback_data = ExtendSubCallback(sub_id=sub.sub_id, page=page.page).pack()
    except ValueError:
        # subId не влез в 64 байта callback_data (или содержит ":") — продлить можно через ввод email
        logging.warning('Не удалось создать кнопку продления для subId %r', sub.sub_id)
        return None
    return InlineKeyboardButton(
        text='💳 Продлить подписку' if single else f'💳 Продлить подписку #{number}',
        callback_data=callback_data
    )


def client_statistic(page: SubscriptionsPage, tz: datetime.timedelta, header: str | None = None):
    """:param header: текст над профилем (например, «Оплата прошла успешно»)"""
    now = date_to_local_tz(datetime.datetime.utcnow(), tz=tz)

    if page.total == 0:
        body = 'У вас пока нет подписок.'
    else:
        body = '\n'.join(
            _sub_text(page.offset + i, sub, tz)
            for i, sub in enumerate(page.items, start=1)
        )

    ikb = []
    if page.pages > 1:
        ikb.append(_pagination_row(page))
    for i, sub in enumerate(page.items, start=1):
        button = _extend_button(page.offset + i, sub, page, single=len(page.items) == 1)
        if button:
            ikb.append([button])
    ikb.append([InlineKeyboardButton(
        text='🔄 Обновить',
        callback_data=UpdateProfileCallback(page=page.page).pack()
    )])
    if page.total == 0:
        ikb.append([InlineKeyboardButton(
            text='💵 Добавить / Продлить подписку', callback_data='buy'
        )])
    ikb.append([InlineKeyboardButton(
        text='В меню', callback_data='menu'
    )])

    return ScreenDef(
        text=(header + '\n' if header else '') + body + f'\n\n📋🔄 Обновлено: {now.strftime(TIME_FORMAT)}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=ikb)
    )
