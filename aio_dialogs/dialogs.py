from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Next, Row, Button, SwitchTo, Cancel
from aiogram_dialog.widgets.text import Const

from aio_dialogs.states import state_user, state_admin

user_dialog = Dialog(
    Window(
        Const('<b>Стартовое окно пользователя</b>'),


        parse_mode='HTML',
        state=state_user.start,
    )
)

admin_dialog = Dialog(
    Window(
        Const('<b>Стартовое окно админа</b>'),


        parse_mode='HTML',
        state=state_admin.start
    )
)
