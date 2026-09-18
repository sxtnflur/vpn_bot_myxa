from aiogram.filters.callback_data import CallbackData


class SelectRateCallback(CallbackData, prefix='select-rate'):
    rate_id: int
