from aiogram.dispatcher.filters.state import StatesGroup, State


class InputCustomName(StatesGroup):
    wait_for_name: State = State()
