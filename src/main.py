import asyncio

from aiogram import Bot
from aiogram.types import BotCommandScopeDefault
from bootstrap import create_container
from config.settings import Settings
from presentation.bot.commands import bot_commands
from presentation.bot.runner import start_polling
from presentation.bot.shared.loader import create_bot, create_dp, register_dp


async def on_startup(bot: Bot):
    await bot.set_my_commands(
        commands=bot_commands,
        scope=BotCommandScopeDefault()
    )


async def main():
    settings = Settings(
        _env_file='.env',
        _env_file_encoding='utf-8'
    )
    bot = create_bot(settings.bot_token)
    container = create_container(bot, settings)
    container.wire(packages=['presentation.bot'])
    dp = create_dp('memory', settings)
    register_dp(dp, settings)
    dp.startup.register(on_startup)
    await start_polling(dp, bot)


if __name__ == '__main__':
    asyncio.run(main())
