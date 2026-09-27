from enum import StrEnum

from config.settings import Settings
from domain.payments.registry import PaymentsRegistry
from infra.payments.rollypay import RollyPayStrategy
from infra.payments.yookassa import YookassaService
from infra.rollypay.client import RollyPay


class PaymentKey(StrEnum):
    rollypay = 'rollypay'
    yookassa = 'yookassa'


def create_payments(
        settings: Settings,
        rolly_pay: RollyPay
):
    registry = PaymentsRegistry()
    registry.add(
        PaymentKey.rollypay,
        RollyPayStrategy(
            rollypay=rolly_pay,
            test=settings.test_payment
        )
    )
    # registry.add(
    #     PaymentKey.yookassa,
    #     YookassaService(
    #         shop_id=settings.yookassa_shop_id,
    #         secret_key=settings.yookassa_secret_key,
    #         return_url=settings.bot_url
    #     ))
    return registry
