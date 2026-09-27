from html import escape

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from domain.rates.sub_rate import SubRate
from presentation.bot.payments.callback_datas import SelectRateCallback
from presentation.bot.shared.screen import ScreenDef


def rates(_rates: list[SubRate]):
    text = '<b>Новая подписка</b>\n\nВыберите тариф:\n'
    ikb = []
    for rate in _rates:
        text += escape(rate.name) + '\n'
        ikb.append([InlineKeyboardButton(
            text=rate.name,
            callback_data=SelectRateCallback(rate_id=rate.id).pack()
        )])

    return ScreenDef(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=ikb + [
            [InlineKeyboardButton(text='Назад', callback_data='menu')]
        ])
    )


def ask_new_email(rate: SubRate):
    return ScreenDef(
        text=f'Тариф: <b>{escape(rate.name)}</b>\n\n'
             f'Укажите email для новой подписки:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Назад', callback_data='rates'
            )]
        ])
    )


def invalid_email():
    return ScreenDef(
        text='Это не похоже на email. Отправьте почту в формате <code>name@example.com</code>:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Назад', callback_data='rates'
            )]
        ])
    )


def email_already_exists(email: str):
    return ScreenDef(
        text=f'Подписка с почтой <b>{escape(email)}</b> уже существует.\n\n'
             f'Отправьте другой email. Продлить свою подписку можно в профиле.',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='👤 Мой профиль', callback_data='statistic'
            )],
            [InlineKeyboardButton(
                text='Назад', callback_data='rates'
            )]
        ])
    )


def pay_link(rate: SubRate, email: str, link: str):
    return ScreenDef(
        text=f'Новая подписка <b>{escape(email)}</b>\n'
             f'Тариф: {escape(rate.name)}\n\n'
             f'Оплата подписки за {rate.price} руб',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Оплатить', url=link
            )],
            [InlineKeyboardButton(
                text='Назад', callback_data='rates'
            )]
        ])
    )


def extend_pay_link(amount: int, pay_link: str, back_callback: str):
    return ScreenDef(
        text=f'Продление подписки за {amount} руб',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Оплатить', url=pay_link)],
            [InlineKeyboardButton(text='Назад', callback_data=back_callback)]
        ])
    )
