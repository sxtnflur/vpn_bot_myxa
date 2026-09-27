from html import escape

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from application.subscriptions.dto import Subscription
from domain.rates.sub_rate import SubRate
from presentation.bot.payments.callback_datas import SelectRateCallback
from presentation.bot.shared.screen import ScreenDef
from presentation.bot.shared.utils.date import sub_end_to_string

ADD_SUB_BTN = InlineKeyboardButton(text='➕ Купить подписку', callback_data='rates')
EXTEND_SUB_BTN = InlineKeyboardButton(text='🔄 Продлить подписку', callback_data='increase_sub_by_email')
MENU_BTN = InlineKeyboardButton(text='В меню', callback_data='menu')


def buy_menu():
    return ScreenDef(
        text='Выберите действие:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [ADD_SUB_BTN],
            [EXTEND_SUB_BTN],
            [MENU_BTN]
        ])
    )


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
             f'Укажите email для новой подписки.\n'
             f'<i>По нему подписку можно будет продлить.</i>',
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
             f'Отправьте другой email или продлите существующую подписку:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [EXTEND_SUB_BTN],
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


def ask_email(profile_command: str):
    return ScreenDef(
        text=f'<i>Свой email можно посмотреть здесь /{profile_command}</i>\n\n'
             f'Укажите ваш email для продления подписки:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Назад', callback_data='menu'
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


def pay_link_by_email(sub: Subscription, pay_link: str, back_callback: str | None = None):
    ikb = [[InlineKeyboardButton(text='Оплатить', url=pay_link)]]
    if back_callback:
        ikb.append([InlineKeyboardButton(text='Назад', callback_data=back_callback)])
    return ScreenDef(
        text=f'''
Убедитесь, что дата окончания подписки совпадает:

Текущая дата окончания подписки для почты <b>{escape(sub.email)}</b>: {sub_end_to_string(sub.expire_at)}
''',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=ikb)
    )


def email_not_found(email: str):
    return ScreenDef(
        text=f'Подписки с почтой <b>{escape(email)}</b> нет.\n\n'
             f'Проверьте email и отправьте его ещё раз:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [ADD_SUB_BTN],
            [InlineKeyboardButton(
                text='Назад', callback_data='menu'
            )]
        ])
    )
