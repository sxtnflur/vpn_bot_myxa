from aiogram import Router
from config.settings import Settings
from .simple import SimpleMiddleware


def register_middlewares(router: Router, settings: Settings):
    simple_mdlwr = SimpleMiddleware(
        settings=settings
    )
    router.message.middleware(simple_mdlwr)
    router.callback_query.middleware(simple_mdlwr)
