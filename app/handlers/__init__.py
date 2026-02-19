from aiogram import Dispatcher

from app.handlers.common import router as common_router
from app.handlers.history import router as history_router
from app.handlers.reminders import router as reminders_router
from app.handlers.stats import router as stats_router
from app.handlers.workouts import router as workouts_router


def setup_routers(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(common_router)
    dispatcher.include_router(workouts_router)
    dispatcher.include_router(history_router)
    dispatcher.include_router(stats_router)
    dispatcher.include_router(reminders_router)
