from aiogram import Dispatcher, Bot


async def start_polling(dp: Dispatcher, bot: Bot):
    await dp.start_polling(bot)
