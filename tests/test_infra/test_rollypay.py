import pytest

from config.settings import Settings
from infra.client.session.aiohttp import AiohttpSession
from infra.payments.rollypay import RollyPayStrategy
from infra.rollypay.client import RollyPay


@pytest.fixture
def rollypay(settings: Settings):
    return RollyPay(
        api_key=settings.rollypay_api_key,
        base_url=settings.rollypay_base_url,
        secret_webhook=settings.rollypay_secret_webhook,
        session=AiohttpSession()
    )


async def test_rolly_pay_create_payment(rollypay):
    result = await rollypay.create_payment(
        amount=1000,
        description='test',
        payment_method='sbp',
        test=True
    )
    print(f'{result=}')


async def test_rolly_pay_strategy_create_payment(rollypay):
    strategy = RollyPayStrategy(
        rollypay, test=True
    )
    result = await strategy.create_payment(
        amount=1000,
        description='test',
        metadata=None,
        expired_date=None
    )
    print(f'{result=}')