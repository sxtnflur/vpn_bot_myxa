import asyncio
import os

from aiogram import Bot
from aiogram.types import BotCommandScopeDefault
from bootstrap import create_container
from logs import config_logger
from presentation.bot.commands import bot_commands
from presentation.bot import runner
from presentation.bot.shared.loader import create_bot, create_dp, register_dp


async def on_startup(bot: Bot):
    await bot.set_my_commands(
        commands=bot_commands,
        scope=BotCommandScopeDefault()
    )


async def start_polling():
    from config.settings import Settings

    settings = Settings(
        _env_file='.env',
        _env_file_encoding='utf-8'
    )
    config_logger(settings.log_level)
    bot = create_bot(settings.bot_token)
    container = create_container(bot, settings)
    container.wire(packages=['presentation.bot'])
    dp = create_dp('memory', settings)
    register_dp(dp, settings)
    dp.startup.register(on_startup)
    await runner.start_polling(dp, bot)


def start_webhook():
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web
    from config.settings import WebhookSettings

    WEBHOOK_PATH = '/webhook'

    settings = WebhookSettings(
        _env_file='.env',
        _env_file_encoding='utf-8'
    )
    config_logger(settings.log_level)
    bot = create_bot(settings.bot_token)
    container = create_container(bot, settings)
    container.wire(packages=['presentation.bot'])
    dp = create_dp('memory', settings)
    register_dp(dp, settings)
    dp.startup.register(on_startup)

    async def on_webhook_startup(bot: Bot):
        await bot.set_webhook(
            url=f'{settings.webhook_url.rstrip("/")}{WEBHOOK_PATH}',
            secret_token=settings.webhook_secret,
            drop_pending_updates=True
        )

    dp.startup.register(on_webhook_startup)

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret
    ).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host='0.0.0.0', port=int(os.getenv('PORT') or 8000))


if __name__ == '__main__':
    asyncio.run(start_polling())
