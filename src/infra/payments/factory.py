from enum import StrEnum

from config.settings import Settings
from domain.payments.registry import PaymentsRegistry
from infra.payments.yookassa import YookassaService


class PaymentKey(StrEnum):
    yookassa = 'yookassa'


def create_payments(settings: Settings):
    registry = PaymentsRegistry()
    registry.add(
        PaymentKey.yookassa,
        YookassaService(
            shop_id=settings.yookassa_shop_id,
            secret_key=settings.yookassa_secret_key,
            return_url=settings.bot_url
        ))
    return registry
