from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from application.subscriptions.service import SubscriptionsTgBotService
from bootstrap import Container
from config.settings import Settings
from dependency_injector.wiring import inject, Provide
from presentation.bot import commands
from presentation.bot.statistic import screens
from presentation.bot.statistic.callback_datas import ProfilePageCallback, UpdateProfileCallback

router = Router()


@inject
async def show_profile(
    event: Message | CallbackQuery,
    settings: Settings,
    page: int = 0,
    subs_service: SubscriptionsTgBotService = Provide[Container.subs]
):
    subs_page = await subs_service.get_user_subscriptions_page(
        telegram_id=event.from_user.id,
        page=page,
        page_size=settings.profile_page_size
    )
    await screens.client_statistic(subs_page, tz=settings.tz).answer(event, 'edit')


async def profile_handler(event: Message | CallbackQuery, settings: Settings):
    await show_profile(event, settings)


router.callback_query(F.data == 'statistic')(profile_handler)
# «Обновить» на сообщениях, отправленных до пагинации
router.callback_query(F.data == 'update_statistic')(profile_handler)
# «Продлить подписку» (ввод email) на старых сообщениях — продление теперь только из профиля
router.callback_query(F.data == 'increase_sub_by_email')(profile_handler)
router.message(Command(commands.STATISTIC))(profile_handler)


@router.callback_query(ProfilePageCallback.filter())
async def profile_page_handler(
    call: CallbackQuery, callback_data: ProfilePageCallback, settings: Settings
):
    await show_profile(call, settings, page=callback_data.page)


@router.callback_query(F.data == screens.NOOP)
async def noop_handler(call: CallbackQuery):
    # Номер страницы и неактивные стрелки — просто убираем «часики» у кнопки
    await call.answer()


@router.callback_query(UpdateProfileCallback.filter())
async def update_profile_handler(
        call: CallbackQuery, callback_data: UpdateProfileCallback, settings: Settings
):
    # Пока грузятся данные, показываем анимированный эмодзи на кнопке «Обновить»
    reply_markup = call.message.reply_markup
    update_data = callback_data.pack()
    for row in reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == update_data:
                button.text = 'Обновить'
                button.icon_custom_emoji_id = '5264727218734524899'
    await call.message.edit_reply_markup(
        reply_markup=reply_markup
    )
    await show_profile(call, settings, page=callback_data.page)
