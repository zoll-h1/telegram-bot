import asyncio
from sqlalchemy import desc
from database import Session, Workout
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from states import AddWorkout
from aiogram import F
from keyboard import main_kb, history_inline_kb
from aiogram.types import CallbackQuery # Нам понадобится для обработки нажатия


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN) # IT'S TALKING 
dp = Dispatcher()    # IT'S THINKING

@dp.message(Command("start"))
async def cmd_start(message: Message):
    # reply_markup=main_kb отправляет кнопки вместе с сообщением    
    await message.answer(
        "Welcome to Zoll_H1_Bot! 🦍\nChoose an action:",
         reply_markup=main_kb
    )
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("""
    /start - Start working with bot
    /help - Show list of commands
    /add - Add training
    /history - History of trainings(soon) 
    """)

@dp.message(Command("add"))
@dp.message(F.text == "💪 Add Workout")
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
    await message.answer(f"Got it! {data_from_user}. How many sets you do?")
    # 4. Doing Transition
    # Swith the tumbler to the next step : Wait the quantity of sets
    await state.set_state(AddWorkout.sets)

# Handler for sets
@dp.message(AddWorkout.sets)
async def process_sets(message: Message, state:FSMContext):
    data_from_user = message.text #get text from user
    # Update memory
    await state.update_data(gym_sets=data_from_user)
    # Ask next question
    await message.answer(f"Got it! {data_from_user}. How many reps?")
    # Switch state to the final step
    await state.set_state(AddWorkout.reps)


#  Hanldler for reps
@dp.message(AddWorkout.reps)
async def process_reps(message: Message, state: FSMContext):
    reps_count = message.text
    # 1. Get all data from memory
    data = await state.get_data()
    ex = data.get('gym_exercise')   # Key from previous step
    sets = data.get('gym_sets')     # Key from step above
        
    # 2. SAve to DATABASE ( THe magic moment)
    #Открываем сессию 
    session = Session()
  
    # Создаем обьект тренировки( строчку для таблицы)
    new_workout = Workout(
        user_id=message.from_user.id, #ID юзера в телеграм
        exercise=ex,
        sets=sets,
        reps=reps_count
    )
   
    try:
        # Добавляем в лист ожидания
        session.add(new_workout)
        # Физически записываем в файл (Commit)
        session.commit()
        await message.answer("<b>Saved to Database!</b>", parse_mode="HTML")

    except Exception as e:
        await message.answer(f"Error saving: {e}")
        session.rollback # Откат изменений если ошибка

    finally:
        session.close() # Закрываем сессию !
    # 3. Answer with summary
    response_text = (
        f"<b>Workout save!</b>\n"
        f"Exercise: {ex}\n"
        f"Sets: {sets}\n"
        f"Reps: {reps_count}"
    )
    # Parse_mode = "HTML" allows bold text
    await message.answer(response_text, parse_mode="HTML")
  
    # 4. CRITICAL: Clear state 
    # if we don't dp this , bot will think next message is also reps
    await state.clear()

@dp.message(Command("history"))
@dp.message(F.text == "📜 History")
async def cmd_history(message:Message):
    session = Session()
    
    try:
        # 1. SELECT * FROM workouts
        # filter(...) -> only show MY workouts (not other users)
        # order_by(desc(...)) -> newest first ( сортировка от новых к старым)
        #limit(5) -> Show only last 5 records
        user_workouts = session.query(Workout)\
            .filter(Workout.user_id == message.from_user.id)\
            .order_by(desc(Workout.id))\
            .limit(5)\
            .all()

            # 2. Check if list is empty
        if not user_workouts:
            await message.answer("📭 History is empty. Go train!")
            return
        # 3. Format the output 
        history_text = "<b>🏋️ Last 5 Workouts: </b>\n\n"

        for w in user_workouts:
            history_text += f"📅 <b>{w.date}</b>: {w.exercise} | {w.sets} x {w.reps}\n" 

        await message.answer(
             history_text,
             parse_mode="HTML",
             reply_markup=history_inline_kb  #<-- кнопка сюда цепляем
        ) 

    except Exception as e:
        await message.answer(f"Error reading DB: {e}")

    finally:
        session.close()
@dp.message(Command('stats'))
@dp.message(F.text == "📊 Stats")
async def cmd_stats(message: Message):
    await message.answer("Feature under construction 🏗")

@dp.callback_query(F.data == "delete_last")
async def delete_last(callback: CallbackQuery):
    session = Session()

    try:
        # find the last workour ot THIS user
        last_workout = session.query(Workout)\
            .filter(Workout.user_id == callback.from_user.id)\
            .order_by(desc(Workout.id))\
            .first()

        if last_workout:
            # Delete it
            session.delete(last_workout)
            session.commit()

            # Notify user
            await callback.answer("✅ Deleted successfully!")

            # Optional : update the message text so the user sees it's gone
            await callback.message.edit_text("🗑 <b>Last workout was deleted.</b> check /history", parse_mode="HTML")

        else:
            await callback.answer("❌ Nothing to delete!", show_alert=True)
    except Exception as e:
            await callback.answer(f"Error bruuh : {e}", show_alert=True)

    finally:
        session.close()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())