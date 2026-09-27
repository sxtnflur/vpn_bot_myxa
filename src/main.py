import asyncio
import os

from aiogram import Bot
from aiogram.types import BotCommandScopeDefault
from bootstrap import create_container
from logs import config_logger
from presentation.api.payment import create_router
from presentation.bot.commands import bot_commands
from presentation.bot import runner
from presentation.bot.shared.loader import create_bot, create_dp, register_dp


async def on_startup(bot: Bot):
    await bot.set_my_commands(
        commands=bot_commands,
        scope=BotCommandScopeDefault()
    )


def create_on_shutdown(container):
    async def on_shutdown():
        await container.cache().close()

    return on_shutdown


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
    dp = create_dp(settings)
    register_dp(dp, settings)
    dp.startup.register(on_startup)
    dp.shutdown.register(create_on_shutdown(container))
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
    APP_PREFIX = '/' + settings.app_prefix.strip('/')
    config_logger(settings.log_level)
    bot = create_bot(settings.bot_token)
    container = create_container(bot, settings)
    container.wire(packages=['presentation.bot'])
    dp = create_dp(settings)
    register_dp(dp, settings)
    dp.startup.register(on_startup)
    dp.shutdown.register(create_on_shutdown(container))

    async def on_webhook_startup(bot: Bot):
        await bot.set_webhook(
            url=f'{settings.webhook_url.rstrip("/")}{APP_PREFIX}{WEBHOOK_PATH}',
            secret_token=settings.webhook_secret,
            drop_pending_updates=True
        )

    dp.startup.register(on_webhook_startup)

    sub_app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret
    ).register(sub_app, path=WEBHOOK_PATH)

    sub_app.add_routes(create_router(payments_service=container.payments(),
                                     rolly_pay=container.rolly_pay()))

    app = web.Application()
    app.add_subapp(APP_PREFIX, sub_app)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host='0.0.0.0', port=settings.port)


if __name__ == '__main__':
    start_webhook()
