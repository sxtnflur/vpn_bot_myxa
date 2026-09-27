from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from application.subscriptions.dto import Subscription
from domain.rates.sub_rate import SubRate
from presentation.bot.payments.callback_datas import SelectRateCallback
from presentation.bot.shared.screen import ScreenDef
from presentation.bot.shared.utils.date import sub_end_to_string


def rates(_rates: list[SubRate]):
    text = ''
    ikb = []
    for rate in _rates:
        text += rate.name + '\n'
        ikb.append([InlineKeyboardButton(
            text=rate.name,
            callback_data=SelectRateCallback(rate_id=rate.id).pack()
        )])

    return ScreenDef(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=ikb + [
            [InlineKeyboardButton(
                text='Продлить по EMAIL',
                callback_data='increase_sub_by_email'
            )],
            [InlineKeyboardButton(
                text='В меню', callback_data='menu'
            )]])
    )


def pay_link(price: int, link: str):
    return ScreenDef(
        text=f'Оплата подписки за {price} руб',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Оплатить', url=link
            )],
            [InlineKeyboardButton(
                text='Назад', callback_data='rates'
            )]
        ])
    )


def ask_email(profile_command: str):
    return ScreenDef(
        text=f'<i>Свой email можно посмотреть здесь /{profile_command}</i>\n\n'
             f'Укажите ваш email для продления подписки:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Назад', callback_data='rates'
            )]
        ])
    )


def pay_link_by_email(sub: Subscription, pay_link: str):
    return ScreenDef(
        text=f'''
Убедитесь, что дата окончания подписки совпадает:

Текущая дата окончания подписки для почты <b>{sub.email}</b>: {sub_end_to_string(sub.expire_at)}
''',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Оплатить', url=pay_link
            )]
        ])
    )
