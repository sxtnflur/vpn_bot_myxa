import datetime


async def test_create_payment(payment_service):
    await payment_service.create_payment(
        rate_id=1,
        amount=1000,
        description='test',
        full_name='test user',
        telegram_id=1304563494,
        username='sheggy_love'
    )
