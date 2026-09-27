from aiogram.types import BotCommand

START = 'start'
STATISTIC = 'profile'
PROFILE = STATISTIC
RATES = 'buy'
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
        description='💵 Купить подписку'
    ),
    BotCommand(
        command=STATISTIC,
        description='👤 Мой профиль'
    )
]