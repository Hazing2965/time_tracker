from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Select, Button

from aio_dialogs.states import new_action
from database.database import add_action_db, update_info


async def action_select(callback: CallbackQuery, widget: Select,
                        dialog_manager: DialogManager, action_name: str):
    await add_action_db(callback.from_user.id, action_name)
    bot = callback.bot
    await bot.send_message(callback.from_user.id, f'Действие "<b>{action_name}</b>" сохранено', parse_mode='HTML')
    await dialog_manager.switch_to(state=new_action.start, show_mode=ShowMode.DELETE_AND_SEND)


async def correct_action_input(message: Message,
                               widget: ManagedTextInput,
                               dialog_manager: DialogManager,
                               text: str) -> None:
    await add_action_db(message.from_user.id, text)
    bot = message.bot

    await bot.send_message(message.from_user.id, f'Действие "<b>{text}</b>" сохранено', parse_mode='HTML')
    await bot.delete_message(message.from_user.id, message.message_id)
    await dialog_manager.switch_to(state=new_action.start, show_mode=ShowMode.DELETE_AND_SEND)


async def uncorrect_action_input(message: Message,
                                 widget: ManagedTextInput,
                                 dialog_manager: DialogManager,
                                 error: ValueError):
    if str(error) == 'emoji':
        await message.answer('Ожидаю название до 20 символов (только текст)')
    else:
        await message.answer('Ожидаю название до 20 символов')


async def no_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.answer(text='Поддерживается только текст')


async def clear_action_list(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    await update_info(fields={"action_list": None}, table="users", where={"user_id": callback.from_user.id})


async def timezone_select(callback: CallbackQuery, widget: Select,
                          dialog_manager: DialogManager, timezone: int):
    await callback.answer('Сохранено')
    await update_info(table='users',
                      where={'user_id': callback.from_user.id},
                      fields={'timezone': timezone})
    await dialog_manager.start(state=new_action.start, mode=StartMode.RESET_STACK)
