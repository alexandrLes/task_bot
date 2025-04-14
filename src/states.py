from aiogram.fsm.state import StatesGroup, State

class AuthStates(StatesGroup):
    choosing_role = State()


class TaskStates(StatesGroup):
    waiting_for_task_title = State()
    waiting_for_task_description = State()
    waiting_for_task_deadline = State()
