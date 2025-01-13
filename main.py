import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs

from aio_dialogs.dialogs import admin_dialog, new_action_dialog
from config.config import BOT_TOKEN
from config.main_menu import set_main_menu
from database.database import create_database
from handlers import default_handler, other_handler
from services.middlewars import User_send

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

    await create_database()

    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)


    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # Подключаем middleware
    dp.message.middleware(User_send())

    # Регистрируем роутеры в диспетчере
    dp.include_router(default_handler.router)
    dp.include_routers(admin_dialog)
    dp.include_routers(new_action_dialog)
    dp.include_router(other_handler.router)

    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=False)
    logger.debug('Запуск polling')
    await dp.start_polling(bot, )




if __name__ == '__main__':
    asyncio.run(main())