from aiogram.fsm.state import State, StatesGroup


class AddWorkout(StatesGroup):
    template = State()
    exercise = State()
    sets = State()
    reps = State()
    weight = State()
    notes = State()
