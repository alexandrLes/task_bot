from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src import keyboards
from src.database import SessionLocal
from src.models import User

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработка /start с выбором роли."""
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == message.from_user.id).first()

    if not user:
        # Клавиатура для выбора роли (покажем в следующем шаге)
        await message.answer(
            "👋 Добро пожаловать! Выберите роль:",
            reply_markup=keyboards.role_keyboard()
        )
    else:
        await message.answer(
            f"🔄 Вы уже зарегистрированы как {user.role}. "
            "Используйте /profile для просмотра статистики."
        )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Показывает профиль пользователя."""
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == message.from_user.id).first()

    if not user:
        await message.answer("Сначала зарегистрируйтесь через /start.")
        return

    stats = {
        "rating": user.rating,
        "tasks_created": len(user.tasks_created),
        "tasks_completed": len([t for t in user.tasks_assigned if t.task.status == "completed"])
    }

    await message.answer(
        f"📊 Ваш профиль:\n"
        f"Роль: {user.role}\n"
        f"Рейтинг: {stats['rating']:.1f}/5\n"
        f"Создано заданий: {stats['tasks_created']}\n"
        f"Выполнено заданий: {stats['tasks_completed']}"
    )