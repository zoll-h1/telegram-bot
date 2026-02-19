from aiogram.fsm.state import State, StatesGroup


class ReminderSetup(StatesGroup):
    timezone = State()
    time = State()
