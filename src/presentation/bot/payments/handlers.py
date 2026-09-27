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
from presentation.bot.payments.states import AddSubStates
from presentation.bot.shared.utils.email import normalize_email
from presentation.bot.statistic.callback_datas import ExtendSubCallback, ProfilePageCallback

router = Router()


# ---------- Добавить подписку: тариф -> email -> оплата ----------

@router.callback_query(F.data == 'rates')
@inject
async def rates_handler(
    event: CallbackQuery | Message,
    state: FSMContext,
    rates_service: RatesService = Provide[Container.rates]
):
    # Кнопка «Назад» из ввода email ведёт сюда — выходим из состояния ожидания email
    await state.clear()
    rates = rates_service.get_rates()
    await screens.rates(rates).answer(event, 'edit')


router.message(Command(commands.RATES))(rates_handler)
# Кнопка «Добавить / Продлить подписку» на старых сообщениях
router.callback_query(F.data == 'buy')(rates_handler)


@router.callback_query(SelectRateCallback.filter())
@inject
async def select_rate(
    call: CallbackQuery,
    callback_data: SelectRateCallback,
    state: FSMContext,
    rates_service: RatesService = Provide[Container.rates]
):
    rate = rates_service.get_rate(callback_data.rate_id)
    await state.set_state(AddSubStates.email)
    await state.update_data(rate_id=rate.id)
    await screens.ask_new_email(rate).answer(call, 'edit')


@router.message(AddSubStates.email)
@inject
async def add_sub_get_email(
    message: Message,
    state: FSMContext,
    rates_service: RatesService = Provide[Container.rates],
    subs_service: SubscriptionsTgBotService = Provide[Container.subs],
    payments_service: PaymentsService = Provide[Container.payments]
):
    email = normalize_email(message.text or '')
    if email is None:
        await screens.invalid_email().answer(message)
        return

    if await subs_service.is_email_taken(email):
        await screens.email_already_exists(email).answer(message)
        return

    data = await state.get_data()
    rate = rates_service.get_rate(data['rate_id'])
    await state.clear()

    payment_link = await payments_service.create_payment(
        amount=Decimal(rate.price),
        description=f'Новая подписка {email}: #{rate.id} ({rate.price} rub; protocol {rate.protocol})',
        rate_id=rate.id,
        email=email,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        telegram_id=message.from_user.id
    )
    await screens.pay_link(rate=rate, email=email, link=payment_link).answer(message)


# ---------- Продлить подписку из профиля (без ввода email) ----------

@router.callback_query(ExtendSubCallback.filter())
@inject
async def extend_sub_from_profile(
    call: CallbackQuery,
    callback_data: ExtendSubCallback,
    state: FSMContext,
    subs_service: SubscriptionsTgBotService = Provide[Container.subs],
    subs_by_email_service: SubscriptionByEmailService = Provide[Container.subs_by_email],
    payment_service: PaymentsService = Provide[Container.payments]
):
    await state.clear()

    sub = await subs_service.get_user_subscription_by_sub_id(call.from_user.id, callback_data.sub_id)
    if sub is None:
        # Подписку удалили или сообщение устарело
        await call.answer('Подписка не найдена. Обновите профиль', show_alert=True)
        return

    amount = await subs_by_email_service.get_subscription_amount_by_sub(sub)

    pay_link = await payment_service.create_payment(
        telegram_id=call.from_user.id,
        username=call.from_user.username,
        full_name=call.from_user.full_name,
        amount=amount,
        description=f'Оплата подписки по почте {sub.email}',
        email=sub.email
    )

    # Подписка выбрана в профиле — почту перепроверять не нужно, только сумма и ссылка
    await screens.extend_pay_link(
        amount=amount, pay_link=pay_link,
        back_callback=ProfilePageCallback(page=callback_data.page).pack()
    ).answer(call, 'edit')

