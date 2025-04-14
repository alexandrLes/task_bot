import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.handlers import common_router, authors_router, executors_router
from src.config import BOT_TOKEN
from src.middlewares import AuthMiddleware, RoleMiddleware


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(RoleMiddleware())

    # Подключаем обработчики
    dp.include_router(common_router)
    dp.include_router(authors_router)
    dp.include_router(executors_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())