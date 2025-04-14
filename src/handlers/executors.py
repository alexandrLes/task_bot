from select import select

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
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

@router.message(Command("my_tasks")):
async def cmd_my_tasks(message: Message):
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.status == TaskStatus.PENDING).all()




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


@router.callback_query(F.data.startswith("task_details_"))
async def task_details(callback: CallbackQuery):
    """Показывает детали задания."""
    task_id = callback.data.split("_")[-1]  # Извлекаем task_id из callback_data

    with SessionLocal() as db:
        # Получаем задание из БД
        task = db.query(Task).filter(Task.task_id == task_id).first()

        if not task:
            await callback.answer("Задание не найдено!", show_alert=True)
            return

        # Форматируем текст сообщения
        text = (
            f"📌 <b>Задание:</b> {task.title}\n"
            f"📝 <b>Описание:</b> {task.description}\n"
            f"⏳ <b>Срок:</b> {task.deadline.strftime('%d.%m.%Y %H:%M')}\n"
            f"💰 <b>Вознаграждение:</b> {task.reward or 'Не указано'}\n"
            f"🔄 <b>Статус:</b> {task.status.value}\n"
            f"👤 <b>Автор:</b> @{task.author.username if task.author.username else 'N/A'}"
        )

        # Если задание в работе, добавляем информацию об исполнителе
        if task.status == TaskStatus.IN_PROGRESS and task.assignments:
            executor = task.assignments[0].executor
            text += f"\n👷 <b>Исполнитель:</b> @{executor.username if executor.username else 'N/A'}"

        # Если задание завершено, добавляем результат
        if task.status == TaskStatus.COMPLETED and task.submissions:
            submission = task.submissions[0]
            text += f"\n✅ <b>Результат:</b> <a href='{submission.screenshot_url}'>Скриншот</a>"

        # Кнопки действий (зависит от роли пользователя)
        buttons = []
        user_id = callback.from_user.id

        # Если пользователь - автор задания
        if user_id == task.author_id:
            if task.status == TaskStatus.IN_PROGRESS:
                buttons.append(
                    InlineKeyboardButton(
                        text="✅ Подтвердить выполнение",
                        callback_data=f"confirm_task_{task_id}"
                    )
                )
                buttons.append(
                    InlineKeyboardButton(
                        text="❌ Отклонить",
                        callback_data=f"reject_task_{task_id}"
                    )
                )

        # Если пользователь - исполнитель
        elif any(asg.executor_id == user_id for asg in task.assignments):
            if task.status == TaskStatus.IN_PROGRESS:
                buttons.append(
                    InlineKeyboardButton(
                        text="📤 Отправить результат",
                        callback_data=f"submit_task_{task_id}"
                    )
                )

        # Кнопка "Назад" к списку заданий
        buttons.append(
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="my_tasks" if user_id == task.author_id else "available_tasks"
            )
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

        # Редактируем сообщение, чтобы показать детали
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()