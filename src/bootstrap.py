from aiogram import Bot
from application.payments import PaymentsService
from application.rates import RatesService
from application.subscriptions.inbounds_service import InboundsService
from application.subscriptions.subscription_by_email_service import SubscriptionByEmailService
from config.settings import Settings
from dependency_injector import providers, containers
from application.subscriptions.service import SubscriptionsTgBotService
from infra.cache.factory import create_cache_service
from infra.client.session.aiohttp import AiohttpSession
from infra.payments.factory import create_payments, PaymentKey
from infra.rollypay.client import RollyPay
from infra.xui_vpn import XUIVPN
from presentation.bot.message_senders.payment import AiogramPaymentMessageSender


class Container(containers.DeclarativeContainer):
    settings = providers.Dependency(instance_of=Settings)
    bot = providers.Dependency(instance_of=Bot)

    session = providers.Factory(
        AiohttpSession
    )

    xui_vpn = providers.Singleton(
        XUIVPN,
        base_url=settings.provided.xui_api_url,
        api_key=settings.provided.xui_api_key,
        sub_base_url=settings.provided.xui_sub_base_url,
        session=session
    )

    rates = providers.Singleton(
        RatesService
    )

    inbounds = providers.Singleton(
        InboundsService,
        vpn_client=xui_vpn
    )

    subs = providers.Singleton(
        SubscriptionsTgBotService,
        vpn_client=xui_vpn,
        rates=rates,
        inbounds_service=inbounds
    )

    rolly_pay = providers.Factory(
        RollyPay,
        api_key=settings.provided.rollypay_api_key,
        base_url=settings.provided.rollypay_base_url,
        secret_webhook=settings.provided.rollypay_secret_webhook,
        session=session,
        redirect_url=settings.provided.bot_url
    )

    payments_registry = providers.Callable(
        create_payments,
        settings=settings,
        rolly_pay=rolly_pay
    )

    payments_sender = providers.Singleton(
        AiogramPaymentMessageSender,
        bot=bot,
        tz=settings.provided.tz,
        subs_service=subs,
        profile_page_size=settings.provided.profile_page_size
    )

    cache = providers.Singleton(
        create_cache_service,
        settings=settings.provided
    )

    payments = providers.Singleton(
        PaymentsService,
        registry=payments_registry,
        subscriptions_service=subs,
        sender=payments_sender,
        rates=rates,
        payment_key=PaymentKey.rollypay,
        cache=cache,
        fake=settings.provided.fake_payment
    )

    subs_by_email = providers.Singleton(
        SubscriptionByEmailService,
        vpn_client=xui_vpn,
        inbounds_service=inbounds
    )


def create_container(bot: Bot, settings: Settings):
    container = Container()
    container.bot.override(bot)
    container.settings.override(settings)
    return container
