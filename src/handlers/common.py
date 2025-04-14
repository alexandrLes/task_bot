from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import update

from src import keyboards
from src.database import SessionLocal
from src.models import User, UserRole
from src.states import AuthStates

router = Router()

# Команда /start - начало авторизации
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == message.from_user.id).first()

    if user:
        role = "автор" if user.role.name == "AUTHOR" else "исполнитель"
        if not user.is_active:
            # Активируем пользователя при повторном входе
            db.execute(
                update(User)
                .where(User.user_id == message.from_user.id)
                .values(is_active=True)
            )
            db.commit()
            await message.answer(
                f"🔹 Добро пожаловать снова! Ваша роль: {role}."
            )
        else:
            await message.answer(
                f"🔹 Вы уже авторизованы как {role}. "
                f"Используйте /profile для просмотра данных."
            )
    else:
        await message.answer(
            "👋 Добро пожаловать! Выберите свою роль:",
            reply_markup=keyboards.role_keyboard()
        )
        await state.set_state(AuthStates.choosing_role)

# Обработка выбора роли
@router.callback_query(F.data.startswith("role_"), AuthStates.choosing_role)
async def set_user_role(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split("_")[1]
    db = SessionLocal()

    new_user = User(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        role=UserRole(role)
    )

    db.add(new_user)
    db.commit()

    await callback.message.edit_text(
        f"✅ Вы успешно зарегистрированы как {role}!\n\n"
        f"Теперь вам доступны команды для этой роли."
    )
    await state.clear()

# Команда /logout - сброс авторизации
@router.message(Command("logout"))
async def cmd_logout(message: Message):
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == message.from_user.id).first()

    if user and user.is_active:
        db.execute(
            update(User)
            .where(User.user_id == message.from_user.id)
            .values(is_active=False)
        )
        db.commit()
        await message.answer(
            "🚪 Вы вышли из системы. Для входа используйте /start\n"
            "Ваши данные сохранены."
        )
    elif user:
        await message.answer("ℹ Вы уже вышли из системы.")
    else:
        await message.answer("ℹ Вы не авторизованы.")

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Показывает профиль пользователя."""
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == message.from_user.id).first()

    if not user:
        await message.answer("Сначала зарегистрируйтесь через /start.")
        return

    stats = {
        "user_id": user.user_id,
        "username": user.username,
        "tasks_completed": len([t for t in user.tasks_assigned if t.task.status == "completed"]),
        "tasks_created": len([t for t in user.tasks_created])
    }

    await message.answer(
        f"📊 Ваш профиль:\n"
        f"ID: {stats.get('user_id')}\n"
        f"Username: {stats.get('username')}\n"
        f"Созданные задания: {stats.get('tasks_created')}\n"
        f"Выполнено заданий: {stats.get('tasks_completed')}"
    )