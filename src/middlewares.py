from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any, Coroutine

from src.database import SessionLocal
from src.models import User


class RoleMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable,
            event: Message,
            data: dict
    ) -> Awaitable:
        user_role = data.get("user_role")  # Получаем роль из БД
        required_role = handler.__annotations__.get("required_role")

        if required_role and user_role != required_role:
            await event.answer("🚫 У вас нет доступа к этой команде.")
            return
        return await handler(event, data)

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: Message,
        data: Dict[str, Any]
    ) -> Any | None:
        db = SessionLocal()
        user = db.query(User).filter(User.user_id == event.from_user.id).first()

        # Игнорируем проверку для команд /start и /logout
        if event.text in ['/start', '/logout']:
            return await handler(event, data)

        if not user:
            await event.answer("⚠ Сначала зарегистрируйтесь через /start")
            return

        data["user"] = user  # Добавляем пользователя в контекст
        return await handler(event, data)