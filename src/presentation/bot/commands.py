from aiogram.types import BotCommand

START = 'start'
STATISTIC = 'profile'
RATES = 'rates'
SUPPORT = 'support'


bot_commands = [
    BotCommand(
        command=START,
        description='Главное меню'
    ),
    BotCommand(
        command=SUPPORT,
        description='🆘 Задать вопрос / Помощь'
    ),
    BotCommand(
        command=RATES,
        description='💵 Тарифы'
    ),
    BotCommand(
        command=STATISTIC,
        description='👤 Мой профиль'
    )
]