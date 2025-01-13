import asyncio
from datetime import datetime

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Select

from aio_dialogs.states import new_action
from database.database import add_action_db


async def action_select(callback: CallbackQuery, widget: Select,
                             dialog_manager: DialogManager, action_name: str):
    await add_action_db(callback.from_user.id, action_name)
    await dialog_manager.next()

async def correct_action_input(message: Message,
                              widget: ManagedTextInput,
                              dialog_manager: DialogManager,
                              text: str) -> None:
    await add_action_db(message.from_user.id, text)
    await dialog_manager.next()

async def uncorrect_action_input(message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer('Ожидаю название до 15 символов')


