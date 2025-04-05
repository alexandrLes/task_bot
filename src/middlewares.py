from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable


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