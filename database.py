from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date

# 1. Create Engine (Connection to file)
# Этим мы говорим: "Создай файл gym_bit.db"
engine = create_engine('sqlite:///gym_bot.db')

# Base Class for our tables
Base = declarative_base()

# Define the Table 
class Workout(Base):
    __tablename__ = 'workout'

    # Column
    id = Column(Integer, primary_key=True) #Unique ID (1,2,3...)
    user_id = Column(Integer)  # Telegram User_id
    exercise = Column(String)  # Exercise name
    sets = Column(String)    # Количество похдодов 
    reps = Column(String)    # Количество повторений
    date = Column(Date, default=date.today)   # Дата (автоматически)

# Create the database content
# Эта команда создаст файл , если его нет
Base.metadata.create_all(engine)

# Helper to save data later
Session = sessionmaker(bind=engine)