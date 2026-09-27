from aiogram.fsm.state import StatesGroup, State


class IncreaseSubStates(StatesGroup):
    email = State()


class AddSubStates(StatesGroup):
    # В data хранится rate_id выбранного тарифа
    email = State()
