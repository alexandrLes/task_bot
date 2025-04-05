from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from .. import keyboards
from src.database import SessionLocal
from src.models import Task
from src.utils.validators import validate_deadline

router = Router()


@router.message(Command("create_task"))
async def cmd_create_task(message: Message, state: FSMContext):
    """Начало создания задания."""
    await message.answer(
        "📝 Введите название задания:",
        reply_markup=keyboards.cancel_keyboard()
    )
    await state.set_state("waiting_for_task_title")


@router.message(F.text, StateFilter("waiting_for_task_title"))
async def process_task_title(message: Message, state: FSMContext):
    """Обработка названия задания."""
    await state.update_data(title=message.text)
    await message.answer("📄 Теперь введите описание:")
    await state.set_state("waiting_for_task_description")


@router.message(F.text, StateFilter("waiting_for_task_description"))
async def process_task_description(message: Message, state: FSMContext):
    """Обработка описания задания."""
    await state.update_data(description=message.text)
    await message.answer("⏳ Введите срок выполнения (например, 2024-12-31 18:00):")
    await state.set_state("waiting_for_task_deadline")


@router.message(F.text, StateFilter("waiting_for_task_deadline"))
async def process_task_deadline(message: Message, state: FSMContext):
    """Валидация срока выполнения."""
    try:
        deadline = validate_deadline(message.text)  # Проверка формата даты
        await state.update_data(deadline=deadline)

        data = await state.get_data()
        db = SessionLocal()
        task = Task(
            author_id=message.from_user.id,
            title=data["title"],
            description=data["description"],
            deadline=deadline
        )
        db.add(task)
        db.commit()

        await message.answer("✅ Задание создано! Исполнители увидят его в /available_tasks.")
        await state.clear()

    except ValueError as e:
        await message.answer(f"❌ Ошибка: {e}\nПопробуйте снова.")