import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from states import AddWorkout

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN) # IT'S TALKING 
dp = Dispatcher()    # IT'S THINKING

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("The virtual environment is working! I'm ready to write your trainings!")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("""
    /start - Start working with bot
    /help - Show list of commands
    /add - Add training(soon)
    /history - History of trainings(soon) 
    """)

@dp.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    await message.answer("""
    Which exercise ? :
    """)
    await state.set_state(AddWorkout.exercise)
# It's an decorator - GUARDIAN (Filter)
# It's says: "Start this function ONLY if user is in "exercise" condition.
@dp.message(AddWorkout.exercise)
async def proccess_exercise_name(message: Message, state: FSMContext):
    # 1. Catch Event : text , which wrote user
    data_from_user = message.text
    # 2. Update the memory (save the data in temporary dict.)
    # We took "Push-Ups" in cell with named "gym_exercise"
    await state.update_data(gym_exercise=data_from_user)
    # 3.React
    await message.answer(f"Get it! {data_from_user}. How many sets you do?")
    # 4. Doing Transition
    # Swith the tumbler to the next step : Wait the quantity of sets
    await state.set_state(AddWorkout.sets)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())