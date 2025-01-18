import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis

from aio_dialogs.dialogs import admin_dialog, new_action_dialog, settings_dialog
from config.config import BOT_TOKEN
from config.main_menu import set_main_menu
from database.database import create_database
from handlers import default_handler, other_handler

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.middlewars import UserSend
from services.scheduler import delete_24_hour

# Инициализируем логгер
logger = logging.getLogger(__name__)
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Инициализируем Redis
    redis = Redis(host='localhost', db=2)
    # Инициализируем Scheduler
    scheduler = AsyncIOScheduler()

    await create_database()

    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)


    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # Подключаем middleware
    dp.update.middleware(UserSend())

    # Регистрируем роутеры в диспетчере
    dp.include_router(default_handler.router)
    dp.include_routers(admin_dialog)
    dp.include_routers(new_action_dialog)
    dp.include_routers(settings_dialog)
    dp.include_router(other_handler.router)

    setup_dialogs(dp)
    scheduler.start()
    await delete_24_hour(bot)
    scheduler.add_job(delete_24_hour, "interval", hours=1, args=(bot,), timezone='Europe/Moscow')





    await bot.delete_webhook(drop_pending_updates=False)
    logger.debug('Запуск polling')
    await dp.start_polling(bot, )




if __name__ == '__main__':
    asyncio.run(main())