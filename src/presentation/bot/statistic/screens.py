import datetime
from html import escape

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from application.subscriptions.dto import ExpandedSubscription
from presentation.bot.shared.screen import ScreenDef
from presentation.bot.shared.utils.date import bool_to_str, TIME_FORMAT, sub_end_to_string, date_to_local_tz
from presentation.bot.shared.utils.online import online_to_str
from presentation.bot.shared.utils.traffic import bytes_to_string, total_gb_to_string


def client_statistic(subs: list[ExpandedSubscription], tz: datetime.timedelta):
    now = date_to_local_tz(datetime.datetime.utcnow(), tz=tz)
    texts = []
    for i, sub in enumerate(subs, start=1):
        inbounds = "\n".join([escape(inbound.name) for inbound in sub.inbounds])
        if inbounds:
            inbounds = '<blockquote>' + inbounds + '</blockquote>'
        else:
            inbounds = '-'

        exp_at = date_to_local_tz(sub.expire_at, tz=tz)

        texts.append(
            f'''
<b>Подписка #{i}</b>
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
        )

    return ScreenDef(
        text='\n'.join(texts) + f'\n\n📋🔄 Обновлено: {now.strftime(TIME_FORMAT)}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='🔄 Обновить',
                callback_data='update_statistic'
            )],
            [InlineKeyboardButton(
                text='В меню', callback_data='menu'
            )]
        ])
    )
