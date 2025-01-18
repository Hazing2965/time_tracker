from aiogram.fsm.state import StatesGroup, State



class state_admin(StatesGroup):
    start = State()

class new_action(StatesGroup):
    start = State()

class settings_state(StatesGroup):
    timezone = State()
