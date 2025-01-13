from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from aio_dialogs.states import state_admin, new_action

router = Router()

@router.message(Command(commands=['start']))
async def process_start_command(message: Message):
    await message.answer('/new_action - Начать\n/stop - Закончить эксперимент')

@router.message(Command(commands=['new_action']))
async def process_new_action_command(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=new_action.start, mode=StartMode.RESET_STACK)


@router.message(Command(commands=['stop']))
async def process_stop_command(message: Message):
    await message.answer('Окончание эксперимента, получение результатов')

@router.message(Command(commands=['admin']))
async def process_admin_command(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=state_admin.start, mode=StartMode.RESET_STACK)

@router.message(Command(commands=['id']))
async def process_searth_id_command(message: Message):
    await message.answer(f'Ваш ID: <b>{message.from_user.id}</b>', parse_mode='HTML')