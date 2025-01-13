from aiogram import BaseMiddleware
from aiogram.types import Message

from database.database import update_last_send, new_user


class User_send(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        user_id = event.from_user.id
        await new_user(user_id)
        await update_last_send(user_id)
        return await handler(event, data)