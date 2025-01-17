from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window, ShowMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Next, Row, Button, SwitchTo, Cancel, Select, Group
from aiogram_dialog.widgets.text import Const, Format, Multi

from aio_dialogs.aio_services import action_select, correct_action_input, uncorrect_action_input, no_text, \
    clear_action_list
from aio_dialogs.filters import action_check
from aio_dialogs.getters import new_action_getter, admin_getter
from aio_dialogs.states import state_admin, new_action

admin_dialog = Dialog(
    Window(
        Multi(Const('<b>Управление ботом</b>'),
              Format('{count_user}'),
              sep='\n\n'),
        SwitchTo(Const('Обновить'), id='refresh', state=state_admin.start),

        Cancel(Const('Выйти')),
        getter=admin_getter,
        parse_mode='HTML',
        state=state_admin.start
    )
)

new_action_dialog = Dialog(
    Window(
        Multi(Const('<b>Создание нового действия</b>'),
        Const('Выберите или напишите (Для остановки используйте <b>/stop</b>)', when=F['is_actions']),
        Const('Напишите действие (Для остановки используйте <b>/stop</b>)', when=~F['is_actions']),
        Format('Сейчас активно: "<b>{action_now}</b>"', when=F['action_now']),
              sep='\n\n'),
        Group(Select(
            Format('{item[0]}'),
            id='action',
            item_id_getter=lambda x: x[0],
            items='actions',
            on_click=action_select,
        ),
            width=3),
        TextInput(
            id='action_input',
            type_factory=action_check,
            on_success=correct_action_input,
            on_error=uncorrect_action_input,
        ),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY
        ),
        Button(Const('Очистить быстрый ввод'), id='clear_action_list', on_click=clear_action_list, when=F['is_actions']),
        getter=new_action_getter,
        parse_mode='HTML',
        state=new_action.start
    )
)
