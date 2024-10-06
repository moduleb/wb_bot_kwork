# crud.py
import logging
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Base

logger = logging.getLogger(__name__)


# ----- CREATE ------------------------------------------------------------------------
async def save_one(session: AsyncSession, obj: object) -> None:
    """Сохраняет объект в базу данных."""
    session.add(obj)
    await session.commit()


async def save_many(session: AsyncSession, objs: list[object]) -> None:
    """Сохраняет объекты в базу данных."""
    session.add_all(objs)
    await session.commit()


# ----- READ --------------------------------------------------------------------------

# Определяем тип переменной для модели
M = TypeVar("M", bound=Base)


async def get_one_by_filters(session: AsyncSession,
                            model: type[M],
                            **filters) -> M | None:

    # Начинаем строить запрос
    query = select(model)

    # Применяем фильтры
    for key, value in filters.items():
        if hasattr(model, key):
            query = query.where(getattr(model, key) == value)
        else:
            logger.debug("Invalid filter key: %s."
                         "No such attribute in model: %s", key, value)

    # Выполняем запрос
    result = await session.execute(query)
    return result.scalars().first()


# ----- DELETE ------------------------------------------------------------------------
async def delete(session: AsyncSession, obj: object) -> None:
    """Удаляет объект из базы данных."""
    await session.delete(obj)
    await session.commit()
