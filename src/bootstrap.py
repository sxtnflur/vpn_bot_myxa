from aiogram import Bot
from application.payments import PaymentsService
from application.rates import RatesService
from config.settings import Settings
from dependency_injector import providers, containers
from application.subscriptions.service import SubscriptionsTgBotService
from infra.client.session.aiohttp import AiohttpSession
from infra.payments.factory import create_payments
from infra.xui_vpn import XUIVPN
from presentation.bot.message_senders.payment import AiogramPaymentMessageSender


class Container(containers.DeclarativeContainer):
    settings = providers.Dependency(instance_of=Settings)
    bot = providers.Dependency(instance_of=Bot)

    auth_headers = providers.Callable(
        lambda api_key: {'Authorization': f'Bearer {api_key}'},
        settings.provided.xui_api_key
    )

    session = providers.Factory(
        AiohttpSession,
        headers=auth_headers
    )

    xui_vpn = providers.Singleton(
        XUIVPN,
        base_url=settings.provided.xui_api_url,
        api_key=settings.provided.xui_api_key,
        sub_base_url=settings.provided.xui_sub_base_url,
        session=session
    )

    subs = providers.Singleton(
        SubscriptionsTgBotService,
        vpn_client=xui_vpn
    )

    payments_registry = providers.Callable(
        create_payments,
        settings=settings
    )

    payments_sender = providers.Singleton(
        AiogramPaymentMessageSender,
        bot=bot,
        tz=settings.provided.tz
    )

    rates = providers.Singleton(
        RatesService
    )

    payments = providers.Singleton(
        PaymentsService,
        registry=payments_registry,
        subscriptions_service=subs,
        sender=payments_sender,
        rates=rates,
        fake=True
    )


def create_container(bot: Bot, settings: Settings):
    container = Container()
    container.bot.override(bot)
    container.settings.override(settings)
    return container
