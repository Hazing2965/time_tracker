from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from aio_dialogs.states import state_admin, new_action, settings_state
from config.config import ADMIN_ID, HELP_USER
from database.database import get_info
from lexicon.LEXICON import TEXT
from services.services import stop_record

router = Router()


@router.message(Command(commands=['start']))
async def process_start_command(message: Message):
    await message.answer(TEXT['/start'], parse_mode='HTML')


@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(f'Поддержка бота: {HELP_USER}')


@router.message(Command(commands=['new_action']))
async def process_new_action_command(message: Message, dialog_manager: DialogManager):
    info = await get_info(table='users', where={"user_id": message.from_user.id}, fields=["timezone"])
    info = info[0].get('timezone')
    if info:
        await dialog_manager.start(state=new_action.start, mode=StartMode.RESET_STACK)
    else:
        await message.answer(TEXT['note'], parse_mode='HTML')
        await dialog_manager.start(state=settings_state.timezone, mode=StartMode.RESET_STACK)


@router.message(Command(commands=['timezone']))
async def process_timezone_command(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=settings_state.timezone, mode=StartMode.RESET_STACK)


@router.message(Command(commands=['stop']))
async def process_stop_command(message: Message, dialog_manager: DialogManager):
    info = await get_info(table='users', where={"user_id": message.from_user.id}, fields=["action_id"])
    info = info[0].get('action_id')
    # Если она была
    if info is None:
        await message.answer('Записей не найдено. Начать: <b>/new_action</b>', parse_mode='HTML')
    else:
        try:
            await dialog_manager.done()
        except Exception:
            pass
        bot = message.bot
        await stop_record(bot, message.from_user.id)


@router.message(Command(commands=['admin']), F.from_user.id == ADMIN_ID)
async def process_admin_command(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=state_admin.start, mode=StartMode.RESET_STACK)


@router.message(Command(commands=['id']))
async def process_searth_id_command(message: Message):
    await message.answer(f'Ваш ID: <b>{message.from_user.id}</b>', parse_mode='HTML')
