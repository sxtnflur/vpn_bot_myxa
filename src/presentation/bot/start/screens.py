from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from presentation.bot.shared.screen import ScreenDef


def start(
        name: str,
        *,
        privacy_policy_link: str,
        user_agreement_link: str
):
    ikb = [
        [InlineKeyboardButton(
            text='👤 Мой профиль',
            callback_data='statistic'
        )],
        [InlineKeyboardButton(
            text='💵 Купить / Продлить',
            callback_data='rates'
        )],
        [
            InlineKeyboardButton(
                text='🆘 Помощь',
                callback_data='support'
            ),
            InlineKeyboardButton(
                text='ℹ О сервисе',
                callback_data='about'
            )]
    ]

    return ScreenDef(
        text=f'''
👋 Привет, {name}.

Задать вопрос — /support

👇 Пожалуйста, выберите:
''',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=ikb)
    )


def support(link: str):
    return ScreenDef(
        text=f'Поддержка: {link}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='В меню', callback_data='menu'
            )]
        ])
    )


def about_us(
        *,
        privacy_policy_link: str,
        user_agreement_link: str
):
    return ScreenDef(
        text='''
ℹ О сервисе

<b>Myxa VPN</b>

🔒 <b>Премиальный VPN-сервис</b> для безопасного и быстрого интернета

<b>🚀 Наши преимущества:</b>
• Высокая скорость соединения
• Современный протокол Vless
• Серверы в разных странах
• Простое подключение на всех устройствах
• Открываем все зарубежные сайты
• Доступ к российским сайтам из других стран
• Российские сайты без необходимости выключения VPN
• Удаляем рекламу и трекеры
• Российский YouTube без рекламы
• 1 подписка на все Ваши личные устройства

<b>🛡️ Безопасность:</b>
• Шифрование трафика
• Скрытие реального IP-адреса
• Защита от блокировок
• Анонимность в сети

<b>💎 Качество сервиса:</b>
• Стабильное соединение
• Минимальные задержки
• Регулярные обновления
• Крутая и мотивированная команда

Используя Myxa VPN, вы получаете надёжный доступ к интернету без ограничений 💯
''',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text='Политика конфиденциальности',
                url=privacy_policy_link
            )],
            [InlineKeyboardButton(
                text='Пользовательское соглашение',
                url=user_agreement_link
            )],
            [InlineKeyboardButton(
                text='В меню', callback_data='menu'
            )]
        ])
    )
