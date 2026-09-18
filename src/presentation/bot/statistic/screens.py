import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from application.subscriptions.dto import User, SubscriptionLinks
from presentation.bot.shared.screen import ScreenDef
from presentation.bot.shared.utils.date import bool_to_str, TIME_FORMAT, sub_end_to_string, date_to_local_tz
from presentation.bot.shared.utils.online import online_to_str
from presentation.bot.shared.utils.traffic import bytes_to_string, total_gb_to_string


def client_statistic(client: User, sub_links: SubscriptionLinks, tz: datetime.timedelta):
    inbounds = "\n".join([inbound.name for inbound in client.inbounds])
    if inbounds:
        inbounds = '\n<blockquote>' + inbounds + '</blockquote>\n'
    else:
        inbounds = '-'

    now = date_to_local_tz(datetime.datetime.utcnow(), tz=tz)
    exp_at = date_to_local_tz(client.expire_at, tz=tz)

    return ScreenDef(
        f'''
{inbounds}
🚨 Активен: {bool_to_str(client.active)}
🌐 Статус соединения: {online_to_str(client.is_online)}
📅 Дата окончания: {sub_end_to_string(exp_at)}
🔼 Загрузка: ↑{bytes_to_string(client.load_up)}
🔽 Загрузка: ↓{bytes_to_string(client.load_down)}
📊 Всего: ↑↓{bytes_to_string(client.load_up + client.load_down)} / {total_gb_to_string(client.total_gb)}

📋🔄 Обновлено: {now.strftime(TIME_FORMAT)}
''',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='🔄 Обновить',
                callback_data='update_statistic'
            )],
            [InlineKeyboardButton(
                text='Ссылка на подписку',
                copy_text=CopyTextButton(text=sub_links.sub_url)
            )],
            [InlineKeyboardButton(
                text='В меню', callback_data='menu'
            )]
        ])
    )
