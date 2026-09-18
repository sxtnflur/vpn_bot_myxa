from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from config.settings import Settings
from presentation.bot import commands
from presentation.bot.start import screens

router = Router()


@router.message(CommandStart())
async def start_handler(
    event: CallbackQuery | Message,
    settings: Settings
):
    await screens.start(
        event.from_user.first_name,
        privacy_policy_link=settings.privacy_policy_url,
        user_agreement_link=settings.user_agreement_url
    ).answer(event, 'edit')


router.callback_query(F.data == 'menu')(start_handler)


@router.message(Command(commands.SUPPORT))
async def support_handler(
    event: CallbackQuery | Message,
    settings: Settings
):
    await screens.support(settings.support_url).answer(event, 'edit')


router.callback_query(F.data == 'support')(support_handler)


async def about_us(
    event: CallbackQuery | Message,
    settings: Settings
):
    await screens.about_us(
        privacy_policy_link=settings.privacy_policy_url,
        user_agreement_link=settings.user_agreement_url
    ).answer(event, 'edit')


router.callback_query(F.data == 'about')(about_us)
