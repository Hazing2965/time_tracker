from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def send_echo(message: Message):
    await message.answer('Для начала записей используйте: <b>/new_action</b>', parse_mode='HTML')
