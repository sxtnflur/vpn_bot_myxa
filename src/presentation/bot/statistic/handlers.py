from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from application.subscriptions.service import SubscriptionsTgBotService
from bootstrap import Container
from config.settings import Settings
from dependency_injector.wiring import inject, Provide
from presentation.bot import commands
from presentation.bot.statistic import screens

router = Router()


@inject
async def profile_handler(
    event: Message | CallbackQuery,
    settings: Settings,
    subs_service: SubscriptionsTgBotService = Provide[Container.subs]
):
    subs = await subs_service.get_user_subscriptions(
        telegram_id=event.from_user.id
    )
    await screens.client_statistic(subs, tz=settings.tz).answer(event, 'edit')


router.callback_query(F.data == 'statistic')(profile_handler)
router.message(Command(commands.STATISTIC))(profile_handler)


@router.callback_query(F.data == 'update_statistic')
async def update_profile_handler(
        call: CallbackQuery, settings: Settings
):
    reply_markup = call.message.reply_markup
    reply_markup.inline_keyboard[0][0].text = 'Обновить'
    reply_markup.inline_keyboard[0][0].icon_custom_emoji_id = '5264727218734524899'
    await call.message.edit_reply_markup(
        reply_markup=reply_markup
    )
    # await call.message.edit_text('<tg-emoji emoji-id="5996553250420037768">⚪️</tg-emoji>')
    await profile_handler(call, settings)
