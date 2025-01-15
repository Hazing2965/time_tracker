from aiogram_dialog import DialogManager

from database.database import get_list_from_db, get_action_now_db


async def new_action_getter(dialog_manager: DialogManager, **kwargs):
    action_list_bot = [('Работаю', 1), ('Рилсы', 2), ('Сплю', 3)]
    action_list_user = await get_list_from_db(dialog_manager.event.from_user.id)
    action_list_user = [(item, idx + 1) for idx, item in enumerate(reversed(action_list_user))]

    action_now = await get_action_now_db(dialog_manager.event.from_user.id)

    return {'actions': action_list_user, 'is_actions': bool(action_list_user), 'action_now': action_now, 'is_action_now': bool(action_now)}
