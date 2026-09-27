from aiogram.fsm.state import StatesGroup, State


class AddSubStates(StatesGroup):
    # В data хранится rate_id выбранного тарифа
    email = State()
