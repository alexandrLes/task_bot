from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src import keyboards
from src.database import SessionLocal
from src.models import Task, TaskStatus

router = Router()


@router.message(Command("available_tasks"))
async def cmd_available_tasks(message: Message):
    """Список доступных заданий."""
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.status == TaskStatus.PENDING).all()

    if not tasks:
        await message.answer("🔄 Нет доступных заданий.")
        return

    for task in tasks:
        await message.answer(
            f"📌 Задание #{task.task_id}\n"
            f"Название: {task.title}\n"
            f"Срок: {task.deadline}\n"
            f"Описание: {task.description[:100]}...",
            reply_markup=keyboards.task_action_keyboard(task.task_id)
        )


@router.callback_query(F.data.startswith("take_task_"))
async def take_task(callback: CallbackQuery):
    """Исполнитель берет задание."""
    task_id = callback.data.split("_")[-1]
    db = SessionLocal()
    task = db.query(Task).filter(Task.task_id == task_id).first()

    if task.status != TaskStatus.PENDING:
        await callback.answer("❌ Задание уже взято другим исполнителем.")
        return

    task.status = TaskStatus.IN_PROGRESS
    task.executor_id = callback.from_user.id
    db.commit()

    await callback.message.edit_text(
        f"✅ Вы взяли задание «{task.title}». "
        f"Срок выполнения: {task.deadline}."
    )