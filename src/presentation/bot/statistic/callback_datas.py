from aiogram.filters.callback_data import CallbackData


class ProfilePageCallback(CallbackData, prefix='profile'):
    page: int  # с 0


class UpdateProfileCallback(CallbackData, prefix='profile-upd'):
    page: int


class ExtendSubCallback(CallbackData, prefix='ext'):
    """Продление подписки из профиля. По sub_id, т.к. email может не влезть в 64 байта callback_data"""
    sub_id: str
    page: int  # страница профиля, на которую вернуться по «Назад»
