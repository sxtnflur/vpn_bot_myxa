from decimal import Decimal

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from application.payments import PaymentsService
from application.rates import RatesService
from application.subscriptions.service import SubscriptionsTgBotService
from application.subscriptions.subscription_by_email_service import SubscriptionByEmailService
from bootstrap import Container
from dependency_injector.wiring import Provide, inject
from presentation.bot import commands
from presentation.bot.payments import screens
from presentation.bot.payments.callback_datas import SelectRateCallback
from presentation.bot.payments.states import IncreaseSubStates

router = Router()


@router.callback_query(F.data == 'rates')
@inject
async def rates_handler(
    call: CallbackQuery,
    rates_service: RatesService = Provide[Container.rates]
):
    rates = rates_service.get_rates()
    await screens.rates(rates).answer(call, 'edit')


router.message(Command(commands.RATES))(rates_handler)


@router.callback_query(F.data == 'increase_sub_by_email')
async def increase_sub_by_email(
    call: CallbackQuery,
    state: FSMContext
):
    await state.set_state(IncreaseSubStates.email)
    await screens.ask_email(commands.PROFILE).answer(call, 'edit')


@router.message(IncreaseSubStates.email)
@inject
async def increase_sub_by_email_get_email(
    message: Message, state: FSMContext,
    subs_service: SubscriptionByEmailService = Provide[Container.subs_by_email],
    payment_service: PaymentsService = Provide[Container.payments]
):
    if not message.text:
        await message.answer('Ожидаю почту')
        return

    email = message.text

    sub = await subs_service.get_subscription_by_email(email)
    if sub is None:
        await message.answer('Подписки с такой почтой нет')
        return

    await state.clear()

    amount = await subs_service.get_subscription_amount_by_sub(sub)

    pay_link = await payment_service.create_payment(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        amount=amount,
        description=f'Оплата подписки по почту {email}',
        email=email
    )

    await screens.pay_link_by_email(sub=sub, pay_link=pay_link).answer(message)


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
        rate_id=rate.id,
        full_name=event.from_user.full_name,
        username=event.from_user.username,
        telegram_id=event.from_user.id
    )
    await screens.pay_link(price=rate.price, link=payment_link).answer(event, 'edit')
