from aiogram.fsm.state import State, StatesGroup
  
class AddWorkout(StatesGroup):
    exercise = State()
    sets = State()
    reps = State()