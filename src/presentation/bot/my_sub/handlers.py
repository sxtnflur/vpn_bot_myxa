# from aiogram import Router, F
# from aiogram.filters import Command
# from aiogram.types import Message, CallbackQuery
#
# from application.subscriptions.service import SubscriptionsTgBotService
# from bootstrap import Container
# from dependency_injector.wiring import Provide, inject
# from presentation.bot import commands
# from presentation.bot.my_sub import screens
#
# router = Router()
#
#
# @inject
# async def my_sub_handler(
#         event: Message | CallbackQuery,
#         subs: SubscriptionsTgBotService = Provide[Container.subs]
# ):
#     sub_links = await subs.get_subscription_link(event.from_user.id)
#     await screens.my_sub_links(sub_links).answer(event, 'edit')
#
#
# router.callback_query(F.data == 'my_sub_links')(my_sub_handler)
# router.message(Command(commands.SUBSCRIPTION))(my_sub_handler)
