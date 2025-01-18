from datetime import datetime

from aiogram import BaseMiddleware, Bot

from config.config import MOSCOW_TIMEZONE, FORMAT_DATE_AND_TIME
from database.database import new_user, update_info


class UserSend(BaseMiddleware):
    async def __call__(self, handler, event, data: dict):
        user = None
        if event.callback_query:
            user = event.callback_query.from_user
        elif event.message:
            user = event.message.from_user
        if user:
            bot: Bot = data['bot']
            await new_user(user, bot)
            await update_info(
                table='users',
                where={'user_id': user.id},
                fields={'date_last': datetime.now(MOSCOW_TIMEZONE).strftime(FORMAT_DATE_AND_TIME)}
            )
        return await handler(event, data)