import logging

from aiogram import Router, Bot, F
from aiogram.types import ErrorEvent

from config.config import ADMIN_ID
from lexicon.LEXICON import TEXT

router = Router()

# Инициализируем логгер
logger = logging.getLogger(__name__)


@router.error()
async def error_handler(event: ErrorEvent, bot: Bot):
    logger.critical("Critical error caused by %s", event.exception, exc_info=False)
    if event.update.event_type == 'message':
        message = event.update.message
        user_id = message.from_user.id
        await message.answer(TEXT['error_message'], parse_mode='HTML')
        await bot.send_message(ADMIN_ID, f'Message ошибка у пользователя {user_id}:\n\n{event.exception}')
    elif event.update.event_type == 'callback_query':
        callback = event.update.callback_query
        user_id = callback.from_user.id
        message_id = callback.message.message_id
        await bot.delete_message(chat_id=user_id, message_id=message_id)
        await bot.send_message(user_id, TEXT['error_message'], parse_mode='HTML')
        await bot.send_message(ADMIN_ID, f'Callback ошибка у пользователя {user_id}:\n\n{event.exception}')
    else:
        await bot.send_message(ADMIN_ID, f'Ошибка: "<b>{event.exception}</b>"\n\n'
                                         f'event_type = "<b>{event.update.event_type}</b>"',
                               parse_mode='HTML')

