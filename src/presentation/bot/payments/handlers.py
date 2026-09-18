from decimal import Decimal

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from application.payments import PaymentsService
from application.rates import RatesService
from bootstrap import Container
from dependency_injector.wiring import Provide, inject
from presentation.bot.payments import screens
from presentation.bot.payments.callback_datas import SelectRateCallback

router = Router()


@router.callback_query(F.data == 'rates')
@inject
async def rates_handler(
    call: CallbackQuery,
    rates_service: RatesService = Provide[Container.rates]
):
    rates = rates_service.get_rates()
    await screens.rates(rates).answer(call, 'edit')


@router.callback_query(SelectRateCallback.filter())
@inject
async def select_rate(
    event: CallbackQuery | Message,
    callback_data: SelectRateCallback,
    rates_service: RatesService = Provide[Container.rates],
    payments_service: PaymentsService = Provide[Container.payments]
):
    rate = rates_service.get_rate(callback_data.rate_id)
    payment_link = await payments_service.create_payment(
        amount=Decimal(rate.price),
        description=f'Оплата подписки #{rate.id} ({rate.price} rub; protocol {rate.protocol})',
        sub_td=rate.sub_td,
        full_name=event.from_user.full_name,
        username=event.from_user.username,
        telegram_id=event.from_user.id
    )
    await screens.pay_link(price=rate.price, link=payment_link).answer(event, 'edit')
