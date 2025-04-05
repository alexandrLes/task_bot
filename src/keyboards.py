from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .models import TaskStatus


# ----- Reply-клавиатуры (обычные кнопки под полем ввода) -----

def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для отмены действия (в FSM)."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# ----- Inline-клавиатуры (кнопки под сообщением) -----

def role_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора роли при /start."""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Автор", callback_data="role_author"),
        InlineKeyboardButton(text="Исполнитель", callback_data="role_executor")
    )
    return builder.as_markup()

def task_action_keyboard(task_id: str) -> InlineKeyboardMarkup:
    """Кнопки для задания (взять/подтвердить/отклонить)."""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="✅ Взять задание",
            callback_data=f"take_task_{task_id}"
        ),
        InlineKeyboardButton(
            text="📝 Подробнее",
            callback_data=f"task_details_{task_id}"
        )
    )
    return builder.as_markup()

def task_management_keyboard(task_id: str) -> InlineKeyboardMarkup:
    """Кнопки управления заданием для автора."""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="✔ Подтвердить выполнение",
            callback_data=f"confirm_task_{task_id}"
        ),
        InlineKeyboardButton(
            text="✖ Отклонить",
            callback_data=f"reject_task_{task_id}"
        )
    )
    return builder.as_markup()

def feedback_keyboard(task_id: str) -> InlineKeyboardMarkup:
    """Кнопки для оценки исполнителя (1-5 звёзд)."""
    builder = InlineKeyboardBuilder()
    for rating in range(1, 6):
        builder.add(
            InlineKeyboardButton(
                text=f"{rating} ⭐",
                callback_data=f"feedback_{task_id}_{rating}"
            )
        )
    builder.adjust(5)  # 5 кнопок в ряд
    return builder.as_markup()

def tasks_filter_keyboard() -> InlineKeyboardMarkup:
    """Фильтры для /my_tasks и /available_tasks."""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🔄 Все",
            callback_data="filter_all"
        ),
        InlineKeyboardButton(
            text="⏳ Ожидание",
            callback_data=f"filter_{TaskStatus.PENDING}"
        ),
        InlineKeyboardButton(
            text="🏗 В работе",
            callback_data=f"filter_{TaskStatus.IN_PROGRESS}"
        )
    )
    return builder.as_markup()