"""Точка входа.
Сознание бота и диспетчера.
Подключение роутеров.
Запуск бота.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.exceptions import AiogramError
from aiogram.fsm.storage.memory import MemoryStorage
from commands import user_commands
from db import check_database_connection
from handlers.any_msg_router import router as any_msg_router
from handlers.delete_router import router as delete_router
from handlers.list_router import router as list_router
from handlers.test_router import router as test_router
from handlers.main_router import router
from settings import settings
from utills.scheduler import loop_check_price

logger = logging.getLogger(__name__)

bot = Bot(token=settings.TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    """Запускает бота."""
    logger.info("Запуск бота...")

    if not await check_database_connection():
        logger.critical("База данных недоступна")
        sys.exit(1)

    try:
        # Запускаем процесс фонового отслеживания цен
        task = asyncio.create_task(loop_check_price(bot, settings.PRICE_UPDATE_TIMEOUT_IN_SEC))

        # Решистрируем роутер
        dp.include_router(test_router)
        dp.include_router(delete_router)
        dp.include_router(list_router)
        dp.include_router(router)
        dp.include_router(any_msg_router)

        # Устанавливаем команды
        await bot.set_my_commands(user_commands)

        await bot.delete_webhook(drop_pending_updates=True)
        """Dы указываете боту удалить текущий вебхук.
        drop_pending_updates=True указывает боту также удалить все ожидающие обновления,
        которые могли быть накоплены во время использования вебхука."""

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        """Запускает бота с использовнием метода Long Polling.
        allowed_updates=dp.resolve_used_upate_types() указывает,
        какие типы обновлений бот будет получать.
        Бот будет ограничивать типы обновлений, которые он получает, только теми,
        которые он может обработать,
        Это полезно для оптимизации работы бота и уменьшения нагрузки на сервер."""

    except AiogramError:
        logger.exception("Произошла ошибка при запуске бота")

    finally:
        # Останавливаем фоновое отслеживание цен
        task.cancel()

        # Закрываем сессию бота
        await bot.session.close()

        logger.info("Бот остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
