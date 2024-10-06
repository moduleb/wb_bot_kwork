"""Создание подключения к базе данных."""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

logger = logging.getLogger(__name__)


# Создание асинхронного движка
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Создание асинхронной сессии
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def check_database_connection() -> bool | None:
    """Проверка подключения к базе данных."""
    try:
        async with AsyncSessionLocal() as session:
        # async with engine.begin() as session:

            # получаем полную строку подключения
            logger.debug("Строка подключения к базе данных:\n\t%s", session.bind.url)

            result = await session.execute(text("select 1"))

            if result.scalar() == 1:
                logger.info("успешно подключено к базе данных")
                return True

    except OSError:
        return False


class DBError(Exception):
    """Исключение для ошибок базы данных."""

    @staticmethod
    def connection_error():  # noqa: ANN205
        return DBError("Ошибка подключения к базе данных.")

    @staticmethod
    def query_error():  # noqa: ANN205
        return DBError("Ошибка выполнения запроса к базе данных.")

    @staticmethod
    def not_found_error():  # noqa: ANN205
        return DBError("Запись не найдена в базе данных.")

    @staticmethod
    def not_null_constrain():  # noqa: ANN205
        return DBError("Заолнены не все поля в модели Item")




class DBDublicateError(DBError):
    """Исключение при дублировании записи в базу даннх."""

    @staticmethod
    def dublicate_error():  # noqa: ANN205
        return DBDublicateError("")
