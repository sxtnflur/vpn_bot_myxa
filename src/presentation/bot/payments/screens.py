from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from domain.rates.sub_rate import SubRate
from presentation.bot.payments.callback_datas import SelectRateCallback
from presentation.bot.shared.screen import ScreenDef


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
        reply_markup=InlineKeyboardMarkup(inline_keyboard=ikb + [[InlineKeyboardButton(
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
