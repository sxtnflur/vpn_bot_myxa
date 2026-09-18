from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from application.subscriptions.dto import SubscriptionLinks
from presentation.bot.shared.screen import ScreenDef


def my_sub_links(sub_links: SubscriptionLinks):
    text = '<i>Ссылки на подписки:</i>\n\n' \
           f'<b>Happ</b>: <code>{sub_links.happ_url}</code>'

    return ScreenDef(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Скопировать ссылку на подписку',
                copy_text=CopyTextButton(text=sub_links.sub_url)
            )],
            [InlineKeyboardButton(
                text='В меню',
                callback_data='menu'
            )]])
    )
