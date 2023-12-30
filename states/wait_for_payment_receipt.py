from aiogram.dispatcher.filters.state import StatesGroup, State


class InputPhotoState(StatesGroup):
    wait_for_photo: State = State()
